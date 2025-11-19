from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    # Declare launch argument for config string
    config_arg = DeclareLaunchArgument(
        'config',
        default_value='gr00t_so101_rtc',
        description='Configuration string for the RFM action server'
    )
    
    return LaunchDescription([
        config_arg,
        
        Node(
            package='rfm_control',
            executable='rfm_action_server',
            name='rfm_action_server',
            arguments=[LaunchConfiguration('config')],
            output='screen'
        ),

        Node(
            package='image_processing',
            executable='image_publisher',
            name='image_publisher',
            parameters=[
                {'camera_index': 2},
                {'topic_prefix': 'wrist'}
            ],
            output='screen'
        ),

        Node(
            package='image_processing',
            executable='image_publisher',
            name='image_publisher',
            parameters=[
                {'camera_index': 0},
                {'topic_prefix': 'global_front'}
            ],
            output='screen'
        )
    ])
