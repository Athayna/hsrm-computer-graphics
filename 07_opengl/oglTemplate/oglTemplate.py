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
 *              @author:   Prof. Dr. Ulrich Schwanecke
 *             @version:   0.91
 *                @date:   07.06.2022
 ******************************************************************************/
/**         oglTemplate.py
 *
 *          Simple Python OpenGL program that uses PyOpenGL + GLFW to get an
 *          OpenGL 3.2 core profile context and animate a colored triangle.
 ****
"""

import glfw
import numpy as np

from OpenGL.GL import *
from OpenGL.arrays.vbo import VBO
from OpenGL.GL.shaders import *

from mat4 import *

import sys

EXIT_FAILURE = -1

class Scene:
    """
        OpenGL scene class that renders obj files as wireframe, with goroud or phong shading.
    """

    def __init__(self, width, height, scenetitle=f"OpenGL obj-Viewer: {sys.argv[1]}"):
        self.scenetitle         = scenetitle
        self.width              = width
        self.height             = height
        self.angle_increment    = 1
        self.animate            = False

        # self added variables
        self.angleY             = 0
        self.angleX             = 0
        self.angleZ             = 0
        self.persective         = True
        self.shading            = 0
        self.center             = np.array([0.0, 0.0, 0.0])
        self.max_len            = 0.0
        self.size               = 1.0
        self.zoom               = False
        self.zoom_start         = 0.0
        self.move               = False
        self.move_start         = np.array([0.0, 0.0])
        self.light_position     = [1.0, 1.0, 2.0]
        self.arc                = False
        self.arc_start          = [0.0, 0.0, 0.0]
        self.arc_angle          = 0.0
        self.arc_axis           = [0.0, 0.0, 0.0]

    def init_GL(self, vert = "shader.vert", frag = "shader.frag"):
        # setup buffer (vertices, colors, normals, ...)
        self.gen_buffers()

        # setup shader
        glBindVertexArray(self.vertex_array)
        vertex_shader       = open(vert,"r").read()
        fragment_shader     = open(frag,"r").read()
        vertex_prog         = compileShader(vertex_shader, GL_VERTEX_SHADER)
        frag_prog           = compileShader(fragment_shader, GL_FRAGMENT_SHADER)
        self.shader_program = compileProgram(vertex_prog, frag_prog)

        if glGetShaderiv(vertex_prog, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(vertex_prog))
        if glGetShaderiv(frag_prog, GL_COMPILE_STATUS) != GL_TRUE:
            raise RuntimeError(glGetShaderInfoLog(frag_prog))

        if glGetProgramiv(self.shader_program, GL_LINK_STATUS) != GL_TRUE:
            raise RuntimeError(glGetProgramInfoLog(self.shader_program))

        # unbind vertex array to bind it again in method draw
        glBindVertexArray(0)
 
    def gen_buffers(self):
        # TODO:
        # 1. Load geometry from file and calc normals if not available
        # 2. Load geometry and normals in buffer objects
        
        positions, normals, indices = self.load_geometry(sys.argv[1])
        self.center, self.max_len = self.center_object(positions) 

        # generate vertex array object
        self.vertex_array = glGenVertexArrays(1)
        glBindVertexArray(self.vertex_array)

        # generate and fill buffer with vertex positions (attribute 0)
        positions = np.array(positions, dtype=np.float32)
        pos_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, pos_buffer)
        glBufferData(GL_ARRAY_BUFFER, positions.nbytes, positions, GL_STATIC_DRAW)
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)
 
        # generate and fill buffer with vertex normals (attribute 1)
        normals = np.array(normals, dtype=np.float32)
        norm_buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, norm_buffer)
        glBufferData(GL_ARRAY_BUFFER, normals.nbytes, normals, GL_STATIC_DRAW)
        glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(1)

        # generate index buffer  
        self.indices = np.array(indices, dtype=np.int32)
        ind_buffer_object = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ind_buffer_object)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.indices.nbytes, self.indices, GL_STATIC_DRAW)
        
        # unbind buffers to bind again in draw()
        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def load_geometry(self, filename):
        with open(f"../models/{filename}", "r") as file:
            lines = file.readlines()
            positions = []
            normals = []
            indices = []
            tempNormals = [0] * sum(1 for line in lines if line.startswith("v ")) # create temp list with length of normals to sort in
            for line in lines:
                if line.startswith("vn"): # add normals
                    normal = line[2:].split()
                    normals.append(list(map(float, normal))) # convert strings to floats and add to list
                elif line.startswith("v"): # add vertices
                    position = line[1:].split()
                    positions.append(list(map(float, position))) # convert strings to floats and add to list
                elif line.startswith("f"): # add faces
                    if "//" in line: # if normals are given by faces
                        index = line[1:].replace("/", " ").split()
                        for i in range(0, 6, 2):
                            indices.append(int(index[i]) - 1) # add vertex indices
                            tempNormals[int(index[i]) - 1] = normals[int(index[i+1]) - 1] # add normal to corresponding vertex index
                    else: # if normals are not given by faces
                        index = line[1:].split()
                        for i in range(3):
                            indices.append(int(index[i]) - 1)           
        return positions, tempNormals if len(normals) > 0 else self.calculate_normals(positions, indices), indices

    def calculate_normals(self, positions, indices):
        normals = np.zeros_like(positions) # create list with length of positions to sort in
        for i in range(0, len(indices), 3):
            v1 = np.array(positions[indices[i+1]]) - np.array(positions[indices[i]]) # v1 - v0
            v2 = np.array(positions[indices[i+2]]) - np.array(positions[indices[i]]) # v2 - v0
            normal = np.cross(v1, v2) # cross product of v1 and v2
            normal = normal / np.linalg.norm(normal) # normalize normal
            normals[indices[i]] += normal # add normal to corresponding vertex index
            normals[indices[i+1]] += normal # add normal to corresponding vertex index
            normals[indices[i+2]] += normal # add normal to corresponding vertex index
        return normals
    
    def center_object(self, positions):
        center = np.mean(positions, axis=0) # calculate center of object
        max_len = np.max(np.linalg.norm(positions, axis=1)) # calculate max length of object
        return center, max_len

    def set_size(self, width, height):
        self.width = width
        self.height = height

    def set_shading(self):
        if self.shading == 0:
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
            self.init_GL("shader.vert", "shader.frag")
        elif self.shading == 1:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            self.init_GL("shader_gouraud.vert", "shader_gouraud.frag")
        elif self.shading == 2:
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
            self.init_GL("shader_phong.vert", "shader_phong.frag")

    def arcball_rotation(self):
        rotation_matrix = np.array([
            [np.cos(self.arc_angle) + self.arc_axis[0]**2 * (1 - np.cos(self.arc_angle)), self.arc_axis[0] * self.arc_axis[1] * (1 - np.cos(self.arc_angle)) - self.arc_axis[2] * np.sin(self.arc_angle), self.arc_axis[0] * self.arc_axis[2] * (1 - np.cos(self.arc_angle)) + self.arc_axis[1] * np.sin(self.arc_angle), 0],
            [self.arc_axis[1] * self.arc_axis[0] * (1 - np.cos(self.arc_angle)) + self.arc_axis[2] * np.sin(self.arc_angle), np.cos(self.arc_angle) + self.arc_axis[1]**2 * (1 - np.cos(self.arc_angle)), self.arc_axis[1] * self.arc_axis[2] * (1 - np.cos(self.arc_angle)) - self.arc_axis[0] * np.sin(self.arc_angle), 0],
            [self.arc_axis[2] * self.arc_axis[0] * (1 - np.cos(self.arc_angle)) - self.arc_axis[1] * np.sin(self.arc_angle), self.arc_axis[2] * self.arc_axis[1] * (1 - np.cos(self.arc_angle)) + self.arc_axis[0] * np.sin(self.arc_angle), np.cos(self.arc_angle) + self.arc_axis[2]**2 * (1 - np.cos(self.arc_angle)), 0],
            [0, 0, 0, 1]
        ])
        rotation = np.eye(4)
        rotation[:3, :3] = rotation_matrix[:3, :3]
        return rotation

    def draw(self):
        # TODO:
        # 1. Render geometry 
        #    (a) just as a wireframe model and 
        #    with 
        #    (b) a shader that realize Gouraud Shading
        #    (c) a shader that realize Phong Shading
        # 2. Rotate object around the x, y, z axis using the keys x, y, z
        # 3. Rotate object with the mouse by realizing the arcball metaphor as 
        #    well as scaling an translation
        # 4. Realize Shadow Mapping
        # 
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT) # type: ignore
        
        if self.animate:
            # increment rotation angle in each frame
            self.angleY += self.angle_increment
        
        # setup matrices
        if self.persective:
            projection = perspective(45.0, self.width/self.height, 1.0, 5.0)
        else:
            projection = ortho((self.width / self.height) * -1, (self.width / self.height) * 1, -1, 1, 0, 10)
        view       = look_at(0,0,2, 0,0,0, 0,1,0)
        rotation   = rotate_y(self.angleY) @ rotate_x(self.angleX) @ rotate_z(self.angleZ)
        translation= translate(-self.center[0], -self.center[1], -self.center[2])
        scaling    = scale((1/self.max_len) * self.size, (1/self.max_len) * self.size, (1/self.max_len) * self.size)
        model      = rotation @ scaling @ translation
        mvp_matrix = projection @ view @ model @ self.arcball_rotation()

        # enable shader & set uniforms
        glUseProgram(self.shader_program)
        
        # determine location of uniform variable varName
        varLocation = glGetUniformLocation(self.shader_program, 'modelview_projection_matrix')
        # pass value to shader
        glUniformMatrix4fv(varLocation, 1, GL_TRUE, mvp_matrix)

        # set location of light
        light_location = glGetUniformLocation(self.shader_program, 'light_position')
        # pass value to shader
        glUniform3fv(light_location, GL_TRUE, self.light_position)

        # enable vertex array & draw triangle(s)
        glBindVertexArray(self.vertex_array)
        glDrawElements(GL_TRIANGLES, self.indices.nbytes//4, GL_UNSIGNED_INT, None)

        # unbind the shader and vertex array state
        glUseProgram(0)
        glBindVertexArray(0)

class RenderWindow:
    """
        GLFW Rendering window class
    """

    def __init__(self, scene):
        # initialize GLFW
        if not glfw.init():
            sys.exit(EXIT_FAILURE)

        # request window with old OpenGL 3.2
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, glfw.TRUE)
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)

        # make a window
        self.width, self.height = scene.width, scene.height
        self.aspect = self.width / self.height
        self.window = glfw.create_window(self.width, self.height, scene.scenetitle, None, None)
        if not self.window:
            glfw.terminate()
            sys.exit(EXIT_FAILURE)

        # Make the window's context current
        glfw.make_context_current(self.window)

        # initialize GL
        self.init_GL()

        # set window callbacks
        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        glfw.set_key_callback(self.window, self.on_keyboard)
        glfw.set_window_size_callback(self.window, self.on_size)
        glfw.set_cursor_pos_callback(self.window, self.on_mouse_move)

        # create scene
        self.scene = scene  
        if not self.scene:
            glfw.terminate()
            sys.exit(EXIT_FAILURE)

        self.scene.set_shading()
        self.scene.init_GL()

        # exit flag
        self.exitNow = False

    def init_GL(self):
        # debug: print GL and GLS version
        # print('Vendor       : %s' % glGetString(GL_VENDOR))
        # print('OpenGL Vers. : %s' % glGetString(GL_VERSION))
        # print('GLSL Vers.   : %s' % glGetString(GL_SHADING_LANGUAGE_VERSION))
        # print('Renderer     : %s' % glGetString(GL_RENDERER))

        # set background color to black
        glClearColor(0, 0, 0, 0)     

        # Enable depthtest
        glEnable(GL_DEPTH_TEST)

    def on_mouse_button(self, win, button, action, mods):
        print("mouse button: ", win, button, action, mods)
        # TODO: realize arcball metaphor for rotations as well as
        #       scaling and translation paralell to the image plane,
        #       with the mouse.
        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                self.scene.arc_start = self.project_on_sphere(glfw.get_cursor_pos(win)[0], glfw.get_cursor_pos(win)[1], (min(width, height) / 2)) # get p1 on arcball
                self.scene.arc = True
            elif action == glfw.RELEASE:
                self.scene.arc = False
        if button == glfw.MOUSE_BUTTON_RIGHT:
            if action == glfw.PRESS:
                self.scene.move_start = np.array(glfw.get_cursor_pos(win)) # get start position
                self.scene.move = True
            elif action == glfw.RELEASE:
                self.scene.move = False
        if button == glfw.MOUSE_BUTTON_MIDDLE:
            if action == glfw.PRESS:
                self.scene.zoom_start = glfw.get_cursor_pos(win)[1] # get start position
                self.scene.zoom = True
            elif action == glfw.RELEASE:
                self.scene.zoom = False

    def on_mouse_move(self, win, x, y):
        if self.scene.arc:
            p2 = self.project_on_sphere(x, y, (min(width, height) / 2)) # get p2 on arcball
            self.scene.arc_angle = np.arccos(np.dot(self.scene.arc_start, p2)) # get angle between p1 and p2
            self.scene.arc_axis = np.cross(self.scene.arc_start, p2) # get axis of rotation
        if self.scene.move:
            if x < self.scene.move_start[0]:
                self.scene.center[0] += 0.005
            elif x > self.scene.move_start[0]:
                self.scene.center[0] -= 0.005
            self.scene.move_start[0] = x # update x-start position
            if y < self.scene.move_start[1]:
                self.scene.center[1] -= 0.005
            elif y > self.scene.move_start[1]:
                self.scene.center[1] += 0.005
            self.scene.move_start[1] = y # update y-start position
        if self.scene.zoom:
            if y < self.scene.zoom_start:
                self.scene.size *= 0.99
            elif y > self.scene.zoom_start:
                self.scene.size /= 0.99
            self.scene.zoom_start = y # update start position


    def on_keyboard(self, win, key, scancode, action, mods):
        print("keyboard: ", win, key, scancode, action, mods)
        if action == glfw.PRESS:
            if key == glfw.KEY_ESCAPE:
                self.exitNow = True
            if key == glfw.KEY_A:
                self.scene.animate = not self.scene.animate
            if key == glfw.KEY_P:
                self.scene.persective = not self.scene.persective
                print("toggle projection: orthographic / perspective ")
            if key == glfw.KEY_S:
                self.scene.shading = (self.scene.shading + 1) % 3
                self.scene.set_shading()
                print("toggle shading: wireframe, grouraud, phong")
            if key == glfw.KEY_X:
                self.scene.angleX += 18
                print("rotate: around x-axis")
            if key == glfw.KEY_Y:
                self.scene.angleY += 18
                print("rotate: around y-axis")
            if key == glfw.KEY_Z:
                self.scene.angleZ += 18
                print("rotate: around z-axis")

    def on_size(self, win, width, height):
        self.scene.set_size(width, height)

    def project_on_sphere(self, x, y, r):
        x, y = x - width/2.0, height/2.0 - y
        a = min(r*r, x**2 + y**2)
        z = np.sqrt(r*r - a)
        l = np.sqrt(x**2 + y**2 + z**2)
        return x/l, y/l, z/l

    def run(self):
        while not glfw.window_should_close(self.window) and not self.exitNow:
            # poll for and process events
            glfw.poll_events()

            # setup viewport
            width, height = glfw.get_framebuffer_size(self.window)
            glViewport(0, 0, width, height)

            # call the rendering function
            self.scene.draw()
            
            # swap front and back buffer
            glfw.swap_buffers(self.window)

        # end
        glfw.terminate()

# main function
if __name__ == '__main__':

    print("press 'a' to toggle animation...")
    print("press 'p' to toggle projection...")
    print("press 's' to toggle shading...")
    print("press 'x' to rotate around x-axis...")
    print("press 'y' to rotate around y-axis...")
    print("press 'z' to rotate around z-axis...")
    print("hold 'mouse middle button' to zoom...")
    print("hold 'mouse right button' to pan...")
    print("press 'esc' to quit...")

    # set size of render viewport
    width, height = 640, 480

    # instantiate a scene
    scene = Scene(width, height)

    # pass the scene to a render window ... 
    rw = RenderWindow(scene)

    # ... and start main loop
    rw.run()
