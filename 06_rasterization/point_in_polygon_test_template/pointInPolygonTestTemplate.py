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

        return np.random.random() > 0.5


    # instantiate a scene
    scene = Scene(width, height, test_line_intersect, "Point in (nonconvex) polygon test")

    rw = RenderWindow(scene)
    rw.run()
