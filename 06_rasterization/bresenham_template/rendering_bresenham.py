"""
/*******************************************************************************
 *
 *            #, #,         CCCCCC  VV    VV MM      MM RRRRRRR
 *           %  %(  #%%#   CC    CC VV    VV MMM    MMM RR    RR
 *           %    %## #    CC        V    V  MM M  M MM RR    RR
 *            ,%      %    CC        VV  VV  MM  MM  MM RRRRRR
 *            (%      %,   CC    CC   VVVV   MM      MM RR   RR
 *              #%    %*    CCCCCC     VV    MM      MM RR    RR
 *             .%    %/
 *                (%.      Computer Vision & Mixed Reality Group
 *
 ******************************************************************************/
/**          @copyright:   Hochschule RheinMain,
 *                         University of Applied Sciences
 *              @author:   Prof. Dr. Ulrich Schwanecke, Fabian Stahl
 *             @version:   2.0
 *                @date:   01.04.2023
 ******************************************************************************/
/**         rendering_bresenham.py
 *
 *          This module is used to create a ModernGL context using GLFW.
 *          It provides the functionality necessary to execute and visualize code
 *          specified by students in the according template.
 *          ModernGL is a high-level modern OpenGL wrapper package.
 ****
"""

import copy
import glfw
import imgui
import numpy as np
import moderngl as mgl
import os

from imgui.integrations.glfw import GlfwRenderer


