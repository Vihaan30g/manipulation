import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import ExecuteProcess, SetEnvironmentVariable
from launch_ros.actions import Node
from launch.substitutions import Command

def generate_launch_description():
    
    # 1. Package Directories
    pkg_gen5manipulator1 = get_package_share_directory('gen5manipulator1')
    pkg_moveit_pkg2 = get_package_share_directory('moveit_pkg2')
    
    # Resolves to the 'share' directory of the workspace so Gazebo finds 'package://' URIs
    workspace_share_dir = os.path.abspath(os.path.join(pkg_gen5manipulator1, '..'))

    # 2. Environment Variables
    # Tells Gazebo where to look for your STL mesh files
    set_env_mesh = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=workspace_share_dir
    )

    # Tells Ignition where to find the system plugin for ros2_control (Humble/Fortress standard path)
    set_env_plugin = SetEnvironmentVariable(
        name='IGN_GAZEBO_SYSTEM_PLUGIN_PATH',
        value='/opt/ros/humble/lib'
    )

    # 3. Process the XACRO into a URDF
    xacro_file = os.path.join(pkg_moveit_pkg2, 'config', 'gen5manipulator1.urdf.xacro')
    robot_description_content = Command(['xacro ', xacro_file])
    robot_description = {"robot_description": robot_description_content}

    # 4. Define Execution Nodes
    
    # Start Ignition Gazebo
    ign_gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', '-r', 'empty.sdf'],
        output='screen'
    )

    # Publish the Robot State (TF tree)
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[robot_description],
        output='screen'
    )

    # Spawn the robot within Ignition using the robot_description topic
    spawn_robot = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-name', 'gen5manipulator1',
            '-topic', 'robot_description',
            '-x', '0.0', '-y', '0.0', '-z', '0.0'
        ],
        output='screen'
    )

    # 5. Spawner Nodes for ros2_control
    
    spawn_joint_state = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_state_broadcaster', '--controller-manager', '/controller_manager'],
    )

    spawn_body_controller = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['body_controller', '--controller-manager', '/controller_manager'],
    )

    

    # 6. Return the Launch Description
    return LaunchDescription([
        set_env_mesh,
        set_env_plugin,
        ign_gazebo,
        robot_state_publisher,
        spawn_robot,
        spawn_joint_state,
        spawn_body_controller,
    ])