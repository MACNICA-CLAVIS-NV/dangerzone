""" HDDZIDS Constants """
###############################################################################################
# scripts/deep_stream.py constants
###############################################################################################

OBJ_CLASS_ID_PERSON = 2                               # Class id for object "Person"

FRAME_WIDTH = 1000                                    # Pipeline - frame width
FRAME_HEIGHT = 600                                    # Pipeline - frame heigh

B_EYE_CALIB_INDEX = 0                                 # Index for Bird's Eye calibration
D_ZONE_CALIB_INDEX = 1                                # Index for Danger Zone calibration

B_EYE_VIEW_DIM = [0, 0, 200, 0, 200, 300, 0, 300]     # Bird's Eye View dimension

# Calibration result status
CALIB_STAT_DEFAULT = 1                                # Default: Not yet started
CALIB_STAT_NORMAL = 0                                 # Normal: Calibration process is successful
CALIB_STAT_ERROR = -1                                 # Error: Calibration process failed

###############################################################################################
# common/common.py constants
###############################################################################################

CALIBRATION_DATA_PATH = "data/calibration.txt"  # Calibration file path
CALIBRATION_COUNT = 2                              # Count: Bird's Eye and Danger zone calibrations
CALIBRATION_VALUE_COUNT = 8                        # Count of calibration points

B_EYE_INPUT_FILE = "data/input_file.txt"        # Bird's Eye Converter - Input file path
B_EYE_OUTPUT_FILE = "data/output_file.txt"      # Bird's Eye Converter - Output file path

FILE_ENCODING = 'utf-8'

###############################################################################################
# scripts/tracker.py constants
###############################################################################################

UPDATE_TIMEOUT = 30                                # No update time out
NO_INDEX = -1                                      # Not existing index

###############################################################################################
# scripts/monitoring.py constants
###############################################################################################

D_ZONE_RANGE = 50                                  # Danger Zone range
D_ZONE_DTIME_LIMIT = 5                             # Danger Zone dwell time limit

# Danger Zone dimension
D_ZONE_DIM = (0, 0, D_ZONE_RANGE, 0, D_ZONE_RANGE, D_ZONE_RANGE, 0, D_ZONE_RANGE)

###########################################################
# scripts/calibration_draw.py constants
###########################################################

CAM_CHANNEL = '/dev/video0'              # Camera channel
#CAM_CHANNEL = '0'              # Camera channel

# Screen calibration status
C_STAT_IDLE = 0                          # Screen calibration status: idle
C_STAT_INIT_STARTED = 1                  # Screen calibration status: start initialization
C_STAT_INIT_DONE = 2                     # Screen calibration status: initialization complete
C_STAT_CORNER_MOVE_START = 3             # Screen calibration status: start moving corner
C_STAT_CORNER_MOVE_END = 4               # Screen calibration status: done moving corner
C_STAT_SAVED = 5                         # Screen calibration status: saved

CORNER_PADDING = 5                       # Calibration corner padding
BOX_AREA_MIN = 30                        # Calibration box minimum area
B_EYE_COLOR = (0, 255, 0)  # Green       # Calibration bird's eye box color

###############################################################################################
# scripts/screen_calibration.py constants
###############################################################################################

# Calibration screen messages
B_EYE_CALIB_DISP_TEXT = "Camera View Calibration"
D_ZONE_CALIB_DISP_TEXT = "Danger Zone Calibration"
CALIB_DONE_DISP_TEXT = "Calibration is complete."
AREA_SELECT_DISP_TEXT = "Drag and Drop to select area..."
EXIT_DISP_TEXT = "Press 'q' to exit."
SAVE_DISP_TEXT = "Press 's' to save selection..."
INVALID_DISP_TEST = "Warning: Please adjust the corner points inside the bird's eye selected area"
OUT_DISP_TEST = "Warning: Please re-draw danger zone inside the bird's eye selected area" 
CALIB_FRAME = "Calibration"

B_EYE_RANGE = 50                               # Bird's Eye range
GRID_DIV = 20                                  # Grid cells division

# Calibration box coloring
CALIB_COLOR_B_EYE = (0, 255, 0)          # [Green] Calibration box color for Bird's Eye box
CALIB_COLOR_D_ZONE = (0, 0, 255)         # [Red] Calibration box color for Danger Zone box

# Host update and alert images coloring
GRID_COLOR = (255, 255, 255)             # [White] Bird's Eye View grid color
GRID_D_ZONE_COLOR = (0, 10, 255)         # [Red] Bird's Eye View grid - danger zone color
PTS_NORM_ZONE_COLOR = (180, 100, 0)      # [Blue] Centroid color - Normal
PTS_ALRT_ZONE_COLOR = (0, 10, 255)       # [Red] Centroid color - Alert

###############################################################################################
# scripts/host_updater.py constants
###############################################################################################

MOBILE_HOST = "192.168.230.88"                # Mqtt server ip address
MOBILE_PORT = 1883                            # Mqtt server port

MAX_TRY = 2                                   # Alert sending max try
RETURN_OK = 0                                 # Function return OK
RETURN_NG = 1                                 # Function return NOT GOOD

ON = 1                                        # ON flag
OFF = 0                                       # OFF flag

BUZZER_TIMEOUT = 5                            # Buzzer - alarm timeout
BUZZ_PIN = 12                                 # Buzzer - gpio pin

MSG_TOPIC_ALERT_DATA = "topic/msgData"        # Mqtt message topic for alert data
MSG_TOPIC_ALERT_IMAGE = "topic/msgImage"      # Mqtt message topic for alert image
MSG_TOPIC_HOST_UPDATE = "topic/grid"          # Mqtt message topic for host update image

C_NAME_ALERT_NOTIFY = "ALERT-NOTIFY"          # Class name for AlertNotify
C_NAME_HOST_UPDATER = "HOST-UPDATER"          # Class name for HostUpdater

USB_MODE = 0                                  # Camera USB mode
RPI_MODE = 1                                  # Camera Raspi mode
CAM_MODE = USB_MODE                           # Camera mode

V_CALIB_DEFAULT = -1                          # Calibration file is not yet checked
V_CALIB_OK = 0                                # Calibration file is ok
V_CALIB_NO_FILE = 1                           # Calibration file does not exists
V_CALIB_FILE_EMPTY = 2                        # Calibration file is empty
V_CALIB_NG_CONTENT = 3                        # Calibration file has invalid content

FRAME_SKIP = 0                                # Frame skip interval


# Result for checking if danger zone is valid
RES_D_ZONE_VALID = 0               # Valid danger zone selected area
RES_D_ZONE_OUT = -1                # Danger zone is outside the bird's eye box
RES_D_ZONE_INVALID = -2            # Portion of danger zone is outside the bird's eye box
