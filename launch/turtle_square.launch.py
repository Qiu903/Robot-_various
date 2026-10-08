from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # 1. 定义海龟仿真器节点
    turtle_sim = Node(
        package='turtlesim',        # 包名
        executable='turtlesim_node',# 可执行程序名
        name='turtlesim'            # 节点重命名
    )

    # 2. 定义我们写的闭环控制节点
    control_node = Node(
        package='my_robot_control',
        executable='closed_loop_square',
        name='square_controller'
    )

    # 把所有要启动的节点放进列表
    return LaunchDescription([
        turtle_sim,
        control_node
    ])
