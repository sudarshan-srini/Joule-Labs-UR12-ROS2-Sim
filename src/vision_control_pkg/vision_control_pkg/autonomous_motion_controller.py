#!/usr/bin/env python3
import os
import yaml
import rclpy
from rclpy.node import Node
from rclpy.parameter import Parameter
from geometry_msgs.msg import PoseStamped
from moveit_configs_utils import MoveItConfigsBuilder
from moveit.planning import MoveItPy
from scipy.spatial.transform import Rotation as R
from ament_index_python.packages import get_package_share_directory

# Action Client for direct controller interaction
from rclpy.action import ActionClient
from control_msgs.action import FollowJointTrajectory

class AutonomousMotionController(Node):
    def __init__(self):
        # Force the Python node into Simulation Time natively
        super().__init__('autonomous_motion_controller',
                         parameter_overrides=[Parameter('use_sim_time', Parameter.Type.BOOL, True)])
        
        # Action Client to bypass MoveIt's faulty Execution Manager
        self.traj_client = ActionClient(self, FollowJointTrajectory, '/joint_trajectory_controller/follow_joint_trajectory')
        
        # 1. Fetch system paths for UR files
        ur_desc_path = os.path.join(get_package_share_directory("ur_description"), "urdf", "ur.urdf.xacro")
        ur_moveit_path = os.path.join(get_package_share_directory("ur_moveit_config"), "srdf", "ur.srdf.xacro")
        
        # 2. Build config with template arguments
        builder = MoveItConfigsBuilder("ur", package_name="ur_moveit_config")
        builder.robot_description(file_path=ur_desc_path, mappings={"name": "ur", "ur_type": "ur12e"})
        builder.robot_description_semantic(file_path=ur_moveit_path, mappings={"name": "ur", "ur_type": "ur12e"})
        
        moveit_configs = builder.to_moveit_configs().to_dict()
        
        # 3. Load OMPL configurations from the package
        ompl_yaml_path = os.path.join(get_package_share_directory("ur_moveit_config"), "config", "ompl_planning.yaml")
        with open(ompl_yaml_path, 'r') as file:
            ompl_config = yaml.safe_load(file)
            
        moveit_configs["ompl"] = ompl_config["ompl"] if "ompl" in ompl_config else ompl_config
        moveit_configs["planning_pipelines"] = {"pipeline_names": ["ompl"]}
        
        moveit_configs["plan_request_params"] = {
            "planning_pipeline": "ompl",
            "planning_time": 5.0,
            "planning_attempts": 5,
            "max_velocity_scaling_factor": 0.5,
            "max_acceleration_scaling_factor": 0.5
        }

        # Force un-scaled simulation controller
        moveit_configs["moveit_simple_controller_manager"] = {
            "controller_names": ["joint_trajectory_controller"],
            "joint_trajectory_controller": {
                "type": "FollowJointTrajectory",
                "action_ns": "follow_joint_trajectory",
                "default": True,
                "joints": [
                    "shoulder_pan_joint", "shoulder_lift_joint", "elbow_joint", 
                    "wrist_1_joint", "wrist_2_joint", "wrist_3_joint",
                ],
            },
        }
        
        # 4. Initialize MoveItPy for planning math only
        self.robot = MoveItPy(
            node_name="moveit_py_controller", 
            config_dict=moveit_configs
        )
        self.arm_group = self.robot.get_planning_component("ur_manipulator")

    def format_pose(self, target_array):
        target_pose = PoseStamped()
        target_pose.header.frame_id = "base_link"
        
        target_pose.pose.position.x = target_array[0]
        target_pose.pose.position.y = target_array[1]
        target_pose.pose.position.z = target_array[2]
        
        rot_vec = [target_array[3], target_array[4], target_array[5]]
        quat = R.from_rotvec(rot_vec).as_quat() 
        
        target_pose.pose.orientation.x = quat[0]
        target_pose.pose.orientation.y = quat[1]
        target_pose.pose.orientation.z = quat[2]
        target_pose.pose.orientation.w = quat[3]
        return target_pose

    def execute_cartesian_move(self, target_array):
        pose_msg = self.format_pose(target_array)
        
        self.arm_group.set_goal_state(pose_stamped_msg=pose_msg, pose_link="tool0")
        self.get_logger().info(f"Computing collision-free path to: {target_array}")
        
        plan_result = self.arm_group.plan()
        
        if plan_result:
            self.get_logger().info("Path verified. Bypassing MoveIt execution manager...")
            
            # --- THE FINAL FIX: Correct Jazzy method name ---
            joint_traj = plan_result.trajectory.get_robot_trajectory_msg().joint_trajectory
            
            # Reset timestamps to 0 for immediate start in Gazebo
            joint_traj.header.stamp.sec = 0
            joint_traj.header.stamp.nanosec = 0
            
            goal_msg = FollowJointTrajectory.Goal()
            goal_msg.trajectory = joint_traj
            
            self.get_logger().info("Sending commands directly to the simulated motors!")
            self.traj_client.wait_for_server()
            self.traj_client.send_goal_async(goal_msg)
        else:
            self.get_logger().error("Motion planning failed.")

def main(args=None):
    rclpy.init(args=args)
    node = AutonomousMotionController()
    my_target = [0.087, 0.168, 0.729, 2.36, 2.237, -0.086]
    node.execute_cartesian_move(my_target)
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()