#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy, DurabilityPolicy
from sensor_msgs.msg import NavSatFix
from geographic_msgs.msg import GeoPoseStamped
from std_msgs.msg import String

class GPSMonitor(Node):
    def __init__(self):
        super().__init__('gps_monitor')

        # Create QoS Profile compatible with ArduPilot
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )


        # subscribe to GPS topics
        self.gps_sub = self.create_subscription(
            NavSatFix,
            '/ap/navsat',
            self.gps_callback,
            qos_profile
        )

        # subscribe to global position topic
        self.global_pos_sub = self.create_subscription(
            GeoPoseStamped,
            '/ap/geopose/filtered',
            self.global_pos_callback,
            qos_profile
        )

        # status publisher
        self.status_pub = self.create_publisher(String, '/gps_status', 10)

        self.timer = self.create_timer(2.0, self.publish_status)

        self.gps_fix_type = 0
        self.satellites_visible = 0
        self.last_gps_time = None
        self.position_valid = False

    def gps_callback(self, msg):
        """  This tells us: "What is the GPS receiver seeing? """
        self.gps_fix_type = msg.status.status # GPS health
        self.last_gps_time = self.get_clock().now()

        self.get_logger().info(
            f"GPS Status: Fix={self.gps_fix_type}, Lat={msg.latitude:.6f}, Lon={msg.longitude:.6f}, Alt={msg.altitude:.2f}m"
        )

    def global_pos_callback(self, msg):
        """ This tells us: "What does ArduPilot think our position is?" (after sensor fusion) """
        self.position_valid = True
        lat = msg.pose.position.latitude
        lon = msg.pose.position.longitude
        alt = msg.pose.position.altitude

        self.get_logger().info(
            f"Position: Lat={lat:.6f}, Lon={lon:.6f}, Alt={alt:.2f}m"
        )

    def publish_status(self):
        """ Publish GPS Status summary """
        current_time = self.get_clock().now()
        if self.last_gps_time is None:
            status = "NO_GPS_DATA"
        elif (current_time - self.last_gps_time).nanoseconds > 5e9: # 5 seconds
            status = "GPS_TIMEOUT"
        elif self.gps_fix_type < 2:
            status = "NO_GPS_FIX"
        else:
            status = "GPS_OK"

        status_msg = String()
        status_msg.data = f"{status} | Fix={self.gps_fix_type}"
        self.status_pub.publish(status_msg)

        self.get_logger().info(f"GPS Status Summary: {status_msg.data}")


def main(args=None):
    rclpy.init(args=args)
    node = GPSMonitor()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
