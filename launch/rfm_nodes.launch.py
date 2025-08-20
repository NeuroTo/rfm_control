from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package='tng_control',
            executable='rfm_action_server',
            name='rfm_action_server',
            arguments=['gr00t_so101_rtc'],
            output='screen'
        ),

        Node(
            package='image_processing',
            executable='image_publisher',
            name='image_publisher',
            parameters=[
                {'camera_index': 6},
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
