""" Tracker History """
#!/usr/bin/env python3

# Add license here

# Add imports here
from common import constants
#pylint: disable=wrong-import-position

# class Tracker
# Description: Class for tracking object detection history
# Parameter: None
# Return value: None
class Tracker:
    """ Tracker class """

    __tracker = None              # Tracker Class instance
    __tracker_id = []             # Holds the object ids
    __tracker_update = []         # Holds the update counter per object id
    __tracker_bbox = []           # Holds the bounding box per object id
    __tracker_centroid = []       # Holds the centroid per object id

    # function get_instance
    # Description: Functon to return the class instance
    # Parameter: None
    # Return value: __tracker
    @staticmethod
    def get_instance():
        """ Static access method. """

        # Check if not yet initialized
        if Tracker.__tracker is None:

            # Call the class constructor
            Tracker()

        # Return the class instance
        return Tracker.__tracker


    # function __init__
    # Description: Class constructor
    # Parameter: self
    # Return value: None
    def __init__(self):
        """ Virtually private constructor. """

        # Check if not yet initialized
        if Tracker.__tracker is None:

            # Initialize class instance
            Tracker.__tracker = self


    # function add
    # Description: Function that add new object details
    # Parameter: self, track_id, bbox
    # Return value: None
    def add(self, track_id, bbox):
        """" Add new object details """

        # Get the index of the track id if already existing
        index = self.get_index(track_id)

        # Track id is not existing
        if constants.NO_INDEX >= index:

            # Add the details for new object
            self.__tracker_id.append(track_id)
            self.__tracker_bbox.append(bbox)
            self.__tracker_centroid.append(self.__compute_centroid(bbox))
            self.__tracker_update.append(0)

        # Track id is existing
        else:

            # Update the details of the existing object
            self.__tracker_bbox[index] = bbox
            self.__tracker_centroid[index] = self.__compute_centroid(bbox)
            self.__tracker_update[index] = 0


    # function __compute_centroid
    # Description: Function that computes centroid
    # Parameter: self, bbox
    # Return value: centroid
    @classmethod
    def __compute_centroid(cls, bbox):
        """ Compute centroid """

        # Set the centroid width and height
        width = int(bbox.width / 2 + 0.5)
        height = bbox.height

        # Set the centroid x and y coordinates
        centroid = (int(bbox.left + width), int(bbox.top + height))

        # Returns computed centroid
        return centroid


    # function get_centroid_list
    # Description: Function that returns the centroid list
    # Parameter: self
    # Return value: __tracker_centroid
    def get_centroid_list(self):
        """ Returns the centroid list """

        return self.__tracker_centroid


    # function get_annotator_data
    # Description: Function that returns the data for annotation
    # Parameter: self, alerts
    # Return value: data
    def get_annotator_data(self, alerts):
        """ Returns annotation data """

        data = []       # Holds data for annotation

        # Check each alert
        for alert in alerts:

            # Set alert track id
            track_id = alert[0]

            # Get index
            index = self.get_index(track_id)

            # Index exists
            if index >= 0:

                # Set bounding box and centroid
                data.append((self.__tracker_bbox[index], self.__tracker_centroid[index]))


        # Return bounding box and centroid
        return data


    # function get_id_list
    # Description: Function that returns the track id list
    # Parameter: self
    # Return value: __tracker_id
    def get_id_list(self):
        """ Returns the track id list """

        return self.__tracker_id


    # function get_new_list
    # Description: Function that returns the current detections
    # Parameter: self
    # Return value: new_ids, new_centroids
    def get_new_list(self):
        """ Returns current detections: ids and centroids """

        update_len = len(self.__tracker_update)    # Set tracker count

        new_ids = []                               # Holds new ids
        new_centroids = []                         # Holds new centroids

        # Return if the tracker count is 0
        if update_len > 0:

            # Check each tracker
            for index in range(0, update_len, 1):

                # Trackers with 1 or less update counter are new data
                if self.__tracker_update[index] <= 1:

                    # Append ids and centroids
                    new_ids.append(self.__tracker_id[index])
                    new_centroids.append(self.__tracker_centroid[index])

        # Return ids and centroids of new data
        return new_ids, new_centroids


    # function get_index
    # Description: Function that returns the index based on track id
    # Parameter: self, track_id
    # Return value: result
    def get_index(self, track_id):
        """ Get track id index """

        result = -1                          # Holds the result index
        track_len = len(self.__tracker_id)   # Get the current number of existing tracker id

        # Check each tracker
        for index in range(0, track_len, 1):

            # Check if the track id has record
            if self.__tracker_id[index] == track_id:

                # Set index as the result
                result = index

                # Exit the loop
                break

        # Return the index as result
        return result


    # function update
    # Description: Function that maintains the active tracker
    # Parameter: self
    # Return value: None
    def update(self):
        """ Maintain active tracker """

        # Remove tracker that exceeds the update timeout
        tracker_max_index = len(self.__tracker_id) - 1
        for index in range(tracker_max_index, -1, -1):

            self.__tracker_update[index] += 1
            if self.__tracker_update[index] >= constants.UPDATE_TIMEOUT:
                del self.__tracker_id[index]
                del self.__tracker_update[index]
                del self.__tracker_bbox[index]
                del self.__tracker_centroid[index]
