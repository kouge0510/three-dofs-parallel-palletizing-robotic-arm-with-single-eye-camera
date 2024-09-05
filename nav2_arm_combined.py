#!/usr/bin/env python3
import threading
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.executors import MultiThreadedExecutor
import numpy as np
from armstart import armstart

from receive import serial_listener

file_lock = threading.Lock()


def start_app1_if_damaged():
    print("Checking recognition file...")
    try:
        with file_lock:
            with open('recognition', 'r') as file:
                content = file.read().strip()
                print(f"Recognition file content: {content}")
                if content == 'undamaged':
                    print("Content is 'undamaged', starting app1...")
                    app1.app.run(host='0.0.0.0', port=5000, debug=False, threaded=True)
                    with open('recognition', 'w') as file:
                        file.write('')
                    print("Removed 'undamaged' from recognition file.")
                else:
                    print("Content is not 'undamaged', app1 will not start.")
    except FileNotFoundError:
        print("Recognition file not found.")


def start_serial_listener():
    serial_listener()
    print("Serial listener started.")


def main_armcontrol():
    armstart_thread = threading.Thread(target=armstart)
    armstart_thread.start()

    listener_thread = threading.Thread(target=start_serial_listener)
    listener_thread.start()

    app1_thread = threading.Thread(target=start_app1_if_damaged)
    app1_thread.start()

    armstart_thread.join()
    listener_thread.join()
    app1_thread.join()


class NavigateAndExecute(Node):
    def __init__(self):
        super().__init__('navigate_and_execute')
        self._action_client = ActionClient(self, NavigateToPose, 'navigate_to_pose')
        self.goal_index = 0
        self.goals = [
            {'x': 0.25, 'y': 0.0, 'yaw': 0.0},
            {'x': 0.5, 'y': 0.0, 'yaw': 0.0},
            {'x': 0.75, 'y': 0.0, 'yaw': 0.0},
            {'x': 1.0, 'y': 0.0, 'yaw': 0.0},
            {'x': 1.25, 'y': 0.0, 'yaw': 0.0},
            {'x': 1.5, 'y': 0.0, 'yaw': 0.0}
        ]
        self.timer = None
        self.executing = False
        self.navigate_to_next_pose()

    def navigate_to_next_pose(self):
        if self.goal_index < len(self.goals):
            goal = self.goals[self.goal_index]
            pose = PoseStamped()
            pose.header.frame_id = 'map'
            pose.pose.position.x = goal['x']
            pose.pose.position.y = goal['y']
            quaternion = self.euler_to_quaternion(0, 0, goal['yaw'])
            pose.pose.orientation.x = quaternion[0]
            pose.pose.orientation.y = quaternion[1]
            pose.pose.orientation.z = quaternion[2]
            pose.pose.orientation.w = quaternion[3]
            self._action_client.wait_for_server()
            self._send_goal_future = self._action_client.send_goal_async(NavigateToPose.Goal(pose=pose))
            self._send_goal_future.add_done_callback(self.goal_response_callback)
        else:
            self.get_logger().info('All goals reached')

    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return
        self.get_logger().info('Goal accepted')
        self._get_result_future = goal_handle.get_result_async()
        self._get_result_future.add_done_callback(self.get_result_callback)

    def get_result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Navigation result: {result}')
        self.on_reach_destination()

    def on_reach_destination(self):
        self.get_logger().info('Reached destination')
        if self.goal_index == len(self.goals) - 3 or self.goal_index == len(self.goals) - 2:
            self.get_logger().info('Reached the penultimate goal, waiting for 20 seconds...')
            command_file_path = '/home/wheeltec/wheeltec_ros2/install/wheeltec_nav2/lib/wheeltec_nav2/command'
            with open(command_file_path, 'w') as file:
                file.write('goal reached')
            self.create_timer(20.0, self.proceed_to_next_goal)
        elif self.goal_index == len(self.goals) - 1:
            self.get_logger().info('Reached the final goal,nothing done...')
        elif self.goal_index == len(self.goals) - 4:
            self.executing = True
            self.execute_custom_function2()
        else:
            self.executing = True
            self.execute_custom_function()


    def proceed_to_next_goal(self):
        self.get_logger().info('Proceeding to the next goal...')
        self.executing = False
        self.goal_index += 1
        self.navigate_to_next_pose()

    def execute_custom_function(self):
        if self.executing:
            self.get_logger().info('Executing custom function...')

            command_file_path = '/home/wheeltec/wheeltec_ros2/install/wheeltec_nav2/lib/wheeltec_nav2/command'
            with open(command_file_path, 'w') as file:
                file.write('goal reached')
            self.get_logger().info('Wrote "goal reached" to command file')

            self.create_timer(50.0, self.check_and_proceed)

    def execute_custom_function2(self):
        if self.executing:
            self.get_logger().info('Executing custom function...')

            command_file_path = '/home/wheeltec/wheeltec_ros2/install/wheeltec_nav2/lib/wheeltec_nav2/command'
            with open(command_file_path, 'w') as file:
                file.write('goal reached')
            self.get_logger().info('Wrote "goal reached" to command file')

            self.create_timer(20.0, self.check_and_proceed)
    def check_and_proceed(self):
        finish_file_path = '/home/wheeltec/wheeltec_ros2/install/wheeltec_nav2/lib/wheeltec_nav2/finish'
        try:
            with open(finish_file_path, 'r') as file:
                content = file.read().strip()
                self.get_logger().info(f'Read from finish file: {content}')
                if content == 'finish':
                    self.get_logger().info('Finish file contains "finish", proceeding with next goal...')
                    with open(finish_file_path, 'w') as file:
                        file.write('')
                    self.executing = False
                    self.goal_index += 1
                    self.navigate_to_next_pose()
                else:
                    self.get_logger().info('Waiting for "finish" in finish file...')
                    self.create_timer(40.0, self.check_and_proceed)
        except FileNotFoundError:
            self.get_logger().error('Finish file not found.')
            self.create_timer(2.0, self.check_and_proceed)

    def euler_to_quaternion(self, roll, pitch, yaw):
        qx = np.sin(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) - np.cos(roll / 2) * np.sin(pitch / 2) * np.sin(
            yaw / 2)
        qy = np.cos(roll / 2) * np.sin(pitch / 2) * np.cos(yaw / 2) + np.sin(roll / 2) * np.cos(pitch / 2) * np.sin(
            yaw / 2)
        qz = np.cos(roll / 2) * np.cos(pitch / 2) * np.sin(yaw / 2) - np.sin(roll / 2) * np.sin(pitch / 2) * np.cos(
            yaw / 2)
        qw = np.cos(roll / 2) * np.cos(pitch / 2) * np.cos(yaw / 2) + np.sin(roll / 2) * np.sin(pitch / 2) * np.sin(
            yaw / 2)
        return [qx, qy, qz, qw]


def main(args=None):
    rclpy.init(args=args)
    node = NavigateAndExecute()
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    finally:
        executor.shutdown()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
