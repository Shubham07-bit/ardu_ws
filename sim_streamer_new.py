#!/usr/bin/env python3
import sys
import gi
import socket
import threading

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GLib

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import Image
from cv_bridge import CvBridge
import cv2
import numpy as np

class RTSPServer:
    def __init__(self, port=8554):
        Gst.init(None)
        self.port = port
        self.server = None
        self.factory = None
        self.frame_count = 0
        self.last_pts = 0
        self.frame = None
        self.start_server()
        
    def start_server(self):
        try:
            # Clean up any existing server
            if self.server:
                self.server.detach()
                self.server = None

            # Create new server instance
            self.server = GstRtspServer.RTSPServer()
            self.server.set_service(str(self.port))
            self.server.set_address("0.0.0.0")
            
            # Create and configure media factory
            self.factory = GstRtspServer.RTSPMediaFactory()
            self.factory.set_launch(
                'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME ' +
                'caps=video/x-raw,format=BGR,width=640,height=480,framerate=30/1 ' +
                '! videoconvert ! video/x-raw,format=I420 ' +
                '! x264enc tune=zerolatency speed-preset=ultrafast key-int-max=30 ' +
                '! h264parse ! rtph264pay config-interval=1 name=pay0 pt=96'
            )
            
            self.factory.set_shared(True)
            mount_points = self.server.get_mount_points()
            mount_points.add_factory("/stream", self.factory)
            
            # Connect signals
            self.factory.connect('media-configure', self.on_media_configure)
            
            # Attach the server
            self.server.attach(None)
            
            # Print stream URLs
            print("\nRTSP Stream URLs:")
            print(f"Local: rtsp://localhost:{self.port}/stream")
            
            # Get all network interfaces
            interfaces = socket.getaddrinfo(socket.gethostname(), None)
            for interface in interfaces:
                ip = interface[4][0]
                if not ip.startswith('127.'):  # Skip localhost
                    print(f"Network: rtsp://{ip}:{self.port}/stream")
                    
        except Exception as e:
            print(f"Error starting RTSP server: {e}")
            raise
        self.frame_count = 0
        self.last_pts = 0
        
        self.factory.set_shared(True)
        mount_points = self.server.get_mount_points()
        mount_points.add_factory("/stream", self.factory)
        self.server.attach(None)
        
        # Get all IP addresses
        print("\nRTSP Stream URLs:")
        print(f"Local: rtsp://localhost:{self.port}/stream")
        
        # Get all network interfaces
        interfaces = socket.getaddrinfo(socket.gethostname(), None)
        for interface in interfaces:
            ip = interface[4][0]
            if not ip.startswith('127.'):  # Skip localhost
                print(f"Network: rtsp://{ip}:{self.port}/stream")
        
        self.frame = None
        self.factory.connect('media-configure', self.on_media_configure)
        
    def on_media_configure(self, factory, media):
        appsrc = media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)
        return True
        
    def on_need_data(self, src, length):
        if self.frame is not None:
            try:
                data = self.frame.tobytes()
                buf = Gst.Buffer.new_wrapped(data)
                
                # Set buffer timestamps
                fps = 30
                duration = Gst.SECOND / fps
                self.frame_count += 1
                pts = self.last_pts + duration
                self.last_pts = pts
                
                buf.pts = pts
                buf.dts = pts
                buf.duration = duration
                
                # Push the buffer
                ret = src.emit('push-buffer', buf)
                
                if ret != Gst.FlowReturn.OK:
                    print(f"Warning: Failed to push buffer: {ret}")
                else:
                    if self.frame_count % 30 == 0:  # Log every second
                        print(f"Pushed frame {self.frame_count}")
            except Exception as e:
                print(f"Error in on_need_data: {e}")

    def update_frame(self, frame):
        # Ensure frame is the right size and format
        if frame is not None:
            try:
                resized = cv2.resize(frame, (640, 480))
                # Ensure the frame is contiguous
                if not resized.flags['C_CONTIGUOUS']:
                    resized = np.ascontiguousarray(resized)
                self.frame = resized
                return True
            except Exception as e:
                print(f"Error updating frame: {e}")
                return False
        return False

class CameraNode(Node):
    def __init__(self, rtsp_server):
        super().__init__('camera_node')
        self.rtsp_server = rtsp_server
        self.bridge = CvBridge()
        
        self.subscription = self.create_subscription(
            Image,
            '/camera/image',
            self.image_callback,
            10
        )
    
    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, 'bgr8')
            self.rtsp_server.update_frame(cv_image)
        except Exception as e:
            self.get_logger().error(f'Error processing image: {e}')

def cleanup_resources():
    """Clean up any lingering RTSP server resources"""
    try:
        # Try to kill any lingering RTSP processes
        import subprocess
        subprocess.run(['pkill', '-f', 'rtsp-server'], stderr=subprocess.DEVNULL)
    except:
        pass

def main():
    # Cleanup any existing resources
    cleanup_resources()
    
    # Initialize GLib loop
    loop = GLib.MainLoop()
    
    try:
        # Start RTSP server
        server = RTSPServer()
        
        # Initialize ROS2
        rclpy.init()
        node = CameraNode(server)
        
        # Run GLib loop in a separate thread
        thread = threading.Thread(target=loop.run)
        thread.daemon = True
        thread.start()
        
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            print("\nShutting down gracefully...")
        finally:
            if server and server.server:
                server.server.detach()
            node.destroy_node()
            rclpy.shutdown()
            loop.quit()
            cleanup_resources()
    except Exception as e:
        print(f"Error in main: {e}")
        cleanup_resources()
        sys.exit(1)

if __name__ == '__main__':
    main()
