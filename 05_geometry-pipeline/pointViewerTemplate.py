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
/**         pointViewerTemplate.py
 *
 *          Simple Python template to load vertices, transform them to pixel
 *          coordinates and display results in a 2D scene using OpenGL.
 ****
"""

import numpy as np
import sys
from rendering import Scene, RenderWindow


if __name__ == '__main__':
    if len(sys.argv) != 2:
       print("pointViewer.py <path_to_obj>")
       print("'a' to toggle animation")
       print("'p' to switch between orthographic and perspective projection")
       print("'ESC' to quit")
       print("'x' : rotate the pointset clockwise around the x-axis ")
       print("'X' : rotate the pointset counter clockwise around the x-axis ")
       print("'y' : rotate the pointset clockwise around the y-axis ")
       print("'Y' : rotate the pointset counter clockwise around the y-axis ")
       print("'z' : rotate the pointset clockwise around the z-axis ")
       print("'Z' : rotate the pointset counter clockwise around the z-axis ")
       sys.exit(-1)

    # set size of render viewport
    width, height = 640, 480


    # TODO :
    # - read in points and replace dummy data
    vertices = [[], [], []]
    with open(sys.argv[1], 'r') as file:
        for line in file:
            if line.startswith('v '):
                _, x, y, z = line.split()
                vertices[0].append(float(x))
                vertices[1].append(float(y))
                vertices[2].append(float(z))

    vertices = np.stack([vertices[0], vertices[1], vertices[2]], axis=1)

    # TODO :
    # - determine bounding box of point set
    # - determine matrix for translation of center of bounding box to origin
    # - determine matrix to scale to [-1,1]^2

    # Set initial bounding box values to infinity and -infinity
    min_x = min_y = min_z = float('inf')
    max_x = max_y = max_z = float('-inf')

    # Read in vertices from file and search for min and max values (use meshes from the previous exercise)
    with open(sys.argv[1], 'r') as file:
        for line in file:
            if line.startswith('v '):
                _, x, y, z = line.split()
                x, y, z = float(x), float(y), float(z)
                
                # Update minimum and maximum values for each axis
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)
                min_z = min(min_z, z)
                max_z = max(max_z, z)

    # Calculate bounding box dimensions
    box_width = max_x - min_x
    box_height = max_y - min_y
    box_depth = max_z - min_z

    # Calculate center of bounding box
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2
    center_z = (min_z + max_z) / 2

    # Create translation matrix
    T = np.array([
        [1, 0, 0, -center_x],
        [0, 1, 0, -center_y],
        [0, 0, 1, -center_z],
        [0, 0, 0, 1]
    ])

    # Calculate scaling factors
    scale_x = 2 / box_width
    scale_y = 2 / box_height
    scale_z = 2 / box_depth

    # Create scaling matrix
    S = np.array([
        [scale_x, 0, 0, 0],
        [0, scale_y, 0, 0],
        [0, 0, scale_z, 0],
        [0, 0, 0, 1]
    ])

    # Combine matrices to model transformation matrix
    M = S @ T

    # Apply model transformation matrix to each point
    vertices = np.hstack([vertices, np.ones((vertices.shape[0], 1))])
    vertices = vertices @ M.T

    # Transform from homogeneous to euclidian point coordinates
    vertices = vertices[:, :3]

    # Perform view port transformation
    vertices[:, 0] = vertices[:, 0] * width / 2 + width / 2
    vertices[:, 1] = vertices[:, 1] * height / 2 + height / 2

    def vertex_transformation_pipeline(vertices, alpha, beta, gamma, width, height, proj_type='orthographic'):
        """
        :param      List    vertices:   The list of normalized vertex positions given to the scene
        :param      float   alpha:      Rotation around the x-axis in degrees
        :param      float   beta:       Rotation around the y-axis in degrees
        :param      float   gamma:      Rotation around the z-axis in degrees
        :param      int     width:      Scene height in pixels (may change with window resizing)
        :param      int     height:     Scene height in pixels (may change with window resizing)
        :param      str     proj_type:  The projection type to use (Either 'orthographic' or 'perspective')

        :return     List    pix_coords: A list of 2D pixel coordinates to render
        """
        # TODO :
        # - define view transformation matrix
        # - define projection matrix
        # - combine matrices to model view projection matrix
        # - apply model view projection matrix to each point
        # - transform from homogeneous to euclidian point coordinates
        # - perform view port transformation

        rotation_x = np.array([[1, 0, 0, 0],
                            [0, np.cos(alpha), -np.sin(alpha), 0],
                            [0, np.sin(alpha), np.cos(alpha), 0],
                            [0, 0, 0, 1]])

        rotation_y = np.array([[np.cos(beta), 0, np.sin(beta), 0],
                            [0, 1, 0, 0],
                            [-np.sin(beta), 0, np.cos(beta), 0],
                            [0, 0, 0, 1]])

        rotation_z = np.array([[np.cos(gamma), -np.sin(gamma), 0, 0],
                            [np.sin(gamma), np.cos(gamma), 0, 0],
                            [0, 0, 1, 0],
                            [0, 0, 0, 1]])

        # Calculate the orthographic projection matrix
        projection_matrix = np.array([[2/width, 0, 0, 0],
                                    [0, 2/height, 0, 0],
                                    [0, 0, 1, 0],
                                    [0, 0, 0, 1]])
        
        # Compute the combined view projection matrix
        view_projection_matrix = rotation_x @ rotation_y @ rotation_z @ projection_matrix

        # Apply the view transformation to each vertex
        vertices = np.hstack([vertices, np.ones((vertices.shape[0], 1))])
        vertices = vertices @ view_projection_matrix.T

        # Transform from homogeneous to euclidian point coordinates
        vertices = vertices[:, :3]

        # Scale and translate the vertices to fit within the viewport size
        vertices[:, 0] = (vertices[:, 0]) * 0.5 * width
        vertices[:, 1] = (vertices[:, 1]) * 0.5 * height

        return vertices[:,:2]


    # instantiate a scene
    scene = Scene(width, height, vertices, vertex_transformation_pipeline, "pointViewer Template")

    rw = RenderWindow(scene)
    rw.run()