class Scene:
    """
        OpenGL 2D scene class
    """
    # initialization
    def __init__(self,
                width,
                height,
                bresenham_line_callback,
                scene_title         = "2D Scene"):

        self.width                  = width
        self.height                 = height
        self.bresenham_line_callback = bresenham_line_callback
        self.scene_title            = scene_title
        self.points                 = []
        self.bresenham_points       = []
        self.show_bresenham_lines   = True
        self.gridsize               = 25

        # Rendering
        self.ctx                = None              # Assigned when calling init_gl()
        self.bg_color           = (0.1, 0.1, 0.1)
        self.point_size         = 7
        self.point_color        = (1.0, 1.0, 1.0)
        self.line_color         = (0.3, 0.3, 0.3)


    def init_gl(self, ctx):
        self.ctx        = ctx

        # Create Shaders
        self.shader = ctx.program(
            vertex_shader = """
                #version 330

                uniform mat4    m_proj;
                uniform int     m_point_size;
                uniform vec3    color;

                in vec2 v_pos;

                out vec3 f_col;

                void main() {
                    gl_Position     = m_proj * vec4(v_pos, 0.0, 1.0);
                    gl_PointSize    = m_point_size;
                    f_col           = color;
                }
            """,
            fragment_shader = """
                #version 330

                in vec3 f_col;

                out vec4 color;

                void main() {
                    color = vec4(f_col, 1.0);
                }
            """
        )
        self.shader['m_point_size'] = self.point_size

        # Set projection matrix
        l, r = 0, self.width
        b, t = self.height, 0
        n, f = -2, 2
        m_proj = np.array([
            [2/(r-l),   0,          0,          -(l+r)/(r-l)],
            [0,         2/(t-b),    0,          -(b+t)/(t-b)],
            [0,         0,          -2/(f-n),    -(n+f)/(f-n)],
            [0,         0,          0,          1]
        ], dtype=np.float32)
        m_proj = np.ascontiguousarray(m_proj.T)
        self.shader['m_proj'].write(m_proj)


    # add a point
    def add_point(self, p):
        point = [int(p[0]//self.gridsize)*self.gridsize,
                 int(p[1]//self.gridsize)*self.gridsize]
        self.points.append(point)
        if len(self.points)>1 and len(self.points) % 2 == 0:
            for i in range(0, len(self.points), 2):
                pixels_hit = self.bresenham_line_callback(self.points[i], self.points[i+1], self.gridsize)
                self.bresenham_points.extend(pixels_hit)

    # clear polygon
    def clear(self):
        self.points = []
        self.bresenham_points = []


    def sign(self, value):
        if value<0:
            return -1
        return 1


    def resize(self, width, height):
        self.width  = width
        self.height = height

        # Set projection matrix
        l, r = 0, self.width
        b, t = self.height, 0
        n, f = -1000, 1000
        m_proj = np.array([
            [2/(r-l),   0,          0,          -(l+r)/(r-l)],
            [0,         2/(t-b),    0,          -(b+t)/(t-b)],
            [0,         0,          -2/(f-n),    -(n+f)/(f-n)],
            [0,         0,          0,          1]
        ], dtype=np.float32)
        m_proj = np.ascontiguousarray(m_proj.T)
        self.shader['m_proj'].write(m_proj)


    def render(self):

        # Fill Background
        self.ctx.clear(*self.bg_color)

        # Render Grid
        self.shader['color'] = self.line_color
        lines_v = np.arange(self.gridsize, self.width, self.gridsize)
        lines_h = np.arange(self.gridsize, self.height, self.gridsize)
        vertex_data_v   = np.array([[x, 0, x, self.height] for x in lines_v])
        vertex_data_h   = np.array([[0, y, self.width, y] for y in lines_h])
        vbo_polygon     = self.ctx.buffer(np.concatenate([vertex_data_v, vertex_data_h], axis=0, dtype=np.float32))
        vao_polygon     = self.ctx.vertex_array(self.shader, [(vbo_polygon, '2f', 'v_pos')])
        vao_polygon.render(mgl.LINES)


        # Colorize pixels
        if self.show_bresenham_lines and len(self.bresenham_points) > 0:
            gs = self.gridsize
            # TL, TR, BR / TL, BR, BL
            t1 = np.array([(p[0], p[1], p[0] + gs, p[1], p[0] + gs, p[1] + gs) for p in self.bresenham_points])
            t2 = np.array([(p[0], p[1], p[0] + gs, p[1] + gs, p[0], p[1] + gs) for p in self.bresenham_points])
            vbo_polygon = self.ctx.buffer(np.concatenate([t1, t2], axis=0, dtype=np.float32))
            vao_polygon = self.ctx.vertex_array(self.shader, [(vbo_polygon, '2f', 'v_pos')])
            vao_polygon.render(mgl.TRIANGLES)


        # Render Points and Lines
        if len(self.points) > 0:
            self.shader['color'] = self.point_color
            vbo_polygon = self.ctx.buffer(np.array(self.points, np.float32) + self.gridsize/2)
            vao_polygon = self.ctx.vertex_array(self.shader, [(vbo_polygon, '2f', 'v_pos')])
            vao_polygon.render(mgl.LINES)
            vao_polygon.render(mgl.POINTS)



class RenderWindow:
    """
        GLFW Rendering window class
        YOU SHOULD NOT EDIT THIS CLASS!
    """
    def __init__(self, scene):

        self.scene = scene

        # save current working directory
        cwd = os.getcwd()

        # Initialize the library
        if not glfw.init():
            return

        # restore cwd
        os.chdir(cwd)

        # buffer hints
        glfw.window_hint(glfw.DEPTH_BITS, 32)

        # define desired frame rate
        self.frame_rate = 60

        # OS X supports only forward-compatible core profiles from 3.2
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
        glfw.window_hint(glfw.COCOA_RETINA_FRAMEBUFFER, False)

        # make a window
        self.width, self.height = scene.width, scene.height
        self.window = glfw.create_window(self.width, self.height, scene.scene_title, None, None)
        if not self.window:
            self.impl.shutdown()
            glfw.terminate()
            return

        # Make the window's context current
        glfw.make_context_current(self.window)

        # initializing imgui
        imgui.create_context()
        self.impl = GlfwRenderer(self.window)

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.onMouseButton)
        glfw.set_key_callback(self.window, self.onKeyboard)
        glfw.set_window_size_callback(self.window, self.onSize)

        # create modernGL context and initialize GL objects in scene
        self.ctx = mgl.create_context()
        self.ctx.enable(flags=mgl.PROGRAM_POINT_SIZE)
        self.scene.init_gl(self.ctx)
        mgl.DEPTH_TEST = True

        # exit flag
        self.exitNow = False


    def onMouseButton(self, win, button, action, mods):
        #print("mouse button: ", win, button, action, mods)
        if not imgui.get_io().want_capture_mouse:
            if action == glfw.PRESS:
                p = glfw.get_cursor_pos(win)
                self.scene.add_point(p)


    def onKeyboard(self, win, key, scancode, action, mods):
        #print("keyboard: ", win, key, scancode, action, mods)
        if action == glfw.PRESS:
            # ESC to quit
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True
            # toggle display of clipped lines
            if key == glfw.KEY_S:
                self.scene.show_bresenham_lines = not self.scene.show_bresenham_lines
            # clear everything
            if key == glfw.KEY_C:
                self.scene.clear()


    def onSize(self, win, width, height):
        #print("onsize: ", win, width, height)
        self.width          = width
        self.height         = height
        self.ctx.viewport   = (0, 0, self.width, self.height)
        self.scene.resize(width, height)


    def run(self):
        # initializer timer
        glfw.set_time(0.0)
        t = 0.0
        while not glfw.window_should_close(self.window) and not self.exitNow:
            # update every x seconds
            currT = glfw.get_time()
            if currT - t > 1.0 / self.frame_rate:
                # update time
                t = currT

                # == Frame-wise IMGUI Setup ===
                imgui.new_frame()                   # Start new frame context
                imgui.begin("Controller")     # Start new window context

                # Define UI Elements
                if imgui.button("Clear Scene (c)"):
                    self.scene.clear()
                if imgui.button("Toggle Lines (s)"):
                    self.scene.show_bresenham_lines = not self.scene.show_bresenham_lines


                imgui.end()                         # End window context
                imgui.render()                      # Run render callback
                imgui.end_frame()                   # End frame context
                self.impl.process_inputs()          # Poll for UI events

                # == Rendering GL ===
                glfw.poll_events()                  # Poll for GLFW events
                self.ctx.clear()                    # clear viewport
                self.scene.render()                 # render scene
                self.impl.render(imgui.get_draw_data()) # render UI
                glfw.swap_buffers(self.window)      # swap front and back buffer


        # end
        self.impl.shutdown()
        glfw.terminate()
