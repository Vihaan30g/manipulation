import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from moveit_configs_utils import MoveItConfigsBuilder

def generate_launch_description():

    # Build config ONCE, with planning pipelines included
    moveit_config = (
        MoveItConfigsBuilder("gen5manipulator1", package_name="moveit_pkg2")
        .trajectory_execution(file_path="config/moveit_controllers.yaml")
        .planning_pipelines(
            default_planning_pipeline="ompl",
            pipelines=["ompl"]
        )
        .to_moveit_configs()
    )

    move_group_node = Node(
        package="moveit_ros_move_group",
        executable="move_group",
        output="screen",
        parameters=[
            moveit_config.to_dict(),
            {"use_sim_time": True},
        ],
    )

    rviz_base = os.path.join(get_package_share_directory("moveit_pkg2"), "config", "moveit.rviz")
    if not os.path.exists(rviz_base):
        rviz_base = os.path.join(get_package_share_directory("moveit_pkg2"), "launch", "moveit.rviz")

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", rviz_base],
        parameters=[
            moveit_config.to_dict(),
            # no use_sim_time here — keeps RViz interactive markers working
            #{"use_sim_time": True},    #DEBUG
        ],
    )

    # Only Node objects go in LaunchDescription — never the config object itself
    return LaunchDescription([
        move_group_node,
        rviz_node,
    ])