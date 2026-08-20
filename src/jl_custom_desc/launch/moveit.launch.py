import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    jl_pkg_share = get_package_share_directory('jl_custom_desc')
    ur_moveit_share = get_package_share_directory('ur_moveit_config')
    xacro_file = os.path.join(jl_pkg_share, 'urdf', 'jl_ur12.urdf.xacro')

    return LaunchDescription([
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(ur_moveit_share, 'launch', 'ur_moveit.launch.py')),
            launch_arguments={'ur_type': 'ur12e', 'use_sim_time': 'true', 'launch_rviz': 'true', 'description_file': xacro_file}.items()
        )
    ])