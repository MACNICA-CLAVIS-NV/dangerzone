""" DeepStream - Metadata process """
#!/usr/bin/env python3

################################################################################
# Copyright (c) 2020, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
################################################################################

import sys
import math
import cv2
import numpy as np
import gi
gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst
#import pyds
from common.is_aarch_64 import is_aarch64
from common.bus_call import bus_call
from common.common import Common
from common import constants
from plugins.screen_calibration import ScreenCalibration
from scripts.tracker import Tracker
from scripts.monitoring import Monitoring
from scripts.host_updater import HostUpdater
from scripts.annotator import Annotator
from scripts.alert_notify import AlertNotify
from scripts.buzzer import Buzzer
import pyds
#pylint: disable=wrong-import-position

# class DeepStream
# Description: Class for DeepStream processes
# Parameter: None
# Return value: None
class DeepStream:
    """ DeepStream main processes """

    __deep_stream = None                                # DeepStream Class instance
    __is_first_frame = True                             # Holds the first frame flag
    __calibrations = None                               # Holds calibration result:
                                                        #      [0] - Bird's Eye View Calibration
                                                        #      [1] - Danger Zone Calibration
    __calibration_stat = constants.CALIB_STAT_DEFAULT   # Holds the calibration status

    __calibration_mode = constants.OFF

    __has_image = False

    __frame_number = 0

    __skip_frame_cnt = 0
    __skipped_cnt = 0

    # function get_instance
    # Description: Functon to return the class instance
    # Parameter: None
    # Return value: __deep_stream
    @staticmethod
    def get_instance():
        """ Static access method. """

        # Check if not yet initialized
        if DeepStream.__deep_stream is None:

            # Call the class constructor
            DeepStream()

        # Return the class instance
        return DeepStream.__deep_stream


    # function __init__
    # Description: Class constructor
    # Parameter: self
    # Return value: None
    def __init__(self):
        """ Virtually private constructor. """

        # Check if not yet initialized
        if DeepStream.__deep_stream is None:

            DeepStream.__deep_stream = self    # Set DeepStream class instance

    # function __metadata_process
    # Description: Function to process pipeline data
    # Parameter: self, pad, info, u_data
    # Return value: Gst.PadProbeReturn
    def __metadata_process(self, _pad, info, _u_data):
        """ Metadata process """

        # Get buffer from gst
        gst_buffer = info.get_buffer()
        if not gst_buffer:
            print("Unable to get GstBuffer ")
            result = None
        else:

            # Retrieve batch metadata from the gst_buffer
            # Note that pyds.gst_buffer_get_nvds_batch_meta() expects the
            # C address of gst_buffer as input, which is obtained with hash(gst_buffer)
            batch_meta = pyds.gst_buffer_get_nvds_batch_meta(hash(gst_buffer))
            l_frame = batch_meta.frame_meta_list

            # Check each frame from list
            while l_frame is not None:

                # Do not proceed if the calibration process failed
                if self.__calibration_stat == constants.CALIB_STAT_ERROR:
                    break

                try:
                    # Get frame metadata
                    frame_meta = pyds.NvDsFrameMeta.cast(l_frame.data)

                except StopIteration:
                    break

                # Getting Image data using nvbufsurface
                # the input should be address of buffer and batch_id
                n_frame = pyds.get_nvds_buf_surface(hash(gst_buffer), 0)

                #convert python array into numpy array format.
                cam_view_img = np.array(n_frame, copy=True, order='C')

                #covert the array into cv2 default color format
                cam_view_img = cv2.cvtColor(cam_view_img, cv2.COLOR_RGBA2BGRA)

                # Ongoing calibration
                if self.__calibration_mode == constants.ON:

                    # Set frame image for screen calibration
                    ScreenCalibration.get_instance().set_frame(cam_view_img)

                    try:
                        l_frame = l_frame.next
                    except StopIteration:
                        break
                    else:
                        continue

                else:

                    # Set frame image in our annotator
                    Annotator.get_instance().set_frame(cam_view_img)

                    # Got frame image
                    self.__has_image = True

                # Increase and display the frame number
                self.__frame_number += 1

                print(f"Frame number: {self.__frame_number}")

                self.__skip_frame_cnt += 1
                if self.__skip_frame_cnt % 2 == 0:

                    self.__skip_frame_cnt = 0

                    self.__skipped_cnt += 1
                    if self.__skipped_cnt > constants.FRAME_SKIP:
                        self.__skipped_cnt = 0
                        self.__skip_frame_cnt = 0
                    else:
                        self.__skip_frame_cnt -= 1

                        try:
                            l_frame = l_frame.next
                        except StopIteration:
                            break
                        else:
                            continue

                # Get object list
                l_obj = frame_meta.obj_meta_list
                # Check object list and get object count
                obj_count = self.__process_object_list(l_obj)

                # Call tracker update. To check and remove unused tracker
                Tracker.get_instance().update()

                # First frame process
                self.__process_first_frame()

                # Main process
                self.__process_main(obj_count)

                try:
                    l_frame = l_frame.next
                except StopIteration:
                    break

            # Pad probe return normally
            result = Gst.PadProbeReturn.OK

        # Return process result
        return result


    # function __process_object_list
    # Description: Function to process object list
    # Parameter: cls, l_obj
    # Return value: obj_count
    @classmethod
    def __process_object_list(cls, l_obj):
        """ Proces object list """

        obj_count = 0      # Holds detection count

        # Check each object from list
        while l_obj is not None:

            try:
                # Get the detected object metadata
                obj_meta = pyds.NvDsObjectMeta.cast(l_obj.data)

                # Check if the detected object is "Person"
                if obj_meta.class_id == constants.OBJ_CLASS_ID_PERSON:

                    # Add tracker info: track id, bounding box details
                    Tracker.get_instance().add(obj_meta.object_id, obj_meta.rect_params)

                    # Add object count
                    obj_count += 1

                l_obj = l_obj.next

            except StopIteration as stop_iteration:
                raise StopIteration from stop_iteration

        return obj_count


    # function __process_first_frame
    # Description: Function that handles the first frame process
    # Parameter: self
    # Return value: None
    def __process_first_frame(self):
        """ First frame process """

        # Check if first frame
        if self.__is_first_frame:
            self.__is_first_frame = False

            # Extract calibrations from calibration file
            self.__calibration_stat = self.__extract_calibrations()

            # Calibrations are extracted successfully
            if self.__calibration_stat is not None:

                # Initialize danger zone transformation
                Monitoring.get_instance().initialize_d_zone(constants.B_EYE_VIEW_DIM, \
                    self.__calibrations[constants.B_EYE_CALIB_INDEX], \
                    self.__calibrations[constants.D_ZONE_CALIB_INDEX])


    # function __process_main
    # Description: Function that handles the main process
    # Parameter: self, obj_count
    # Return value: None
    def __process_main(self, obj_count):
        """ Main process """

        # Get new detection objects: ids and centroids
        new_ids, new_centroids = Tracker.get_instance().get_new_list()

        # Get the list of transformed centroid
        trans_centroid_list = self.__get_b_eye_centroids(new_centroids)

        # Get transformed Danger zone corner points
        trans_d_zone = Monitoring.get_instance().get_trans_d_zone()

        # Bird's Eye View - Update sending
        HostUpdater.get_instance().run(new_ids, trans_centroid_list, trans_d_zone)

        # detected person is not none and the calibrations are extracted
        if obj_count > 0 and self.__calibration_stat is not None and self.__has_image:

            # Danger zone monitoring
            Monitoring.get_instance().run(new_ids, trans_centroid_list)

            # Get alerts
            alerts = Monitoring.get_instance().get_alerts()

            alerts_count = len(alerts)

            # If alerts is not empty, it means there are persons which
            # having dwell time inside the Danger zone that exceeded the allowable time.
            if alerts_count > 0:

                # Alert details: Object id, Dwell time, Alert flag, Alert time
                # Get list of bbox and centroid of all alert
                annotator_data = Tracker.get_instance().get_annotator_data(alerts)

                if len(annotator_data) > 0:

                    # Annotate frame
                    frame = Annotator.get_instance().annotate(annotator_data)

                    # Add alert
                    AlertNotify.get_instance().add_alert(alerts[alerts_count - 1][0], \
                        alerts[alerts_count - 1][3], frame)

                    # Alarm buzzer
                    Buzzer.get_instance().alarm_buzz()

        # Send alert
        AlertNotify.get_instance().send_alert()

        # Check if there is alert
        if not Monitoring.get_instance().has_alert():

            # Turn off buzzer alarm
            Buzzer.get_instance().alarm_off()



    # function __extract_calibrations
    # Description: Function to extract calibrations from file
    # Parameter: self
    # Return value: calibration_stat
    def __extract_calibrations(self):
        """ Extract calibrations from file """

        # Get calibration details
        self.__calibrations = Common.get_instance().get_calibrations()

        # Calibration process failed
        if self.__calibrations is None:

            print("[INFO] Calibration is not yet done successfully. Unable to proceed.")

            # Set calibration status to error
            calibration_stat = constants.CALIB_STAT_ERROR

        # Calibration process is successful
        else:

            print("[INFO] Calibration is extracted successfully.")

            # Set calibration status to normal
            calibration_stat = constants.CALIB_STAT_NORMAL

        # Return the calibration process status
        return calibration_stat


    # function __get_b_eye_centroids
    # Description: Function to get the bird's eye centroids
    # Parameter: self, new_centroids
    # Return value: trans_centroid_list
    def __get_b_eye_centroids(self, new_centroids):
        """ Get the Bird's eye centroids """

        # Write details in the input file.
        # This input file will be read by Bird's Eye Converter plugin when executed
        Common.get_instance().write_b_eye_input_file(constants.B_EYE_VIEW_DIM, \
           self.__calibrations[constants.B_EYE_CALIB_INDEX], \
           new_centroids)

        # Run the Bird's Eye Converter plugin
        Common.get_instance().run_b_eye_converter()

        # Get the list of transformed centroid
        trans_centroid_list = Common.get_instance().read_b_eye_output_file()

        # Return the transformed centroid list
        return trans_centroid_list


    # function run
    # Description: Function that process the deepstream pipeline
    # Parameter: self, live_camera, stream_path
    # Return value: process_result
    def run(self, live_camera, stream_path):
        """Deepstream function for detection and tracking"""

        has_element_err = False

        number_sources = 1
        # Standard GStreamer initialization
        GObject.threads_init()
        Gst.init(None)
        # Create gstreamer elements
        # Create Pipeline element that will form a connection of other elements
        print("Creating Pipeline \n ")
        pipeline = Gst.Pipeline()

        if not pipeline:
            sys.stderr.write(" Unable to create Pipeline \n")
            has_element_err = True
        if live_camera:
            if constants.RPI_MODE == constants.CAM_MODE:
                print("Creating Source \n ")
                source = Gst.ElementFactory.make("nvarguscamerasrc", "src-elem")
                if not source:
                    sys.stderr.write(" Unable to create Source \n")
                    has_element_err = True
            else:
                print("Creating Source \n ")
                source = Gst.ElementFactory.make("v4l2src", "usb-cam-source")
                if not source:
                    sys.stderr.write(" Unable to create Source \n")
                    has_element_err = True

                caps_v4l2src = Gst.ElementFactory.make("capsfilter", "v4l2src_caps")
                if not caps_v4l2src:
                    sys.stderr.write(" Unable to create v4l2src capsfilter \n")
                    has_element_err = True
                print("Creating Video Converter \n")
                # videoconvert to make sure a superset of raw formats are supported
                vidconvsrc = Gst.ElementFactory.make("videoconvert", "convertor_src1")
                if not vidconvsrc:
                    sys.stderr.write(" Unable to create videoconvert \n")
                    has_element_err = True
            # nvvideoconvert to convert incoming raw buffers to NVMM Mem (NvBufSurface API)
            nvvidconvsrc = Gst.ElementFactory.make("nvvideoconvert", "convertor_src2")
            if not nvvidconvsrc:
                sys.stderr.write(" Unable to create Nvvideoconvert \n")
                has_element_err = True
            caps_vidconvsrc = Gst.ElementFactory.make("capsfilter", "nvmm_caps")
            if not caps_vidconvsrc:
                sys.stderr.write(" Unable to create capsfilter \n")
                has_element_err = True
        else:
            # Source element for reading from the file
            print("Creating Source \n ")
            source = Gst.ElementFactory.make("filesrc", "file-source")
            if not source:
                sys.stderr.write(" Unable to create Source \n")
                has_element_err = True
            # Since the data format in the input file is elementary h264 stream,
            # we need a h264parser
            print("Creating H264Parser \n")
            h264parser = Gst.ElementFactory.make("h264parse", "h264-parser")
            if not h264parser:
                sys.stderr.write(" Unable to create h264 parser \n")
                has_element_err = True
            # Use nvdec_h264 for hardware accelerated decode on GPU
            print("Creating Decoder \n")
            decoder = Gst.ElementFactory.make("nvv4l2decoder", "nvv4l2-decoder")
            if not decoder:
                sys.stderr.write(" Unable to create Nvv4l2 Decoder \n")
                has_element_err = True
        # Create nvstreammux instance to form batches from one or more sources.
        streammux = Gst.ElementFactory.make("nvstreammux", "Stream-muxer")
        if not streammux:
            sys.stderr.write(" Unable to create NvStreamMux \n")
            has_element_err = True
        # Use nvinfer to run inferencing on decoder's output,
        # behaviour of inferencing is set through config file
        pgie = Gst.ElementFactory.make("nvinfer", "primary-inference")
        if not pgie:
            sys.stderr.write(" Unable to create pgie \n")
            has_element_err = True

        # Use nv-tracker to keep track of the detected objects
        tracker = Gst.ElementFactory.make("nvtracker", "NV-Tracker")
        if not tracker:
            sys.stderr.write(" Unable to create tracker \n")
            has_element_err = True

        # Add nvvidconv1 and filter1 to convert the frames to RGBA
        # which is easier to work with in Python.
        print("Creating nvvidconv1 \n ")
        nvvidconv1 = Gst.ElementFactory.make("nvvideoconvert", "convertor1")
        if not nvvidconv1:
            sys.stderr.write(" Unable to create nvvidconv1 \n")
            has_element_err = True
        print("Creating filter1 \n ")
        caps1 = Gst.Caps.from_string("video/x-raw(memory:NVMM), format=RGBA")
        filter1 = Gst.ElementFactory.make("capsfilter", "filter1")
        if not filter1:
            sys.stderr.write(" Unable to get the caps filter1 \n")
            has_element_err = True
        #filter1.set_property("caps", caps1)
        print("Creating tiler \n ")
        tiler = Gst.ElementFactory.make("nvmultistreamtiler", "nvtiler")
        if not tiler:
            sys.stderr.write(" Unable to create tiler \n")
            has_element_err = True
        print("Creating nvvidconv \n ")
        nvvidconv = Gst.ElementFactory.make("nvvideoconvert", "convertor")
        if not nvvidconv:
            sys.stderr.write(" Unable to create nvvidconv \n")
            has_element_err = True
        print("Creating nvosd \n ")
        nvosd = Gst.ElementFactory.make("nvdsosd", "onscreendisplay")
        if not nvosd:
            sys.stderr.write(" Unable to create nvosd \n")
            has_element_err = True
        print("Creating Fake sink \n")
        # sink = Gst.ElementFactory.make("nveglglessink", "nvvideo-renderer")
        sink = Gst.ElementFactory.make("fakesink", "fakesink")
        if not sink:
            sys.stderr.write(" Unable to create fake sink \n")
            has_element_err = True
        print("Playing file %s " %stream_path)


        if has_element_err:

            process_result = False

        else:

            if live_camera:
                if constants.RPI_MODE == constants.CAM_MODE:
                    source.set_property('bufapi-version', True)
                else:
                    source.set_property('device', stream_path)
                    caps_v4l2src.set_property('caps', \
                        Gst.Caps.from_string("video/x-raw, framerate=30/1"))
                caps_vidconvsrc.set_property('caps', \
                    Gst.Caps.from_string("video/x-raw(memory:NVMM)"))
            else:
                source.set_property('location', stream_path)

            streammux.set_property('width', 1920)
            streammux.set_property('height', 1080)
            streammux.set_property('batch-size', 1)
            streammux.set_property('batched-push-timeout', 4000000)

            tiler_rows = int(math.sqrt(number_sources))
            tiler_columns = int(math.ceil((1.0*number_sources)/tiler_rows))
            tiler.set_property("rows", tiler_rows)
            tiler.set_property("columns", tiler_columns)
            tiler.set_property("width", constants.FRAME_WIDTH)
            tiler.set_property("height", constants.FRAME_HEIGHT)

            if is_aarch64():
                sink.set_property("sync", 0)
            else:
                sink.set_property("sync", 1)

                # Use CUDA unified memory in the pipeline so frames
                # can be easily accessed on CPU in Python.
                mem_type = int(pyds.NVBUF_MEM_CUDA_UNIFIED)
                streammux.set_property("nvbuf-memory-type", mem_type)
                nvvidconv.set_property("nvbuf-memory-type", mem_type)
                nvvidconv1.set_property("nvbuf-memory-type", mem_type)
                tiler.set_property("nvbuf-memory-type", mem_type)

            filter1.set_property("caps", caps1)

            #Set properties of pgie
            pgie.set_property('config-file-path', "dstest1_pgie_config.txt")

            #Set nv-tracker properties
            tracker.set_property('ll-lib-file', \
                '/opt/nvidia/deepstream/deepstream-6.0/lib/libnvds_nvdcf.so')
            tracker.set_property('tracker-width', 20*32)
            tracker.set_property('tracker-height', 20*32)
            tracker.set_property('enable-past-frame', 1)
            tracker.set_property('enable-batch-process', 1)
            tracker.set_property('ll-config-file', 'config/tracker_config.yml')

            print("Adding elements to Pipeline \n")
            pipeline.add(source)
            if live_camera:
                if constants.RPI_MODE != constants.CAM_MODE:
                    pipeline.add(caps_v4l2src)
                    pipeline.add(vidconvsrc)
                pipeline.add(nvvidconvsrc)
                pipeline.add(caps_vidconvsrc)
            else:
                pipeline.add(h264parser)
                pipeline.add(decoder)
            pipeline.add(streammux)
            pipeline.add(pgie)
            pipeline.add(tracker)
            pipeline.add(tiler)
            pipeline.add(nvvidconv)
            pipeline.add(filter1)
            pipeline.add(nvvidconv1)
            pipeline.add(nvosd)
            pipeline.add(sink)

            # we link the elements together
            # file-source -> h264-parser -> nvh264-decoder ->
            # nvinfer -> nvvidconv -> nvosd -> video-renderer
            print("Linking elements in the Pipeline \n")
            if live_camera:
                if constants.RPI_MODE == constants.CAM_MODE:
                    source.link(nvvidconvsrc)
                else:
                    source.link(caps_v4l2src)
                    caps_v4l2src.link(vidconvsrc)
                    vidconvsrc.link(nvvidconvsrc)
                nvvidconvsrc.link(caps_vidconvsrc)
            else:
                source.link(h264parser)
                h264parser.link(decoder)

            sinkpad = streammux.get_request_pad("sink_0")
            if not sinkpad:
                sys.stderr.write(" Unable to get the sink pad of streammux \n")
            if live_camera:
                srcpad = caps_vidconvsrc.get_static_pad("src")
            else:
                srcpad = decoder.get_static_pad("src")
            if not srcpad:
                sys.stderr.write(" Unable to get source pad of decoder \n")
            srcpad.link(sinkpad)
            streammux.link(pgie)
            pgie.link(tracker)
            tracker.link(nvvidconv1)
            nvvidconv1.link(filter1)
            filter1.link(tiler)
            tiler.link(nvvidconv)
            nvvidconv.link(nvosd)
            nvosd.link(sink)

            # create and event loop and feed gstreamer bus mesages to it
            loop = GObject.MainLoop()

            bus = pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect("message", bus_call, loop)

            # Lets add probe to get informed of the meta data generated, we add probe to
            # the sink pad of the osd element, since by that time, the buffer would have
            # had got all the metadata.
            tiler_sink_pad = nvvidconv.get_static_pad("sink")
            if not tiler_sink_pad:
                sys.stderr.write(" Unable to get src pad \n")
            else:
                tiler_sink_pad.add_probe(Gst.PadProbeType.BUFFER, self.__metadata_process, 0)

            print("Starting pipeline \n")
            # start play back and listed to events
            pipeline.set_state(Gst.State.PLAYING)

            calib_result = Common.get_instance().check_calibration_file()

            if calib_result != constants.V_CALIB_OK:

                self.__calibration_mode = constants.ON
                ScreenCalibration.get_instance().run()
                self.__calibration_mode = constants.OFF

            # start play back and listed to events
            try:
                loop.run()
            except KeyboardInterrupt:
                pass

            # cleanup
            pipeline.set_state(Gst.State.NULL)

            process_result = True

        return process_result
