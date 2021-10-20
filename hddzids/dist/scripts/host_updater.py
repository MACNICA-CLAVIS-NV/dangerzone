""" Host Updater """
#!/usr/bin/env python3

# Add imports here
import time
import socket
import paho.mqtt.client as mqtt
from common import constants
from common.common import Common
from scripts.grid_draw import GridDraw
from scripts.monitoring import Monitoring
#pylint: disable=wrong-import-position

# class HostUpdater
# Description: Updates host mobile app
# Parameter: None
# Return value: None
class HostUpdater:
    """ Update sender to mobile """

    __host_updater = None  # HostUpdater Class instance
    __common = None        # Common class instance
    __grid_draw = None     # GridDraw class instance
    __monitoring = None    # Monitoring class instance

    # function get_instance
    # Description: Functon to return the class instance
    # Parameter: None
    # Return value: __host_updater
    @staticmethod
    def get_instance():
        """ Static access method. """

        # Check if not yet initialized
        if HostUpdater.__host_updater is None:

            # Call the class constructor
            HostUpdater()

        # Return the class instance
        return HostUpdater.__host_updater


    # function __init__
    # Description: Class constructor
    # Parameter: self
    # Return value: None
    def __init__(self):
        """ Virtually private constructor. """

        # Check if not yet initialized
        if HostUpdater.__host_updater is None:

            HostUpdater.__host_updater = self             # Initialize HostUpdater class instance
            self.__common = Common.get_instance()         # Initialize Common class instance
            self.__grid_draw = GridDraw.get_instance()    # Initialize GridDraw class instance
            self.__monitoring = Monitoring.get_instance() # Initialize Monitoring class instance
            self.name = constants.C_NAME_HOST_UPDATER     # Set class name


    # function __send_update_to_host
    # Description: function that publishes the host update using bytecode image
    # Parameter: image
    # Return value: result
    def __send_update_to_host(self, image):
        """ Updates the mobile host """

        client = mqtt.Client()
        try:
            # Timeout for image saving time
            time.sleep(0.3)
            # Connect client
            client.connect(constants.MOBILE_HOST, constants.MOBILE_PORT, 60)

            #publish topic and image
            client.publish(constants.MSG_TOPIC_HOST_UPDATE, image, 0)

        # This error occurred when:
        # - The MQTT service is off
        # - The Host and Port of MQTT service and Edge PC did not matched
        except ConnectionRefusedError:

            self.__common.post_message(self.name, \
                "[ConnectionRefusedError] Unable to connect to MQTT service!")
            result = constants.RETURN_NG

        # This error occurred when the IP string is not valid
        except socket.gaierror:

            self.__common.post_message(self.name, \
                "[socket.gaierror] Invalid MQTT host!")
            result = constants.RETURN_NG

        # This error occurred when:
        # - The Host is set with integer
        # - The Port is set with string
        except TypeError:

            self.__common.post_message(self.name, \
                "[TypeError] Host IP should be in string form. Port should be in int form.")
            result = constants.RETURN_NG

        # The update is sent successfully
        else:
            result = constants.RETURN_OK

        finally:
            #Disconnect client
            client.disconnect()

        return result


    # function run
    # Description: Function that runs the host updater
    # Parameter: self, new_ids, trans_centroid_list, trans_d_zone_pts
    # Return value: None
    def run(self, new_ids, trans_centroid_list, trans_d_zone_pts):
        """ Runs the host updater """

        # Initialize grid template
        self.__grid_draw.initialize_grid( \
            (constants.B_EYE_VIEW_DIM[2], constants.B_EYE_VIEW_DIM[7]), \
            constants.GRID_DIV, \
            trans_d_zone_pts)

        # Generate grid data
        grid_data = self.__generate_grid_data(new_ids, trans_centroid_list)

        # Get byte code Bird's Eye grid image with centroids
        grid_byte_img = self.__grid_draw.get_b_eye_grid_img(grid_data)

        # Send updated grid image to mobile
        # Check if the sending process fails
        if constants.RETURN_OK != self.__send_update_to_host(grid_byte_img):
            self.__common.post_message(self.name, "Update sending failed!")


    # function __generate_grid_data
    # Description: Function that generates the data for grid
    # Parameter: self, new_ids, new_centroids
    # Return value: data
    def __generate_grid_data(self, new_ids, new_centroids):
        """ Generate grid data """

        ids_len = len(new_ids)          # Get id count
        data = []                       # Holds grid data

        # Check each id if they have alert
        for index in range(0, ids_len, 1):

            alert_flag = False          # Holds alert flag. Initial value is False

            # Verify alert flag
            alert_flag = self.__monitoring.has_alert_by_id(new_ids[index])

            # Append new centroid details and alert flag
            data_item = (new_centroids[index], alert_flag)
            data.append(data_item)

        # Return collected centroids and alert flags
        return data
