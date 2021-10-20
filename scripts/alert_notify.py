""" Alert Notify """
#!/usr/bin/env python3

# Add license here

# Add imports here
import socket
import paho.mqtt.client as mqtt
from common import constants
from common.common import Common
#pylint: disable=wrong-import-position


# class AlertNotify
# Description: Class that notifies the mobile host with alert
# Parameter: None
# Return value: None
class AlertNotify:
    """ Notify mobile host with alert """

    __alarm_notify = None   # AlertNotify class instance
    __common = None         # Common class instance

    # Alert pool
    __alert_topics = []     # Holds alert topic
    __alert_messages = []   # Holds alert messages
    __alert_try = []        # Holds alert try counter

    # function get_instance
    # Description: Functon to return the class instance
    # Parameter: None
    # Return value: __alarm_notify
    @staticmethod
    def get_instance():
        """ Static access method. """

        # Check if not yet initialized
        if AlertNotify.__alarm_notify is None:

            # Call the class constructor
            AlertNotify()

        # Return the class instance
        return AlertNotify.__alarm_notify


    # function __init__
    # Description: Class constructor
    # Parameter: self
    # Return value: None
    def __init__(self):
        """ Virtually private constructor. """

        # Check if not yet initialized
        if AlertNotify.__alarm_notify is None:

            AlertNotify.__alarm_notify = self            # Initialize AlertNotify class instance
            self.__common = Common.get_instance()        # Initialize Common class instance
            self.name = constants.C_NAME_ALERT_NOTIFY    # Set class name


    # function __send_alert_to_host
    # Description: Function that publish alert data and image
    # Paremeter: self, topic, message
    # Return value: result
    def __send_alert_to_host(self, topic, message):
        """ Send alert message to mobile host """


        client = mqtt.Client()    # Get mqtt client instance

        try:

            # Connect mqtt client
            client.connect(constants.MOBILE_HOST, constants.MOBILE_PORT, 60)

            # Publish message
            client.publish(topic, message)

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

        # Published successfully
        else:

            # Notification when the message sent is alert data
            if constants.MSG_TOPIC_ALERT_DATA == topic:

                self.__common.post_message(self.name, \
                    f"Alert data was sent: [TOPIC:{topic}][MSG:{message}].")

            # Notification when the message sent is alert image
            elif constants.MSG_TOPIC_ALERT_IMAGE == topic:

                self.__common.post_message(self.name, "Alert image was sent.")

            # Result is successful
            result = constants.RETURN_OK

        finally:

            # Disconnect client
            client.disconnect()

        # Return process result
        return result


    # function add_alert
    # Description: Function that adds alert details into the alert pool
    # Paremeter: self, object_id, alert_time, image
    # Return value: None
    def add_alert(self, object_id, alert_time, image):
        """ Add new alert into the alert pool """

        # Add alert message
        self.__alert_topics.append(constants.MSG_TOPIC_ALERT_DATA)
        message = f"{object_id}/{alert_time}"
        self.__alert_messages.append(message)
        self.__alert_try.append(0)

        # Add alert image
        self.__alert_topics.append(constants.MSG_TOPIC_ALERT_IMAGE)
        message = image
        self.__alert_messages.append(image)
        self.__alert_try.append(0)


    # function send_alert
    # Description: Function that monitors the send try counter after sending an alert
    # Paremeter: self
    # Return value: None
    def send_alert(self):
        """ Send alert while max try counter is not yet reached """

        # Check if the alert list has alert left
        if len(self.__alert_topics) > 0:

            index = 0              # First index

            # check if max retry is not yet reached
            if constants.MAX_TRY > self.__alert_try[index]:

                self.__common.post_message(self.name, f"Send count: {self.__alert_try[index]}")

                # Send alert message to mobile host
                result = self.__send_alert_to_host(
                    self.__alert_topics[index],
                    self.__alert_messages[index]
                )

                # Check if send result is not good
                if constants.RETURN_NG == result:

                    # Add try count
                    self.__alert_try[index] += 1

                    # Check if max try has been reached
                    if constants.MAX_TRY == self.__alert_try[index]:

                        # Delete alert
                        self.__pop_alert()

                # Successfull sending
                else:

                    # Delete alert
                    self.__pop_alert()

            # Try counter reached limit
            else:

                # Delete alert
                self.__pop_alert()


    # function __pop_alert
    # Description: Function that pops the first element from alert pool
    # Paremeter: self
    # Return value: None
    def __pop_alert(self):
        """ Pops alert from alert pool """

        # Delete alert
        index = 0
        del self.__alert_topics[index]
        del self.__alert_messages[index]
        del self.__alert_try[index]
