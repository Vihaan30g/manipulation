import rclpy
from rclpy.node import Node
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint
from builtin_interfaces.msg import Duration
import tkinter as tk

class ManipulatorGUI(Node):
    def __init__(self):
        super().__init__('manipulator_gui_node')
        
        # Create publisher for the body controller
        self.publisher_ = self.create_publisher(
            JointTrajectory, 
            '/body_controller/joint_trajectory', 
            10
        )
        
        # These must match your URDF and controller configuration exactly
        self.joint_names = [
            'base_rotation', 
            'link1_pitch', 
            'link2_pitch', 
            'bevel_pitch', 
            'bevel_roll'
        ]

    def send_trajectory(self, positions):
        msg = JointTrajectory()
        msg.joint_names = self.joint_names
        
        point = JointTrajectoryPoint()
        point.positions = positions
        # Set movement duration to 1.0 second for smooth motion
        point.time_from_start = Duration(sec=1, nanosec=0)
        
        msg.points.append(point)
        self.publisher_.publish(msg)
        self.get_logger().info(f"Command Sent: {positions}")


def on_send(gui_node, sliders):
    # Read the current values of all sliders
    positions = [float(slider.get()) for slider in sliders]
    gui_node.send_trajectory(positions)


def main():
    rclpy.init()
    gui_node = ManipulatorGUI()

    # --- Setup Tkinter Window ---
    root = tk.Tk()
    root.title("Gen5 Manipulator Control Panel")
    root.geometry("450x350")

    tk.Label(root, text="Adjust Joint Angles (Radians)", font=("Arial", 14, "bold")).pack(pady=10)

    sliders = []
    
    # Generate a slider for every joint
    for joint in gui_node.joint_names:
        frame = tk.Frame(root)
        frame.pack(pady=5, padx=10, fill='x')
        
        # Joint Label
        tk.Label(frame, text=joint, width=15, anchor='w').pack(side='left')
        
        # Slider (-3.14 to 3.14 radians for full rotation)
        slider = tk.Scale(frame, from_=-3.14, to=3.14, resolution=0.01, orient='horizontal', length=250)
        slider.set(0.0) # Default to 0 position
        slider.pack(side='right')
        
        sliders.append(slider)

    # Send Command Button
    btn = tk.Button(
        root, 
        text="Send Command", 
        command=lambda: on_send(gui_node, sliders), 
        bg="green", 
        fg="white", 
        font=("Arial", 12, "bold")
    )
    btn.pack(pady=20)

    # Background ROS 2 Spin loop to keep the node alive
    def spin_ros():
        rclpy.spin_once(gui_node, timeout_sec=0.01)
        root.after(50, spin_ros)

    root.after(50, spin_ros)

    # Clean shutdown handling
    def on_closing():
        root.destroy()
        gui_node.destroy_node()
        rclpy.shutdown()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    
    # Start the GUI
    root.mainloop()

if __name__ == '__main__':
    main()