#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float64MultiArray

class TeleopGUI(Node):
    def __init__(self):
        super().__init__('teleop_gui')
        
        self.declare_parameter('controller_topic', '/leg_joint_position_controller/commands')
        topic = self.get_parameter('controller_topic').value
        
        self.publisher_ = self.create_publisher(Float64MultiArray, topic, 10)
        
        # Joint names matching the YAML configuration
        self.joint_names = [
            'rear_right_base_hip_joint',
            'rear_right_hip_tibia_joint',
            'rear_right_tibia_paw_joint',
            'rear_left_base_hip_joint',
            'rear_left_hip_tibia_joint',
            'rear_left_tibia_paw_joint',
            'front_right_base_hip_joint',
            'front_right_hip_tibia_joint',
            'front_right_tibia_paw_joint',
            'front_left_base_hip_joint',
            'front_left_hip_tibia_joint',
            'front_left_tibia_paw_joint'
        ]
        
        self.positions = {name: 0.0 for name in self.joint_names}
        
    def publish_positions(self):
        msg = Float64MultiArray()
        msg.data = [float(self.positions[name]) for name in self.joint_names]
        self.publisher_.publish(msg)

    def set_position(self, name, value):
        self.positions[name] = value
        self.publish_positions()

# GUI Setup
def main(args=None):
    rclpy.init(args=args)
    node = TeleopGUI()

    root = tk.Tk()
    root.title("RoboDog Joint Control")
    root.geometry("600x600")
    
    # Outer frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    title = ttk.Label(main_frame, text="RoboDog Kinematics Controller", font=("Helvetica", 16))
    title.pack(pady=(0, 20))
    
    # Create sliders for each joint
    for i, joint_name in enumerate(node.joint_names):
        frame = ttk.Frame(main_frame)
        frame.pack(fill='x', pady=5)
        
        label = ttk.Label(frame, text=joint_name, width=30)
        label.pack(side='left')
        
        value_label = ttk.Label(frame, text="0.00", width=5)
        
        # Callback wrapper to pass the joint name
        def make_callback(jname, vlabel):
            def callback(val):
                vlabel.config(text=f"{float(val):.2f}")
                node.set_position(jname, float(val))
            return callback
        
        slider = ttk.Scale(frame, from_=-3.14, to=3.14, orient='horizontal', 
                           command=make_callback(joint_name, value_label))
        slider.set(0.0)
        slider.pack(side='left', fill='x', expand=True, padx=10)
        value_label.pack(side='right')

    # Status label
    status = ttk.Label(main_frame, text="Publishing to /leg_joint_position_controller/commands", foreground="green")
    status.pack(pady=20)

    # Allow to update ros communication in Tkinter window loop
    def update_ros():
        if rclpy.ok():
            rclpy.spin_once(node, timeout_sec=0.01)
            root.after(50, update_ros)
        
    root.after(50, update_ros)
    
    # Handle window close
    def on_closing():
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()
        root.destroy()
        
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

if __name__ == '__main__':
    main()
