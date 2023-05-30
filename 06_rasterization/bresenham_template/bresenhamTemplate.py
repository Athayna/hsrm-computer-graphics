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
/**         bresenhamTemplate.py
 *
 *          Simple Python template to calculate pixels on a bresenham line, and
 *          display results in a 2D scene using OpenGL.
 ****
"""

from rendering_bresenham import Scene, RenderWindow


def bresenham_line_callback(p, q, gridsize):
    """
        TODO: implement bresenhams algorithm

        :param      Tuple[int, int] p:          Line start pixel coordinates
        :param      Tuple[int, int] p:          Line end pixel coordinates
        :param      int             gridsize:   Pixel grid size (horizontal and vertical)

        :return     List[Tuple[int, int]]:      List of pixel coordinates on line fromp to q using bresenhams algorithm
    """
    return [p, q]




# call main
if __name__ == '__main__':
    print("bresenham.py")
    print("Using Bresenhams algorithm to draw lines on a raster")
    print("pressing 'C' should clear everything")
    print("pressing 'S' should toggle display of bresenham line")

    # set size of render viewport
    width, height = 640, 480

    # instantiate a scene
    scene = Scene(width, height, bresenham_line_callback, "Line drawing using Bresenhams algorithm (Template)")

    rw = RenderWindow(scene)
    rw.run()
