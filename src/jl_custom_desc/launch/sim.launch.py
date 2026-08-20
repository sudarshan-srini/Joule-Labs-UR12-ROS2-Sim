import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, AppendEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    # Dynamically find the install directories
    jl_pkg_share = get_package_share_directory('jl_custom_desc')
    ur_sim_share = get_package_share_directory('ur_simulation_gz')
    
    xacro_file = os.path.join(jl_pkg_share, 'urdf', 'jl_ur12.urdf.xacro')
    ros2_share_dir = os.path.abspath(os.path.join(jl_pkg_share, '..'))

    return LaunchDescription([
        AppendEnvironmentVariable('GZ_SIM_RESOURCE_PATH', ros2_share_dir),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(ur_sim_share, 'launch', 'ur_sim_control.launch.py')),
            launch_arguments={'ur_type': 'ur12e', 'description_file': xacro_file}.items()
        )
    ])