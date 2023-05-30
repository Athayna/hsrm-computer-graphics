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
/**         lineClippingTemplate.py
 *
 *          Simple Python template to calculate line codes and calculate clipped
 *          lines. Results are displayed in a 2D scene using OpenGL.
 ****
"""

from rendering_lineClipping import Scene, RenderWindow


# call main
if __name__ == '__main__':
    print("lineClipping.py")
    print("pressing 'C' should clear the everything")
    print("pressing 'S' toggle display of clipped lines")

    # set size of render viewport
    width, height = 640, 480


    # determine line code
    def line_code_callback(p1, code1, p2, code2):
        """ TODO 1:
            - implement the Cohen-Sutherland Algorithm.
            - return -1 if line is completely on on side of the clipping region
                    line code otherwise.

        :param  Tuple[float, float] p1:     The line segment start point
        :param  int                 code1:  The region code of point 1
        :param  Tuple[float, float] p2:     The line segment end point
        :param  int                 code2:  The region code of point 2

        :return int: line code or -1
        """

        return -1




    def clip_line_callback(p1, p2, line_code, x_min, y_min, x_max, y_max):
        """ TODO 2:
            - implement the Cohen-Sutherland Algorithm.
            - return clipped line segment

        :param  Tuple[float, float] p1:         The line segment start point
        :param  Tuple[float, float] p2:         The line segment end point
        :param  int                 line_code:  The line code assigned in 'line_code_callback'
        :param  float               x_min:      The clipping region's minimum x position
        :param  float               y_min:      The clipping region's minimum y position
        :param  float               x_max:      The clipping region's maximum x position
        :param  float               y_max:      The clipping region's maximum y position
        :returns List[Tuple[float, float], Tuple[float, float]]: The clipped line segment
        """

        return [p1, p2]


    # instantiate a scene
    scene = Scene(width, height, line_code_callback, clip_line_callback, "Line clipping Template")

    rw = RenderWindow(scene)
    rw.run()
