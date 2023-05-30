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
/**         rendering_lineClipping.py
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


class Point:
    """ Point class
        co : 2d point coordinates
        cr : clipping region
    """
    def __init__(self, co, cr):
	    self.coords = co
	    # region code
	    self.reCode = 8 * (co[1] < cr[1][1])+ \
            4 * (co[1] > cr[0][1]) + \
            2 * (co[0] > cr[1][0]) + \
            1 * (co[0] < cr[0][0])


class Scene:
    """
        OpenGL 2D scene class
    """
    # initialization
    def __init__(self,
                width,
                height,
                line_code_callback,
                clip_line_callback,
                scene_title         = "2D Scene"):

        self.width                  = width
        self.height                 = height
        self.line_code_callback     = line_code_callback
        self.clip_line_callback     = clip_line_callback
        self.scene_title            = scene_title
        self.points                 = []
        self.lines                  = []
        self.clipped_lines          = []
        self.show_clipped_lines     = True

        # Rendering
        self.ctx                = None              # Assigned when calling init_gl()
        self.bg_color           = (0.1, 0.1, 0.1)
        self.point_size         = 7
        self.point_color        = (1, 1, 1)
        self.line_color_within  = (0.75, 1.0, 0.75)
        self.line_color_outer   = (1.0, 0.35, 0.35)
        self.frame_color        = (0.5, 0.5, 1.0)

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
        self.shader['color'] = self.point_color


    # set polygon
    def add_point(self, point):
        self.points.append(point)

        # store a new line for every 2nd point
        if len(self.points) > 2 and len(self.points) % 2 == 0:
            self.lines.append([self.points[-2], self.points[-1]])
            self.append_clipped_line([self.points[-2], self.points[-1]])


    # clip line
    def append_clipped_line(self, l):
        # get clippling region as oriented BBOX
        frame = self.points[:2]
        x_min = min(frame[0][0], frame[1][0])
        y_min = min(frame[0][1], frame[1][1])
        x_max = max(frame[0][0], frame[1][0])
        y_max = max(frame[0][1], frame[1][1])
        cr    = [(x_min, y_max), (x_max, y_min)]

        # set region codes for line points
        p, q = Point(l[0], cr), Point(l[1], cr)
        # set line code
        lc = self.line_code_callback(p.coords, p.reCode, q.coords, q.reCode)
        # do nothing if line is completely outside clippling region
        if lc != -1:
            # calc new line segment ...
            l = self.clip_line_callback(p.coords, q.coords, lc, x_min, y_min, x_max, y_max)
            # ... add to list of clipped lines if clipped segment is not empty
            if l:
                self.clipped_lines.append(l)


    # clear polygon
    def clear(self):
        self.points = []
        self.lines = []
        self.clipped_lines = []


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

        point_data = np.array(self.points, np.float32)

        # Render next points
        if len(self.points) > 2:
            self.shader['color'] = self.point_color
            vbo_polygon = self.ctx.buffer(point_data[2:])
            vao_polygon = self.ctx.vertex_array(self.shader, [(vbo_polygon, '2f', 'v_pos')])
            vao_polygon.render(mgl.POINTS)

        # Render next points as raw lines
        if len(self.points) > 3:
            self.shader['color'] = self.line_color_outer
            end_index = len(point_data) if len(point_data) % 2 == 0 else len(point_data) - 1
            vbo_polygon = self.ctx.buffer(point_data[2:end_index])
            vao_polygon = self.ctx.vertex_array(self.shader, [(vbo_polygon, '2f', 'v_pos')])
            vao_polygon.render(mgl.LINES)

        # Render Clipped Lines
        if self.show_clipped_lines and len(self.clipped_lines) > 0:
            self.shader['color'] = self.line_color_within
            clip_data = np.concatenate(self.clipped_lines, 0, dtype=np.float32)
            vbo_polygon = self.ctx.buffer(clip_data)
            vao_polygon = self.ctx.vertex_array(self.shader, [(vbo_polygon, '2f', 'v_pos')])
            vao_polygon.render(mgl.LINES)

        # Render first 2 points as clipping region
        if len(self.points) >= 2:
            self.shader['color'] = self.frame_color
            p, q = np.array(point_data[:2], np.float32)
            bbox = np.array([p, [q[0], p[1]], q, [p[0], q[1]]], dtype=np.float32)
            vbo_polygon = self.ctx.buffer(bbox)
            vao_polygon = self.ctx.vertex_array(self.shader, [(vbo_polygon, '2f', 'v_pos')])
            vao_polygon.render(mgl.LINE_LOOP)

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
                x, y = glfw.get_cursor_pos(win)
                p = [int(x), int(y)]
                self.scene.add_point(p)


    def onKeyboard(self, win, key, scancode, action, mods):
        #print("keyboard: ", win, key, scancode, action, mods)
        if action == glfw.PRESS:
            # ESC to quit
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True
            # toggle display of clipped lines
            if key == glfw.KEY_S:
                self.scene.show_clipped_lines = not self.scene.show_clipped_lines
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
                if imgui.button("Toggle Clip Lines (s)"):
                    self.scene.show_clipped_lines = not self.scene.show_clipped_lines

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
