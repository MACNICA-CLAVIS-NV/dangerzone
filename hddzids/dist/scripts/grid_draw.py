""" Draw Bird's Eye View Grid """
#!/usr/bin/env python3

# Add license here

# Add imports here
import cv2
import numpy as np
from common import constants
#pylint: disable=wrong-import-position

# class GridDraw
# Description: Class for drawing Bird's Eye Grid and centroids
# Parameter: None
# Return value: None
class GridDraw:
    """ Draw Bird's Eye View Grid """

    __grid_draw = None         # Class instance
    __grid = None              # Grid template with danger zone box

    # function get_instance
    # Description: Functon to return the class instance
    # Parameter: b_eye_dimension, grid_division, d_zone_cornert_pts
    # Return value: __grid_draw
    @staticmethod
    def get_instance():
        """ Static access method. """

        # Check if not yet initialized
        if GridDraw.__grid_draw is None:

            # Call the class constructor
            GridDraw()

        # Return the class instance
        return GridDraw.__grid_draw


    # function __init__
    # Description: Class constructor
    # Parameter: self
    # Return value: None
    def __init__(self):
        """ Virtually private constructor. """

        # Check if not yet initialized
        if GridDraw.__grid_draw is None:

            GridDraw.__grid_draw = self           # Set GridDraw class instance


    # function initialize_grid
    # Description: Function that initializes grid
    # Parameter: self, b_eye_dimension, grid_division, d_zone_cornert_pts
    # Return value: None
    def initialize_grid(self, b_eye_dimension, grid_division, d_zone_cornert_pts):
        """ Initialize grid """

        # Check if grid is not yet initialized
        if self.__grid is None:

            # Initialize grid template
            self.__grid = self.__create_grid(b_eye_dimension)
            self.__draw_lines(self.__grid, b_eye_dimension, grid_division, d_zone_cornert_pts)


    # function __create_grid
    # Description: Function to create grid template
    # Parameter: self, b_eye_dimension, grid_division
    # Return value: grid
    @classmethod
    def __create_grid(cls, b_eye_dimension):
        """ Create grid template """

        # Initialize grid
        grid = np.zeros((b_eye_dimension[1], b_eye_dimension[0], 3), np.uint8)

        # Return grid template
        return grid


    # function __draw_lines
    # Description: Function to draw grid lines
    # Parameter: self, frame, b_eye_dimension, grid_division, d_zone_corner_pts
    # Return value: None
    def __draw_lines(self, frame, b_eye_dimension, grid_division, d_zone_corner_pts):
        """ Draw grid lines on template """

        # Set grid cell dimension
        cell_x = int(b_eye_dimension[0] / grid_division)
        cell_y = int(b_eye_dimension[1] / grid_division)

        ###############################################################
        # Draw grid lines
        ###############################################################

        for pt_x in range(cell_x, b_eye_dimension[0], cell_x):

            cv2.line(frame, (pt_x, 0), (pt_x, b_eye_dimension[1]), constants.GRID_COLOR, 1)

        for pt_y in range(cell_y, b_eye_dimension[1], cell_x):

            cv2.line(frame, (0, pt_y), (b_eye_dimension[0], pt_y), constants.GRID_COLOR, 1)

        # Set frame as our grid template
        self.__grid = frame

        ###############################################################
        # Draw danger zone
        ###############################################################

        cv2.line(frame, (d_zone_corner_pts[0], d_zone_corner_pts[1]), \
            (d_zone_corner_pts[2], d_zone_corner_pts[3]), constants.GRID_D_ZONE_COLOR, 2)
        cv2.line(frame, (d_zone_corner_pts[2], d_zone_corner_pts[3]), \
            (d_zone_corner_pts[4], d_zone_corner_pts[5]), constants.GRID_D_ZONE_COLOR, 2)
        cv2.line(frame, (d_zone_corner_pts[4], d_zone_corner_pts[5]), \
            (d_zone_corner_pts[6], d_zone_corner_pts[7]), constants.GRID_D_ZONE_COLOR, 2)
        cv2.line(frame, (d_zone_corner_pts[6], d_zone_corner_pts[7]), \
            (d_zone_corner_pts[0], d_zone_corner_pts[1]), constants.GRID_D_ZONE_COLOR, 2)


    # function __draw_centroids
    # Description: Function to plot centroids in the grid
    # Parameter: self, frame, data
    # Return value: frame
    @classmethod
    def __draw_centroids(cls, frame, data):
        """ Plot centroids in the grid """

        # Check each item
        for item in data:

            # Alert flag is true
            if item[1]:
                # Centroid color is red
                centroid_color = constants.PTS_ALRT_ZONE_COLOR
            else:
                # Centroid color is blue
                centroid_color = constants.PTS_NORM_ZONE_COLOR

            # Draw centroid
            cv2.circle(frame, item[0], 7, centroid_color, -1)

        return frame


    # function get_b_eye_grid_img
    # Description: Function that returns the bytecode copy of the grid image with centroids
    # Parameter: self, centroid_data
    # Return value: byte_img
    def get_b_eye_grid_img(self, centroid_data):
        """ Return bytecode copy of the grid image """

        # Copy the grid template
        frame = self.__grid.copy()

        # Plot centroid
        frame = self.__draw_centroids(frame, centroid_data)

        # Convert to bytecode
        _, img = cv2.imencode(".jpg", frame)
        byte_img = img.tobytes()

        # Return bytecode grid image
        return byte_img
