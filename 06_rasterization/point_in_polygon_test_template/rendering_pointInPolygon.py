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
/**         rendering_pointInPolygon.py
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
                test_line_intersect,
                scene_title         = "2D Scene"):

        self.width                  = width
        self.height                 = height
        self.test_line_intersect    = test_line_intersect
        self.scene_title            = scene_title
        self.polygon                = []
        self.test_points            = []
        self.test                   = False

        # Rendering
        self.ctx                = None              # Assigned when calling init_gl()
        self.bg_color           = (0.1, 0.1, 0.1)
        self.point_size         = 10
        self.point_color_outer  = (0.3, 0.3, 0.3)
        self.point_color_within = (1.0, 1.0, 1.0)
        self.line_color         = (0.5, 0.5, 1.0)


    def init_gl(self, ctx):
        self.ctx        = ctx

        # Create Shaders
        self.shader = ctx.program(
            vertex_shader = """
                #version 330

                uniform mat4    m_proj;
                uniform int     m_point_size;

                in vec2 v_pos;
                in vec3 v_col;

                out vec3 f_col;

                void main() {
                    gl_Position     = m_proj * vec4(v_pos, 0.0, 1.0);
                    gl_PointSize    = m_point_size;
                    f_col           = v_col;
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
        l, r = 0, 1
        b, t = 0, 1
        n, f = -2, 2
        m_proj = np.array([
            [2/(r-l),   0,          0,          -(l+r)/(r-l)],
            [0,         2/(t-b),    0,          -(b+t)/(t-b)],
            [0,         0,          -2/(f-n),    -(n+f)/(f-n)],
            [0,         0,          0,          1]
        ], dtype=np.float32)
        m_proj = np.ascontiguousarray(m_proj.T)
        self.shader['m_proj'].write(m_proj)


    def add_point_to_polygon(self, point):
        self.polygon.append(point)


    # clear polygon
    def clear(self):
        self.polygon        = []
        self.test_points    = []
        self.test           = False


    def add_test_point(self, p):
        self.test_points.append(p)


    def pointInPolygon(self, p):
        """ test wether point p is in polygon or not"""
        pList = copy.deepcopy(self.polygon)
        pList.append(self.polygon[0])
        count = 0
        testLine = [p, [self.width, p[1]]]
        for line in zip(pList, pList[1:]):
            if self.test_line_intersect(line, testLine):
                count = count +1
        return (count % 2) == 1


    def render(self):

        # Fill Background
        self.ctx.clear(*self.bg_color)

        # Render Polygon Lines and Points
        if len(self.polygon) > 0:
            colors = np.ones((len(self.polygon), 3)) * self.line_color
            vertex_data = np.concatenate([self.polygon, colors], axis=1)
            vbo_polygon = self.ctx.buffer(np.array(vertex_data, np.float32))
            vao_polygon = self.ctx.vertex_array(self.shader, [(vbo_polygon, '2f 3f', 'v_pos', 'v_col')])
            vao_polygon.render(mgl.LINE_LOOP)
            vao_polygon.render(mgl.POINTS)

        # Render Test Points
        if len(self.test_points) > 0:

            # Intersection Test
            colors = []
            for p in self.test_points:
                if self.pointInPolygon(p):
                    colors.append(self.point_color_within)
                else:
                    colors.append(self.point_color_outer)
            vertex_data = np.concatenate([self.test_points, colors], axis=1)
            vbo_points = self.ctx.buffer(np.array(vertex_data, np.float32))
            vao_points = self.ctx.vertex_array(self.shader, [(vbo_points, '2f 3f', 'v_pos', 'v_col')])
            vao_points.render(mgl.POINTS)




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

                # Relative coordinates in [0, 1]
                x, y = x / self.width, y / self.height

                # Reverse y-Axis
                y = 1 - y

                p = [x, y]
                if not self.scene.test:
                    self.scene.add_point_to_polygon(p)
                else:
                    self.scene.add_test_point(p)


    def onKeyboard(self, win, key, scancode, action, mods):
        #print("keyboard: ", win, key, scancode, action, mods)
        if action == glfw.PRESS:
            # ESC to quit
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True
            if key == glfw.KEY_C:
                # Clear everything
                self.scene.clear()
            if key == glfw.KEY_T:
                # Set test
                self.scene.test = True
            if key == glfw.KEY_P:
                # Set test
                self.scene.test = False


    def onSize(self, win, width, height):
        #print("onsize: ", win, width, height)
        self.width          = width
        self.height         = height
        self.ctx.viewport   = (0, 0, self.width, self.height)


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
                if imgui.button("Draw Polygon (p)"):
                    self.scene.test = False
                if imgui.button("Draw Test Points (t)"):
                    self.scene.test = True

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
