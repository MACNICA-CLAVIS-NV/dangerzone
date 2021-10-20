""" Alarm Buzzer """
#!/usr/bin/env python3

# Add license here

# Add imports here
import time
from common import constants
from RPi import GPIO

#pylint: disable=wrong-import-position

# class Buzzer
# Description: Class that alarms buzzer
# Parameter: None
# Return value: None
class Buzzer:
    """ Alarm buzzer """

    __buzzer = None         # Class instance

    # function get_instance
    # Description: Function that returns the class instance
    # Parameter: None
    # Return value: Buzzer.__buzzer
    @staticmethod
    def get_instance():
        """ Static access method. """

        # Check if the class is not yet initialized
        if Buzzer.__buzzer is None:

            # Call class constructor
            Buzzer()

        # Return class instance
        return Buzzer.__buzzer


    # function __init__
    # Description: Class constructor
    # Parameter: self
    # Return value: None
    def __init__(self):
        """ Virtually private constructor. """

        # Check if the class is not yet initialized
        if Buzzer.__buzzer is None:

            # Initialize class instance
            Buzzer.__buzzer = self

            # BOARD pin-numbering scheme
            GPIO.setmode(GPIO.BOARD)

            # Setup gpio output to high to start buzzer alarm
            GPIO.setup(constants.BUZZ_PIN, GPIO.OUT, initial=GPIO.LOW)


    #function alarm_buzz
    #Description: Function that triggers buzzer alarm
    #Parameter: self
    #Return value: None
    @classmethod
    def alarm_buzz(cls):
        """ Trigger buzzer alarm """

        try:

             # Check if the buzzer alarm is off
            if not GPIO.input(constants.BUZZ_PIN):

                # Activate buzzer alarm
                print(f"Outputting {GPIO.HIGH} to pin {constants.BUZZ_PIN}")
                GPIO.output(constants.BUZZ_PIN, GPIO.HIGH)

        except KeyboardInterrupt:
            pass


    #function alarm_off
    #Description: Function that turns off the buzzer alarm
    #Parameter: None
    #Return value: None
    @classmethod
    def alarm_off(cls):
        """ Turns off buzzer alarm """

        try:

            # Check if the buzzer is alarming
            if GPIO.input(constants.BUZZ_PIN):

                # Deactivate buzzer alarm
                print(f"Outputting {GPIO.LOW} to pin {constants.BUZZ_PIN}")
                GPIO.output(constants.BUZZ_PIN, GPIO.LOW)

        except KeyboardInterrupt:
            pass


    #function cleanup
    #Description: Function for GPIO cleanup
    #Parameter: self
    #Return value: None
    @classmethod
    def clean_up(cls):
        """ GPIO cleanup """

        # Clean up
        GPIO.cleanup()
