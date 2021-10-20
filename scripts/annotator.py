""" Frame Image Annotator """
#!/usr/bin/env python3

# Add license here

# Add imports here
import cv2
from common import constants
#pylint: disable=wrong-import-position

# class Annotator
# Description: Class for frame annotation
# Parameter: None
# Return value: None
class Annotator:
    """ Frame annotator """

    __annotator = None  # Class instance
    __frame = None      # Frame image

    # function get_instance
    # Description: Functon to return the class instance
    # Parameter: None
    # Return value: __annotator
    @staticmethod
    def get_instance():
        """ Static access method. """

        # Check if not yet initialized
        if Annotator.__annotator is None:

            # Call the class constructor
            Annotator()

        # Return the class instance
        return Annotator.__annotator


    # function __init__
    # Description: Class constructor
    # Parameter: self
    # Return value: None
    def __init__(self):
        """ Virtually private constructor. """

        # Check if not yet initialized
        if Annotator.__annotator is None:

            # Initialize class instance
            Annotator.__annotator = self


    # function set_frame
    # Description: Function to set frame image
    # Parameter: self, frame
    # Return value: None
    def set_frame(self, frame):
        """ Set frame image """

        self.__frame = frame


    # function annotate
    # Description: Function to annotate the frame
    # Parameter: self, annotator_data
    # Return value: frame
    def annotate(self, annotator_data):
        """ Annotate the frame """

        frame = self.__frame.copy()    # Set frame image

        for data in annotator_data:

            # Get bbox and centroid details
            bbox, centroid = data

            # Get bbox details
            bbox_y = int(bbox.top)         # Set bounding box y point
            bbox_x = int(bbox.left)        # Set bounding box x point
            width = int(bbox.width)        # Set bounding box width
            height = int(bbox.height)      # Set bounding box height

            # Draw bounding box
            cv2.rectangle(frame, (bbox_x, bbox_y), (bbox_x + width, bbox_y + height), \
                constants.PTS_ALRT_ZONE_COLOR, 1)

            # Draw centroid
            cv2.circle(frame, centroid, 7, constants.PTS_ALRT_ZONE_COLOR, -1)

        __, img = cv2.imencode(".jpg", frame)
        byte_img = img.tobytes()

        # Return the annotated frame image
        return byte_img
