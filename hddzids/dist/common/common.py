""" HDDZIDS Common """
#!/usr/bin/env python3

# Add license here

# Add imports here
import os
import cv2
from common import constants
from plugins import birds_eye_converter
#pylint: disable=wrong-import-position

# class Common
# Description: Class for common functions
# Parameter: None
# Return value: None
class Common:
    """ Common class """

    __common = None                 # Common Class instance

    # function get_instance
    # Description: Functon to return the class instance
    # Parameter: None
    # Return value: __common
    @staticmethod
    def get_instance():
        """ Static access method. """

        # Check if not yet initialized
        if Common.__common is None:

            # Call the class constructor
            Common()

        # Return the class instance
        return Common.__common

    # function __init__
    # Description: Class constructor
    # Parameter: self
    # Return value: None
    def __init__(self):
        """ Virtually private constructor. """

        # Check if not yet initialized
        if Common.__common is None:

            # Initialize class instance
            Common.__common = self

    # function get_calibrations
    # Description: Function that extract the data from calibration file
    # Parameter: self
    # Return value: b_eye_calib_final, d_zone_calib_final
    @classmethod
    def get_calibrations(cls):
        """ Read calibration file """

        calibrations = None       # functionault return value

        # Check if the file is existing
        if os.path.isfile(constants.CALIBRATION_DATA_PATH):

            # Open the calibration file
            with open(constants.CALIBRATION_DATA_PATH, \
                encoding=constants.FILE_ENCODING) as calibration_file:

                # Read lines from file
                calibration_lines = calibration_file.readlines()

                # Check if the number of lines is valid
                if constants.CALIBRATION_COUNT == len(calibration_lines):

                    # Extract values
                    b_eye_calib_arr = calibration_lines[0].split(',')
                    d_zone_calib_arr = calibration_lines[1].split(',')

                    # Check if value count for Bird's Eye calibration is valid
                    if len(b_eye_calib_arr) != constants.CALIBRATION_VALUE_COUNT:

                        print(f"[{constants.CALIBRATION_DATA_PATH}]:" + \
                            " Line 1 has incorrect value count!")

                    # Check if value count for Danger Zone calibration is valid
                    elif len(d_zone_calib_arr) != constants.CALIBRATION_VALUE_COUNT:

                        print(f"[{constants.CALIBRATION_DATA_PATH}]:" + \
                            " Line 2 has incorrect value count!")

                    else:

                        b_eye_calib_final = []     # Holds Bird's Eye calibration values
                        d_zone_calib_final = []    # Holds Danger Zone calibration vlaues

                        try:

                            # Convert to int before appending each value
                            for num in range(0, constants.CALIBRATION_VALUE_COUNT, 1):
                                b_eye_calib_final.append(int(b_eye_calib_arr[num]))
                                d_zone_calib_final.append(int(d_zone_calib_arr[num]))

                            # Set calibrations as result
                            result = (b_eye_calib_final, d_zone_calib_final)

                        # Error due to invalid literal for int
                        except ValueError:

                            print(f"[{constants.CALIBRATION_DATA_PATH}]" + \
                                " has invalid literal for int!")
                            result = None

                        finally:

                            # Set result
                            calibrations = result

                # Error: Invalid line count
                else:

                    print(f"[{constants.CALIBRATION_DATA_PATH}] has incorrect content!")

        # Error: File not found
        else:

            print(f"[{constants.CALIBRATION_DATA_PATH}]: File not found!")

        # Return calibrations. if not successful, return None
        return calibrations


    # function write_b_eye_input_file
    # Description: Function that write data in the input file for Bird's Eye Converter plugin
    # Parameter: cls, b_eye_dimension, b_eye_calibration, centroids
    # Return value: None
    @classmethod
    def write_b_eye_input_file(cls, b_eye_dimension, b_eye_calibration, centroids):
        """ Write data in the Bird's Eye Converter plugin input file """

        # Write data in the input file
        with open(constants.B_EYE_INPUT_FILE, 'w', \
            encoding=constants.FILE_ENCODING) as input_file:

            # Write Bird's Eye dimension details
            input_text = f"{b_eye_dimension[0]},{b_eye_dimension[1]}," + \
                f"{b_eye_dimension[2]},{b_eye_dimension[3]}," + \
                f"{b_eye_dimension[4]},{b_eye_dimension[5]}," + \
                f"{b_eye_dimension[6]},{b_eye_dimension[7]}\n"
            input_file.write(input_text)

            # Write selected area for Bird's Eye View from Camera calibration
            input_text = ""
            b_eye_calib_len = len(b_eye_calibration)
            for index in range(0, b_eye_calib_len, 1):
                if index == 0:
                    input_text = f"{b_eye_calibration[index]}"
                else:
                    input_text = f"{input_text},{b_eye_calibration[index]}"
            input_text = f"{input_text}\n"
            input_file.write(input_text)

            # Write the list of centroids to be converted to bird's eye view centroids
            for centroid in centroids:
                input_text = f"{centroid[0]},{centroid[1]}\n"
                input_file.write(input_text)


    # function write_calibration_file
    # Description: Function that write data in the calibration file
    # Parameter: cls, b_eye_calib, d_zone_calib
    # Return value: None
    @classmethod
    def write_calibration_file(cls, b_eye_calib, d_zone_calib):
        """ Write calibration file """

        # Write data in the input file
        with open(constants.CALIBRATION_DATA_PATH, 'w', \
            encoding=constants.FILE_ENCODING) as calib_file:

            # Write Bird's Eye calibration details
            input_text = f"{b_eye_calib[0]},{b_eye_calib[1]}," + \
                f"{b_eye_calib[2]},{b_eye_calib[3]}," + \
                f"{b_eye_calib[4]},{b_eye_calib[5]}," + \
                f"{b_eye_calib[6]},{b_eye_calib[7]}\n"
            calib_file.write(input_text)

            # Write Danger Zone calibration details
            input_text = f"{d_zone_calib[0]},{d_zone_calib[1]}," + \
                f"{d_zone_calib[2]},{d_zone_calib[3]}," + \
                f"{d_zone_calib[4]},{d_zone_calib[5]}," + \
                f"{d_zone_calib[6]},{d_zone_calib[7]}\n"
            calib_file.write(input_text)

    # function read_b_eye_output_file
    # Description: Function that read the output file after Bird's Eye Converter plugin execution
    # Parameter: cls
    # Return value: trans_centroids
    @classmethod
    def read_b_eye_output_file(cls):
        """ Read the Bird's Eye Converter plugin output file """

        trans_centroids = []    # Holds the list of transformed centroid

        # Check the file if existing
        if os.path.isfile(constants.B_EYE_OUTPUT_FILE):

            # Read the output file
            with open(constants.B_EYE_OUTPUT_FILE, 'r', \
                encoding=constants.FILE_ENCODING) as out_file:

                # Read each line to get centroid
                content = out_file.readlines()
                for item in content:

                    values = item.split(",")

                    if len(values) != 2:
                        continue

                    centroid = (int(values[0]), int(values[1]))
                    trans_centroids.append(centroid)

        # Return the list of transformed centroids
        return trans_centroids


    # function run_b_eye_converter
    # Description: Function that runs command to execute the
    #              binary form of Bird's Eye Converter plugin
    # Parameter: cls
    # Return value: None
    @classmethod
    def run_b_eye_converter(cls):
        """ Runs Bird's Eye converter """

        birds_eye_converter.run()


    # function draw_corner
    # Description: Function that draws calibration corner
    # Parameter: cls
    # Return value: cv2.rectangle
    @classmethod
    def draw_corner(cls, frame, point_x, point_y, color):
        """ Draw corner """

        return cv2.rectangle(frame, \
            (point_x  - constants.CORNER_PADDING, point_y - constants.CORNER_PADDING), \
            (point_x  + constants.CORNER_PADDING, point_y + constants.CORNER_PADDING), \
            color, -1)


    # function post_message
    # Description: Function that posts message in terminal
    # Parameter: cls
    # Return value: cv2.rectangle
    @classmethod
    def post_message(cls, class_name, message):
        """ Post message in the terminal """

        print(f"[{class_name}]{message}")


    # function check_calibration_file
    # Description: Function that validates the calibration file
    # Parameter: self
    # Return value: result
    def check_calibration_file(self):
        """ Check calibration file """

        result = constants.V_CALIB_DEFAULT        # Holds the calibration file check result

        # Check the file if existing
        if os.path.isfile(constants.CALIBRATION_DATA_PATH):

            # Open the calibration file
            with open(constants.CALIBRATION_DATA_PATH, \
                encoding=constants.FILE_ENCODING) as calibration_file:

                # Read lines from file
                calibration_lines = calibration_file.readlines()

                # Get content line count
                line_cnt = len(calibration_lines)

                # Calibration line count is 2
                if line_cnt == constants.CALIBRATION_COUNT:

                    # Validate calibration values
                    result = self.__validate_calibration_values(calibration_lines)

                # Empty file
                elif line_cnt == 0:

                    # Calibration file is empty
                    result = constants.V_CALIB_FILE_EMPTY

                # Invalid file
                else:

                    # Calibration file has invalid content
                    result = constants.V_CALIB_NG_CONTENT

        # File not found
        else:

            # Calibration file is not found
            result = constants.V_CALIB_NO_FILE

        # Return validation result
        return result


    # function __validate_calibration_values
    # Description: Function that validates calibration values
    # Parameter: cls, calibration_lines
    # Return value: result
    @classmethod
    def __validate_calibration_values(cls, calibration_lines):
        """ Validates the calibration values """

        result = constants.V_CALIB_DEFAULT  # Holds the validation result


        # Check each line
        for calib in calibration_lines:

            # Split line into values
            calib_values = calib.split(',')

            # Value count is 8
            if len(calib_values) == constants.CALIBRATION_VALUE_COUNT:

                # Check each value
                for value in calib_values:

                    try:

                        # Check if value is a valid int literal
                        int(value)

                    # Value is an invalid int literal
                    except ValueError:

                        # Calibration file has invalid content
                        result = constants.V_CALIB_NG_CONTENT

                    # Value is a valid int literal
                    else:

                        # Calibration file has invalid content
                        result = constants.V_CALIB_OK

                    finally:
                        pass

            # Invalid value count
            else:

                # Calibration file has invalid content
                result = constants.V_CALIB_NG_CONTENT

        # Return the validation result
        return result


    # function show_text
    # Description: Function that displays screen text
    # Parameter: cls, img, text, font, pos, font_scale, font_thickness, text_color, text_color_bg
    # Return value: None
    @classmethod
    def show_text(cls, img, text, pos, font_scale, font_thickness, \
        text_color=(0, 255, 0), text_color_bg=(0, 0, 0)):
        """Displays screen text"""

        # Set font style
        font = cv2.FONT_HERSHEY_PLAIN

        # Get text position (x, y)
        pos_x, pos_y = pos

        # Get text size
        text_size, _ = cv2.getTextSize(text, font, font_scale, font_thickness)

        # Get text size width and height
        text_w, text_h = text_size

        # Draw text background
        cv2.rectangle(img, pos, (pos_x + text_w + 10, pos_y + text_h + 10), text_color_bg, -1)

        # Draw text
        cv2.putText(img, text, (pos_x + 5, pos_y + 5 + text_h + font_scale - 1),
            font, font_scale, text_color, font_thickness)
