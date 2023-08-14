#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  20 02:07:13 2019

@author: prabhakar
"""
# import necessary argumnets 
import gi
import cv2
import argparse


import pyrealsense2 as rs
import numpy as np

# import required library like Gstreamer and GstreamerRtspServer
gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject

# Sensor Factory class which inherits the GstRtspServer base class and add
# properties to it.
class SensorFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self, **properties):
        super(SensorFactory, self).__init__(**properties)
        # self.cap = cv2.VideoCapture(opt.device_id)
        self.number_frames = 0
        self.fps = opt.fps
        self.duration = 1 / self.fps * Gst.SECOND  # duration of a frame in nanoseconds
        # self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
        #                      'caps=video/x-raw,format=BGR,width={},height={},framerate={}/1 ' \
        #                      '! videoconvert ! video/x-raw,format=I420 ' \
        #                      '! x264enc speed-preset=ultrafast tune=zerolatency ' \
        #                      '! rtph264pay config-interval=1 name=pay0 pt=96' \
        #                      .format(opt.image_width, opt.image_height, self.fps)

        self.pipeline = rs.pipeline()
        config = rs.config()
        # Get device product line for setting a supporting resolution
        pipeline_wrapper = rs.pipeline_wrapper(self.pipeline)
        pipeline_profile = config.resolve(pipeline_wrapper)
        self.device = pipeline_profile.get_device()
        device_product_line = str(self.device.get_info(rs.camera_info.product_line))
        found_rgb = False
        for s in self.device.sensors:
            if s.get_info(rs.camera_info.name) == 'RGB Camera':
                found_rgb = True
                break
        if not found_rgb:
            print("The demo requires Depth camera with Color sensor")
            exit(0)

        config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)

        if device_product_line == 'L500':
            config.enable_stream(rs.stream.color, 960, 540, rs.format.bgr8, 30)
            self.width = 960
            self.height = 540
        else:
            config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)
            self.width = 640
            self.height = 480
        # Start streaming
        self.pipeline.start(config)
        self.launch_string = 'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' \
                             'caps=video/x-raw,format=BGR,width={},height={},framerate={}/1 ' \
                             '! videoconvert ! video/x-raw,format=I420 ' \
                             '! x264enc speed-preset=ultrafast tune=zerolatency ' \
                             '! rtph264pay config-interval=1 name=pay0 pt=96' \
                             .format(self.width, self.height, self.fps)
        
    # method to capture the video feed from the camera and push it to the
    # streaming buffer.
    def on_need_data(self, src, length):
        if self.pipeline:
            frames = self.pipeline.wait_for_frames()
            if frames:
                # It is better to change the resolution of the camera 
                # instead of changing the image shape as it affects the image quality.
                color_frame = frames.get_color_frame()
                color_image = np.asanyarray(color_frame.get_data())
                print(color_image.shape)
                frame = cv2.resize(color_image, (self.width, self.height),  interpolation=cv2.INTER_AREA)
                # frame = cv2.resize(frame, (opt.image_width, opt.image_height), \
                #     interpolation = cv2.INTER_LINEAR)
                # data = frame.tostring()
                data = frame.tostring()
                buf = Gst.Buffer.new_allocate(None, len(data), None)
                buf.fill(0, data)
                buf.duration = self.duration
                timestamp = self.number_frames * self.duration
                buf.pts = buf.dts = int(timestamp)
                buf.offset = timestamp
                self.number_frames += 1
                retval = src.emit('push-buffer', buf)
                print('pushed buffer, frame {}, duration {} ns, durations {} s'.format(self.number_frames,
                                                                                       self.duration,
                                                                                       self.duration / Gst.SECOND))
                if retval != Gst.FlowReturn.OK:
                    print(retval)
    # attach the launch string to the override method
    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)
    
    # attaching the source element to the rtsp media
    def do_configure(self, rtsp_media):
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)

# Rtsp server implementation where we attach the factory sensor with the stream uri
class GstServer(GstRtspServer.RTSPServer):
    def __init__(self, **properties):
        super(GstServer, self).__init__(**properties)
        self.factory = SensorFactory()
        self.factory.set_shared(True)
        self.set_service(str(opt.port))
        self.get_mount_points().add_factory(opt.stream_uri, self.factory)
        self.attach(None)

# getting the required information from the user 
parser = argparse.ArgumentParser()
# parser.add_argument("--device_id", required=True, help="device id for the \
#                 video device or video file location")
parser.add_argument("--fps", required=True, help="fps of the camera", type = int)
# parser.add_argument("--image_width", required=True, help="video frame width", type = int)
# parser.add_argument("--image_height", required=True, help="video frame height", type = int)
parser.add_argument("--port", default=8554, help="port to stream video", type = int)
parser.add_argument("--stream_uri", default = "/video_stream", help="rtsp video stream uri")
opt = parser.parse_args()

# try:
#     opt.device_id = int(opt.device_id)
# except ValueError:
#     pass
# initializing the threads and running the stream on loop.

GObject.threads_init()
Gst.init(None)
server = GstServer()
loop = GObject.MainLoop()
loop.run()