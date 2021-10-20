""" Danger Zone Monitoring """
#!/usr/bin/env python3

# Add license here

# Add imports here
import time
from datetime import datetime
from common import constants
from common.common import Common
#pylint: disable=wrong-import-position

# class Monitoring
# Description: Class for danger zone monitoring
# Parameter: None
# Return value: None
class Monitoring:
    """ Danger zone monitoring """

    __monitoring = None                   # Monitoring class instance
    __common = None                       # Common class instance

    __trans_d_zone = None                 # Holds Transformed danger zone calibration

    # Monitoring details
    __obj_ids = []                        # Monitoring ids
    __dwell_time = []                     # Monitoring dwell time
    __alert_flag = []                     # Monitoring alert flag
    __alert_trig_time = []                # Alert time triggered

    __has_new_alert = False

    # function get_instance
    # Description: Functon to return the class instance
    # Parameter: None
    # Return value: __monitoring
    @staticmethod
    def get_instance():
        """ Static access method. """

        # Check if not yet initialized
        if Monitoring.__monitoring is None:

            # Call the class constructor
            Monitoring()

        # Return the class instance
        return Monitoring.__monitoring


    # function __init__
    # Description: Class constructor
    # Parameter: self
    # Return value: None
    def __init__(self):
        """ Virtually private constructor. """

        # Check if not yet initialized
        if Monitoring.__monitoring is None:

            Monitoring.__monitoring = self                      # Set Monitoring class instance
            self.__common = Common.get_instance()               # Set Common class instance


    # function initialize_d_zone
    # Description: Function that initializes the danger zone transformation
    # Parameter: self, b_eye_dim, b_eye_calib, d_zone_calib
    # Return value: None
    def initialize_d_zone(self, b_eye_dim, b_eye_calib, d_zone_calib):
        """ Initializes danger zone transformation """

        # Check if transformed danger zone is not yet initialized
        if self.__trans_d_zone is None:

            # Set transformed danger zone corner points
            self.__set_trans_d_zone(b_eye_dim, b_eye_calib, d_zone_calib)


    # function __set_trans_d_zone
    # Description: Function that transform the corner points of the danger zone calibration
    # Parameter: self, b_eye_dim, b_eye_calib, d_zone_calib
    # Return value: None
    def __set_trans_d_zone(self, b_eye_dim, b_eye_calib, d_zone_calib):
        """ Set transformed danger zone """

        # Write details in the input file.
        # This input file will be read by Bird's Eye Converter plugin when executed
        self.__common.write_b_eye_input_file(b_eye_dim, b_eye_calib, \
           [(d_zone_calib[0], d_zone_calib[1]), (d_zone_calib[2], d_zone_calib[3]), \
            (d_zone_calib[4], d_zone_calib[5]), (d_zone_calib[6], d_zone_calib[7])])

        # Run the Bird's Eye Converter plugin
        self.__common.run_b_eye_converter()

        # Get the list of transformed centroid
        trans_centroid_list = self.__common.read_b_eye_output_file()

        self.__trans_d_zone = []        # Holds transformed danger zone corner points

        # Read each transformed centroid
        for centroid_x, centroid_y in trans_centroid_list:

            # Set transformed danger zone corner points
            self.__trans_d_zone.append(centroid_x)
            self.__trans_d_zone.append(centroid_y)


    # function run
    # Description: Function that runs the monitoring process
    # Parameter: self, track_id_list, trans_centroid_list
    # Return value: result
    def run(self, track_id_list, trans_centroid_list):
        """ Runs the monitoring process """

        id_list_len = len(track_id_list)               # Get id count

        # Write details in the input file.
        # This input file will be read by Bird's Eye Converter plugin when executed
        self.__common.write_b_eye_input_file(constants.D_ZONE_DIM, self.__trans_d_zone, \
           trans_centroid_list)

        # Run the Bird's Eye Converter plugin
        self.__common.run_b_eye_converter()

        # Get the list of transformed centroid
        trans_dz_centroid_list = self.__common.read_b_eye_output_file()

        try:

            # Check each index corresponds to id_list
            for index in range(0, id_list_len, 1):

                # Check if the centroid is outside the danger zone
                outside_flag = int(trans_dz_centroid_list[index][0]) <= 0 or \
                    int(trans_dz_centroid_list[index][0]) >= 50 or \
                    int(trans_dz_centroid_list[index][1]) <= 0 or \
                    int(trans_dz_centroid_list[index][1]) >= 50

                # Check if track id has existing record
                if track_id_list[index] in self.__obj_ids:

                    # Get monitoring index
                    monitor_index = self.__get_id_index(track_id_list[index])

                    # Centroid is outside the danger zone
                    if outside_flag is True:

                        # Remove existing record
                        self.__remove_alert(monitor_index)

                    # Centroid is insde the danger zone
                    else:

                        # Check dwell time
                        self.__dwell_time_check(monitor_index)

                # Track id has no record yet
                else:

                    # If inside danger zone, add new record
                    if not outside_flag:

                        # add new item in danger zone monitoring
                        self.__add_alert(track_id_list[index])

        except IndexError:

            print("Transform error from Bird's Eye Converter output file...")


    # function __get_id_index
    # Description: Function that returns the monitoring index
    # Parameter: self, track_id
    # Return value: result_index
    def __get_id_index(self, track_id):
        """ Returns the monitoring index """

        ids_len = len(self.__obj_ids)      # id count

        result_index = -1                  # Holds index as result

        # Check if id list is not empty
        if ids_len != 0:

            # Check each monitoring index
            for index in range(0, ids_len, 1):

                # Track id exists
                if track_id == self.__obj_ids[index]:

                    # Set index as result
                    result_index = index

                    # Exit loop
                    break

        # Return the monitoring index
        return result_index

    # function get_trans_d_zone
    # Description: Function that returns the transformed danger zone corner points
    # Parameter: self
    # Return value: self.__trans_d_zone.copy()
    def get_trans_d_zone(self):
        """ Returns the transformed danger zone """

        return self.__trans_d_zone.copy()


    # function has_alert
    # Description: Function that returns True if there is any existing alert, False if no alert
    # Parameter: self
    # Return value: result
    def has_alert(self):
        """ Returns flag for alert existence """

        result = False        # Holds the Has alert flag

        # Check each alert flag
        for flag in self.__alert_flag:

            # Alert exists
            if flag is True:

                # Set result to True
                result = True

                # Exit loop
                break

        # Return Has alert flag
        return result


    # function has_alert
    # Description: Function that return True if the track id has alert, False if not
    # Parameter: self, track_id
    # Return value: result
    def has_alert_by_id(self, track_id):
        """ Returns flag for alert existence """

        result = False        # Holds the Has alert flag

        # Get alert record index
        index = self.__get_id_index(track_id)

        # Check if record exists
        if index >= 0:

            # Set alert flag
            result = self.__alert_flag[index]

        # Return alert flag
        return result


    # function __add_alert
    # Description: Function that adds new alert record
    # Parameter: self, track_id
    # Return value: None
    def __add_alert(self, track_id):
        """ Adds new alert """

        # Add new alert record
        self.__obj_ids.append(track_id)
        self.__dwell_time.append(time.time())
        self.__alert_flag.append(False)
        self.__alert_trig_time.append('')


    # function remove_alert
    # Description: Function that removes an alert record
    # Parameter: self, index
    # Return value: None
    def __remove_alert(self, index):
        """ Removes an alert record """

        # Remove alert item
        del self.__obj_ids[index]
        del self.__dwell_time[index]
        del self.__alert_flag[index]
        del self.__alert_trig_time[index]


    # function __dwell_time_check
    # Description: Function that checks the dwell time inside the danger zone
    # Parameter: self, index
    # Return value: None
    def __dwell_time_check(self, index):
        """ Checks dwell time inside the danger zone """

        # Check dwell time
        current_time = time.time()
        time_passed = current_time - self.__dwell_time[index]

        # Check if dwell time reached time limit
        if self.__alert_flag[index] is False and \
            constants.D_ZONE_DTIME_LIMIT <= time_passed:

            # Set dwell time
            self.__dwell_time[index] = time_passed

            # Set alert flag to True
            self.__alert_flag[index] = True

            # Set alert trigger time
            dtime = datetime.now()
            self.__alert_trig_time[index] = dtime.strftime("%Y-%m-%d %H:%M:%S")

            # Activate flag for new alert
            self.__has_new_alert = True


    # function get_alerts
    # Description: Function that returns all alert item
    # Parameter: self
    # Return value: alert_list
    def get_alerts(self):
        """ Return alerts """

        alerts = []         # Holds alert items

        # If new alert exists
        if self.__has_new_alert is True:

            # Disable new alert flag
            self.__has_new_alert = False

            # Get index count
            len_ids = len(self.__obj_ids)

            # Check each index
            for index in range(0, len_ids, 1):

                # Check if alert is activated
                if self.__alert_flag[index]:

                    # Add alert details
                    alerts.append((self.__obj_ids[index], \
                        self.__dwell_time[index], \
                        self.__alert_flag[index], \
                        self.__alert_trig_time[index]))

        # Return alerts
        return alerts
