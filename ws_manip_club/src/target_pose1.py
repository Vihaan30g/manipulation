#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from geometry_msgs.msg import PoseStamped
from moveit_msgs.action import MoveGroup
from moveit_msgs.msg import MotionPlanRequest, Constraints, PositionConstraint, OrientationConstraint, BoundingVolume
from shape_msgs.msg import SolidPrimitive

class MoveToPoseClient(Node):
    def __init__(self):
        super().__init__('move_to_pose_client')
        # Connect directly to the existing active move_group action server
        self._action_client = ActionClient(self, MoveGroup, 'move_action')
        
    def send_goal(self):
        self.get_logger().info('Connecting to the active MoveIt engine...')
        if not self._action_client.wait_for_server(timeout_sec=10.0):
            self.get_logger().error('Could not find running MoveIt action server! Is MoveIt/RViz open?')
            return
        
        # Initialize the goal message
        goal_msg = MoveGroup.Goal()
        
        # 1. Motion Plan Request
        req = MotionPlanRequest()
        req.group_name = 'body' 
        req.pipeline_id = 'ompl'
        req.num_planning_attempts = 5
        req.allowed_planning_time = 5.0
        req.max_velocity_scaling_factor = 0.2
        req.max_acceleration_scaling_factor = 0.2
        
        # 2. Exact target coordinates and orientation
        target_pose = PoseStamped()
        target_pose.header.frame_id = 'world'
        target_pose.pose.position.x = 0.8290262523847088
        target_pose.pose.position.y = 0.41051866277680915
        target_pose.pose.position.z = 0.7971929132709911
        target_pose.pose.orientation.x = -6.979124120094485e-05
        target_pose.pose.orientation.y = 8.926367260080265e-05
        target_pose.pose.orientation.z = 4.0902185802763375e-05
        target_pose.pose.orientation.w = 0.9999999927440952
        
        # 3. Define Constraints (Target link + tolerances)
        constraints = Constraints()
        
        # Position Constraint
        pos_constraint = PositionConstraint()
        pos_constraint.header.frame_id = 'world'
        pos_constraint.link_name = 'dummy_ee_link'
        
        # Define an acceptable 1cm tolerance region around the target point
        bv = BoundingVolume()
        box = SolidPrimitive()
        box.type = SolidPrimitive.BOX
        box.dimensions = [0.01, 0.01, 0.01] 
        bv.primitives.append(box)
        bv.primitive_poses.append(target_pose.pose)
        
        pos_constraint.constraint_region = bv
        pos_constraint.weight = 1.0
        constraints.position_constraints.append(pos_constraint)
        
        # Orientation Constraint
        ori_constraint = OrientationConstraint()
        ori_constraint.header.frame_id = 'world'
        ori_constraint.link_name = 'dummy_ee_link' 
        ori_constraint.orientation = target_pose.pose.orientation
        ori_constraint.absolute_x_axis_tolerance = 0.05 
        ori_constraint.absolute_y_axis_tolerance = 0.05
        ori_constraint.absolute_z_axis_tolerance = 0.05
        ori_constraint.weight = 1.0
        constraints.orientation_constraints.append(ori_constraint)
        
        req.goal_constraints.append(constraints)
        goal_msg.request = req
        
        # 4. Set planning options: False means Plan AND Execute immediately
        goal_msg.planning_options.plan_only = False
        
        self.get_logger().info('Sending Cartesian goal directly to MoveIt...')
        self._send_goal_future = self._action_client.send_goal_async(goal_msg)
        self._send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected by MoveIt! Is the target out of reach?')
            return

        self.get_logger().info('Goal accepted! MoveIt is calculating path and moving...')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        self.get_logger().info('Success! Target execution complete.')
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    client = MoveToPoseClient()
    client.send_goal()
    rclpy.spin(client)

if __name__ == '__main__':
    main()
