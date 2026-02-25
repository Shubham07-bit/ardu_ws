#!/usr/bin/env python3
# filepath: /home/shubham/ardu_ws/src/autonomus_takeoff_landing/autonomus_takeoff_landing/gps_disabler.py

import rclpy
from rclpy.node import Node
from rcl_interfaces.srv import SetParameters, GetParameters
from rcl_interfaces.msg import Parameter, ParameterValue, ParameterType
from std_srvs.srv import Trigger

class GPSDisabler(Node):
    def __init__(self):
        super().__init__('gps_disabler')
        
        # Service clients for ArduPilot parameters
        self.param_set_client = self.create_client(SetParameters, '/ap/set_parameters')
        self.param_get_client = self.create_client(GetParameters, '/ap/get_parameters')
        
        # Service to trigger GPS disable
        self.disable_gps_srv = self.create_service(
            Trigger, 
            '/disable_gps', 
            self.disable_gps_callback
        )
        
        # Service to re-enable GPS
        self.enable_gps_srv = self.create_service(
            Trigger, 
            '/enable_gps', 
            self.enable_gps_callback
        )
        
        # Store original parameter values for restoration
        self.original_params = {}
        
        # Wait for services
        self.get_logger().info("Waiting for ArduPilot parameter services...")
        if self.param_set_client.wait_for_service(timeout_sec=10.0):
            self.get_logger().info("✓ Parameter services ready!")
        else:
            self.get_logger().error("✗ Parameter services not available")
            
        self.get_logger().info("GPS Disabler ready! Use services:")
        self.get_logger().info("  - ros2 service call /disable_gps std_srvs/srv/Trigger")
        self.get_logger().info("  - ros2 service call /enable_gps std_srvs/srv/Trigger")
    
    async def set_ardupilot_parameter(self, param_name, param_value):
        """Set an ArduPilot parameter using standard ROS2 parameter service"""
        request = SetParameters.Request()
        
        # Create Parameter message
        param = Parameter()
        param.name = param_name
        param.value = ParameterValue()
        
        # Set parameter type and value
        if isinstance(param_value, int):
            param.value.type = ParameterType.PARAMETER_INTEGER
            param.value.integer_value = param_value
        elif isinstance(param_value, float):
            param.value.type = ParameterType.PARAMETER_DOUBLE
            param.value.double_value = param_value
        elif isinstance(param_value, str):
            param.value.type = ParameterType.PARAMETER_STRING
            param.value.string_value = param_value
        elif isinstance(param_value, bool):
            param.value.type = ParameterType.PARAMETER_BOOL
            param.value.bool_value = param_value
        
        request.parameters = [param]
        
        try:
            future = self.param_set_client.call_async(request)
            rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
            
            if future.result() and len(future.result().results) > 0:
                result = future.result().results[0]
                if result.successful:
                    self.get_logger().info(f"✓ Set {param_name} = {param_value}")
                    return True
                else:
                    self.get_logger().error(f"✗ Failed to set {param_name} = {param_value}: {result.reason}")
                    return False
            else:
                self.get_logger().error(f"✗ No result for {param_name} = {param_value}")
                return False
        except Exception as e:
            self.get_logger().error(f"Error setting {param_name}: {e}")
            return False
    
    async def get_ardupilot_parameter(self, param_name):
        """Get an ArduPilot parameter using standard ROS2 parameter service"""
        request = GetParameters.Request()
        request.names = [param_name]
        
        try:
            future = self.param_get_client.call_async(request)
            rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
            
            if future.result() and len(future.result().values) > 0:
                param_value = future.result().values[0]
                
                if param_value.type == ParameterType.PARAMETER_NOT_SET:
                    self.get_logger().warn(f"Parameter {param_name} is not set")
                    return None
                elif param_value.type == ParameterType.PARAMETER_INTEGER:
                    value = param_value.integer_value
                elif param_value.type == ParameterType.PARAMETER_DOUBLE:
                    value = param_value.double_value
                elif param_value.type == ParameterType.PARAMETER_STRING:
                    value = param_value.string_value
                elif param_value.type == ParameterType.PARAMETER_BOOL:
                    value = param_value.bool_value
                else:
                    value = "UNKNOWN_TYPE"
                
                self.get_logger().info(f"Current {param_name} = {value}")
                return value
            else:
                self.get_logger().error(f"Failed to get {param_name}")
                return None
        except Exception as e:
            self.get_logger().error(f"Error getting {param_name}: {e}")
            return None
    
    def disable_gps_callback(self, request, response):
        """Service callback to disable GPS"""
        self.get_logger().info("🚫 DISABLING GPS DURING FLIGHT...")
        
        # Run async parameter setting
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(self.disable_gps_params())
        
        if success:
            response.success = True
            response.message = "GPS disabled successfully. Monitor the drone behavior!"
            self.get_logger().info("🚫 GPS DISABLED - Watch how the drone behaves now!")
        else:
            response.success = False
            response.message = "Failed to disable GPS"
        
        return response
    
    def enable_gps_callback(self, request, response):
        """Service callback to re-enable GPS"""
        self.get_logger().info("📡 RE-ENABLING GPS...")
        
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        success = loop.run_until_complete(self.enable_gps_params())
        
        if success:
            response.success = True
            response.message = "GPS re-enabled successfully"
            self.get_logger().info("📡 GPS RE-ENABLED")
        else:
            response.success = False
            response.message = "Failed to re-enable GPS"
        
        return response
    
    async def disable_gps_params(self):
        """Disable GPS by setting ArduPilot parameters"""
        self.get_logger().info("Setting parameters to disable GPS...")
        
        # First, let's get current values and store them for restoration
        params_to_check = ['GPS1_TYPE', 'GPS2_TYPE', 'AHRS_GPS_USE']
        
        for param_name in params_to_check:
            current_value = await self.get_ardupilot_parameter(param_name)
            if current_value is not None:
                self.original_params[param_name] = current_value
        
        # Parameters to disable GPS (corrected names)
        params_to_disable = [
            ('GPS1_TYPE', 0),      # Disable primary GPS (corrected from GPS_TYPE)
            ('GPS2_TYPE', 0),      # Disable secondary GPS (corrected from GPS_TYPE2)
            ('AHRS_GPS_USE', 0),   # Don't use GPS for AHRS
        ]
        
        success_count = 0
        total_attempts = 0
        
        for param_name, param_value in params_to_disable:
            # Only try to set parameters that exist
            if param_name in self.original_params:
                total_attempts += 1
                self.get_logger().info(f"Setting {param_name} = {param_value}")
                if await self.set_ardupilot_parameter(param_name, param_value):
                    success_count += 1
            else:
                self.get_logger().info(f"Parameter {param_name} not available, skipping")
        
        success = success_count > 0
        self.get_logger().info(f"Successfully disabled {success_count}/{total_attempts} GPS parameters")
        return success
    
    async def enable_gps_params(self):
        """Re-enable GPS by restoring ArduPilot parameters"""
        self.get_logger().info("Restoring original GPS parameters...")
        
        if not self.original_params:
            self.get_logger().warn("No original parameters stored! Using default values...")
            # Use default values if no original parameters stored
            params_to_enable = [
                ('GPS1_TYPE', 1),     # Enable primary GPS (AUTO)
                ('GPS2_TYPE', 0),     # Keep secondary GPS disabled  
                ('AHRS_GPS_USE', 1),  # Use GPS for AHRS
            ]
            
            success_count = 0
            for param_name, param_value in params_to_enable:
                self.get_logger().info(f"Setting {param_name} = {param_value}")
                if await self.set_ardupilot_parameter(param_name, param_value):
                    success_count += 1
            
            return success_count > 0
        
        # Restore original values
        success_count = 0
        for param_name, original_value in self.original_params.items():
            self.get_logger().info(f"Restoring {param_name} = {original_value}")
            if await self.set_ardupilot_parameter(param_name, original_value):
                success_count += 1
        
        success = success_count == len(self.original_params)
        if success:
            self.original_params.clear()  # Clear stored values after successful restoration
        
        return success

def main(args=None):
    rclpy.init(args=args)
    node = GPSDisabler()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()