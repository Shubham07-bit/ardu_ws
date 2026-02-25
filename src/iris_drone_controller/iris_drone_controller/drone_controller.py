#!/usr/bin/env python3

import rclpy
from rclpy.node import Node
from ardupilot_msgs.srv import ArmMotors
from ardupilot_msgs.srv import ModeSwitch
from ardupilot_msgs.srv import Takeoff

class DroneController(Node):
    def __init__(self):
        super().__init__('drone_controller')
        
        # Create service clients
        self.mode_client = self.create_client(ModeSwitch, '/ap/mode_switch')
        self.arm_client = self.create_client(ArmMotors, '/ap/arm_motors')
        self.takeoff_client = self.create_client(Takeoff, '/ap/experimental/takeoff')
        
        # Wait for services to become available
        self.wait_for_services()
        
    def wait_for_services(self):
        self.get_logger().info('Waiting for services...')
        self.mode_client.wait_for_service()
        self.arm_client.wait_for_service()
        self.takeoff_client.wait_for_service()
        self.get_logger().info('All services are available!')

    def takeoff_sequence(self, altitude):
        # Change to GUIDED mode
        mode_request = ModeSwitch.Request()
        mode_request.mode = 4
        self.mode_client.call_async(mode_request)
        self.get_logger().info('Changed mode to GUIDED')
        
        # Arm the drone
        arm_request = ArmMotors.Request()
        arm_request.arm = True
        self.arm_client.call_async(arm_request)
        self.get_logger().info('Armed motors')
        
        # Takeoff to desired altitude
        takeoff_request = Takeoff.Request()
        takeoff_request.alt = float(altitude)
        self.takeoff_client.call_async(takeoff_request)
        self.get_logger().info(f'Taking off to {altitude} meters')

def main(args=None):
    rclpy.init(args=args)
    controller = DroneController()
    
    # Execute takeoff sequence with desired altitude (e.g., 10 meters)
    rclpy.spin_until_future_complete(
        controller,
        controller.takeoff_sequence(10.0)
    )
    
    controller.destroy_node()
    rclpy.shutdown()
