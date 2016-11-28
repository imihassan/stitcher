"""
Module for defining wrappers to OpenCV incoming feeds.
"""
from __future__ import absolute_import, division, print_function
from abc import ABCMeta, abstractmethod
import time
import sys
import imutils
import cv2
from app.stitcher.correction.corrector import correct_distortion
from .textformatter import TextFormatter

class Feed(object):
    """
    Abstract feed class for representing a feed.
    """
    __metaclass__ = ABCMeta

    @abstractmethod
    def has_next(self):
        """
        Returns True if feed has remaining frames.
        """
        pass

    @abstractmethod
    def get_next(self, resize, correct):
        """
        Returns the next frame from feed.
        """
        pass

    @abstractmethod
    def is_valid(self):
        """
        Returns True if feed is valid.
        """
        pass

    @abstractmethod
    def close(self):
        """
        Closes feed object.
        """
        pass

class CameraFeed(Feed):
    """
    Wrapper class for incoming camera feed.
    """
    def __init__(self, feed_index, width=640, height=480, fps=30):
        self.feed_index = feed_index
        self.camera_feed = cv2.VideoCapture(feed_index)
        self.width = width
        self.height = height
        self.fps = fps
        self.frame_duration = 1.0 / fps

    def is_valid(self):
        """
        Declares whether or not the CameraFeed instance is a valid feed.
        Similar in meaning to has_next(self), but with output.


        What is coming: checking if the frame is all black or close to all black.
        If it isn't, return true (in addition to the current feed validity test)
        """
        frame_indicator = self.camera_feed.grab()

        # If a frame is read, print message and return True.
        if frame_indicator:
            msg = "Index {0} is valid {1}".format(
                TextFormatter.color_text(str(self.feed_index), "magenta"),
                TextFormatter.get_check())
            print(msg)
            self.camera_feed.release()
            self.camera_feed = cv2.VideoCapture(self.feed_index)
            return True
        else:
            msg = "Index {0} is invalid {1}".format(
                TextFormatter.color_text(str(self.feed_index), "magenta"),
                TextFormatter.get_xmark())
            print(msg)
            return False

    def has_next(self):
        """
        Declares if the CameraFeed has a next frame.
        """
        return self.camera_feed.grab()

    def retrieve_next(self):
        """
        Retrieves the previously grabbed frame.
        Usually called after has_next()
        """
        return self.camera_feed.retrieve()


    def get_next(self, resize=True, correct=True):
        """
        Gets the next frame in the CameraFeed. If resize is True, resizes frame.
        If correct is True, corrects distortion.
        """
        start_time = time.time()
        frame = self.camera_feed.read()[1]
        if correct:
            frame = correct_distortion(frame)
        if resize:
            frame = imutils.resize(frame, width=self.width)
        end_time = time.time()
        elapsed_time = end_time - start_time
        time_left = self.frame_duration - elapsed_time

        """
        This takes into account experimentally determined average time.time()
        fps residual of 0.072906 for 30 fps.
        """
        time_left_adjusted = time_left - 0.072906
        if time_left_adjusted > 0:
            time.sleep(time_left_adjusted)
        return frame

    def ramp(self, num_frames=30):
        """ Ramps the camera feed to prepare for capture and data relay. """
        try:
            for _ in xrange(num_frames):
                self.get_next()
        except NameError:
            for _ in range(num_frames):
                self.get_next()

    def set_fps(self, fps):
        """
        Sets the desired fps for the CameraFeed
        """
        self.fps = fps

    def get_fps(self):
        """
        Gets the fps of the CameraFeed.
        """
        return self.camera_feed.get(5)

    def show(self, correct=True):
        """
        Shows a resized version of the CameraFeed.
        """
        if self.is_valid():
            while self.has_next():
                if correct:
                    frame = self.get_next()
                else:
                    frame = self.get_next(True, False)
                title = "Camera Feed %s" % self.feed_index
                cv2.imshow(title, frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
            TextFormatter.print_info("Cleaning up the camera feed.")
            self.close()
            cv2.destroyAllWindows()
            cv2.waitKey(1)

    def close(self):
        """
        Closes the CameraFeed.
        """
        self.camera_feed.release()

class VideoFeed(Feed):
    """ Wrapper class for video feed. """
    def __init__(self, path, width=640, height=480):
        self.path = path
        self.video_feed = cv2.VideoCapture(path)
        self.width = width
        self.height = height

    def is_valid(self):
        """
        Declares whether or not the VideoFeed instance is a valid feed.
        Similar in meaning to has_next(self), but with output.
        """
        frame_indicator = self.video_feed.grab()

        if frame_indicator:
            msg = "Video file {0} is valid {1}".format(
                TextFormatter.color_text(str(self.path), "magenta"),
                TextFormatter.get_check())
            # print(msg)
            sys.stderr.write(msg)
            self.video_feed.release()
            self.video_feed = cv2.VideoCapture(self.path)
            return True
        else:
            msg = "Video file {0} is invalid {1}".format(
                TextFormatter.color_text(str(self.path), "magenta"),
                TextFormatter.get_xmark())
            # print(msg)
            sys.stderr.write(msg)
            return False

    def has_next(self):
        """
        Declares if the VideoFeed has a next frame.
        """
        return self.video_feed.grab()

    def get_next(self, resize=True, correct=True):
        """
        Gets the next frame in the CameraFeed. If resize is True, resizes frame.
        If correct is True, corrects distortion.
        """
        frame = self.video_feed.read()[1]
        if correct:
            frame = correct_distortion(frame)
        if resize:
            frame = imutils.resize(frame, width=self.width)
        return frame

    def show(self, correct=True):
        """
        Shows a resized version of the CameraFeed.
        """
        if self.is_valid():
            while self.has_next():
                if correct:
                    frame = self.get_next()
                else:
                    frame = self.get_next(True, False)
                title = "Video Feed"
                cv2.imshow(title, frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord("q"):
                    break
            TextFormatter.print_info("Cleaning up the camera feed.")
            self.close()
            cv2.destroyAllWindows()
            cv2.waitKey(1)

    def close(self):
        """
        Closes the VideoFeed.
        """
        self.video_feed.release()
