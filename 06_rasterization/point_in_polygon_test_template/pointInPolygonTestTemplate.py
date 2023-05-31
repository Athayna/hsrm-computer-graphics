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
/**         pointInPolygonTest.py
 *
 *          Simple Python template to check if a pair of 2D line segments intersect.
 *          Results are displayed in a 2D scene using OpenGL.
 ****
"""

import numpy as np

from rendering_pointInPolygon import Scene, RenderWindow


if __name__ == '__main__':
    print("pointInPolygonTest.py")
    print("pressing 'C' should clear the everything")
    print("pressing 'T' should start point in polygon test")

    # set size of render viewport
    width, height = 640, 480


    def test_line_intersect(l1, l2):
        """ Tests if two line segments intersect.

        :param  Tuple[Tuple[float, float], Tuple[float, float]] l1: 2D Start and End Point of first linesegment
        :param  Tuple[Tuple[float, float], Tuple[float, float]] l1: 2D Start and End Point of first linesegment

        :return bool: True if line segments intersect, False otherwise
        """
        # TODO:
        # - write test routine to check wether line l1 and line l2 intersect
        # - should return TRUE iff the lines intersect

        t1 = np.array(l1[1]) - np.array(l1[0]) # b - a
        t2 = np.array(l2[1]) - np.array(l2[0]) # d - c
        u1 = np.array(l2[0]) - np.array(l1[0]) # c - a
        u2 = np.array(l2[1]) - np.array(l1[0]) # d - a
        v1 = np.array(l1[1]) - np.array(l2[0]) # b - c
        v2 = np.array(l1[1]) - np.array(l2[1]) # b - d

        s1 = np.sign(np.cross(t1, u1))
        s2 = np.sign(np.cross(t1, v1))
        s3 = np.sign(np.cross(t2, u2))
        s4 = np.sign(np.cross(t2, v2))

        return s1 * s2 < 0 and s3 * s4 < 0


    # instantiate a scene
    scene = Scene(width, height, test_line_intersect, "Point in (nonconvex) polygon test")

    rw = RenderWindow(scene)
    rw.run()
