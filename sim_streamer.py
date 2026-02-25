#!/usr/bin/env python3
import sys
import socket
import netifaces
import numpy as np
import gi

gi.require_version('Gst', '1.0')
gi.require_version('GstRtspServer', '1.0')
from gi.repository import Gst, GstRtspServer, GObject, GLib

# Initialize GStreamer
Gst.init(None)
mainloop = GLib.MainLoop()

try:
    import rclpy
    from rclpy.node import Node
    from sensor_msgs.msg import Image
    from cv_bridge import CvBridge
    import cv2
    from threading import Thread, Lock
except ImportError as e:
    print(f"Error importing ROS2 packages: {e}")
    sys.exit(1)

def get_all_ip_addresses():
    """Get all available network interface IP addresses."""
    ip_addresses = {}
    interfaces = netifaces.interfaces()
    
    for iface in interfaces:
        addrs = netifaces.ifaddresses(iface)
        if netifaces.AF_INET in addrs:  # Only get IPv4 addresses
            ip_addresses[iface] = addrs[netifaces.AF_INET][0]['addr']
    
    return ip_addresses
Gst.init(None)

class VideoStreamFactory(GstRtspServer.RTSPMediaFactory):
    def __init__(self):
        super().__init__()
        self.number_frames = 0
        self.fps = 30
        self.duration = 1 / self.fps * Gst.SECOND
        self.frame = None
        self._frame_lock = Lock()
        self.launch_string = (
            'appsrc name=source is-live=true block=true format=GST_FORMAT_TIME '
            'caps=video/x-raw,format=BGR,width=1280,height=720,framerate={}/1 '
            '! videoconvert ! video/x-raw,format=I420 '
            '! x264enc speed-preset=ultrafast tune=zerolatency '
            '! rtph264pay config-interval=1 name=pay0 pt=96'
            .format(self.fps)
        )

    def do_create_element(self, url):
        return Gst.parse_launch(self.launch_string)

    def do_configure(self, rtsp_media):
        self.number_frames = 0
        appsrc = rtsp_media.get_element().get_child_by_name('source')
        appsrc.connect('need-data', self.on_need_data)

    def on_need_data(self, src, length):
        with self._frame_lock:
            if self.frame is not None:
                try:
                    data = self.frame.tobytes()
                    buf = Gst.Buffer.new_allocate(None, len(data), None)
                    buf.fill(0, data)
                    buf.duration = self.duration
                    timestamp = self.number_frames * self.duration
                    buf.pts = buf.dts = int(timestamp)
                    buf.offset = timestamp
                    self.number_frames += 1
                    retval = src.emit('push-buffer', buf)
                    if retval != Gst.FlowReturn.OK:
                        print(f'Error pushing buffer: {retval}')
                except Exception as e:
                    print(f'Error in on_need_data: {e}')

class ROS2ToRTSP(Node):
    def __init__(self):
        super().__init__('ros2_to_rtsp')
        self.bridge = CvBridge()
        
        # Get all network interfaces
        ip_addresses = get_all_ip_addresses()
        
        # Log available interfaces
        self.get_logger().info("\nAvailable network interfaces:")
        for iface, ip in ip_addresses.items():
            self.get_logger().info(f"{iface}: {ip}")
        
        self.factory = VideoStreamFactory()
        self.server = GstRtspServer.RTSPServer()
        self.server.set_service("8554")
        
        # Listen on all interfaces
        self.server.set_address("0.0.0.0")
        
        mount_points = self.server.get_mount_points()
        mount_points.add_factory("/mystream", self.factory)
        self.server.attach(None)
        
        # Log all possible stream URLs
        self.get_logger().info("\nRTSP Stream URLs:")
        self.get_logger().info("Local: rtsp://localhost:8554/mystream")
        for iface, ip in ip_addresses.items():
            self.get_logger().info(f"{iface}: rtsp://{ip}:8554/mystream")

        # Create subscription
        self.subscription = self.create_subscription(
            Image,
            '/camera/image',
            self.image_callback,
            10)

    def image_callback(self, msg):
        try:
            cv_image = self.bridge.imgmsg_to_cv2(msg, desired_encoding='bgr8')
            resized_image = cv2.resize(cv_image, (1280, 720))
            self.factory.frame = resized_image
        except Exception as e:
            self.get_logger().error(f"Image conversion failed: {e}")

def check_dependencies():
    try:
        import cv2
        import numpy
        from cv_bridge import CvBridge
        import netifaces
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please install required packages:")
        print("pip install opencv-python numpy")
        print("sudo apt-get install python3-netifaces ros-humble-cv-bridge")
        return False

def main(args=None):
    if not check_dependencies():
        sys.exit(1)

    rclpy.init(args=args)
    
    try:
        # Create ROS2 node
        node = ROS2ToRTSP()
        
        # Run GLib main loop in the main thread
        try:
            rclpy.spin(node)
        except KeyboardInterrupt:
            pass
        
    except Exception as e:
        print(f"Error in main: {e}")
    
    finally:
        if 'node' in locals():
            node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
