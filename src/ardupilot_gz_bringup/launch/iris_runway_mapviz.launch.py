#!/usr/bin/env python3

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, ExecuteProcess, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
import os


def generate_launch_description():
    pkg_ardupilot_gz_bringup = get_package_share_directory("ardupilot_gz_bringup")
    
    # Launch arguments
    model_arg = DeclareLaunchArgument(
        "model",
        default_value="iris_runway",
        description="Model name",
    )
    
    # Include the base iris_runway launch
    iris_runway_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            PathJoinSubstitution([
                pkg_ardupilot_gz_bringup,
                "launch",
                "iris_runway.launch.py"
            ])
        ]),
        launch_arguments={
            "model": LaunchConfiguration("model"),
        }.items(),
    )
    
    # MapViz configuration file path
    mapviz_config_file = os.path.join(
        pkg_ardupilot_gz_bringup,
        "config",
        "iris_mapviz.mvc"
    )
    
    # MapViz node
    mapviz_node = Node(
        package='mapviz',
        executable='mapviz',
        name='mapviz',
        parameters=[{
            'config': mapviz_config_file,
            'use_sim_time': True,
        }],
        output='screen'
    )
    
    # TF2 buffer server
    tf2_buffer_server = Node(
        package='tf2_ros',
        executable='buffer_server',
        name='tf2_buffer_server',
        output='screen'
    )
    
    # Static transform for map frame
    static_transform_map = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_transform_map',
        arguments=['0', '0', '0', '0', '0', '0', 'map', 'base_link'],
        output='screen'
    )
    
    # Delayed launch of MapViz to allow simulation to start first
    delayed_mapviz = TimerAction(
        period=5.0,
        actions=[mapviz_node]
    )
    
    return LaunchDescription([
        model_arg,
        iris_runway_launch,
        tf2_buffer_server,
        static_transform_map,
        delayed_mapviz,
    ])
