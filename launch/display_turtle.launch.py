import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    # 1. URDF 模型文件路径（构建后位于 share/my_robot_control/urdf/）
    pkg_share = get_package_share_directory('my_robot_control')
    urdf_file = os.path.join(pkg_share, 'urdf', 'turtle_base.urdf')

    # 读取 URDF 内容，作为 robot_description 参数传给 robot_state_publisher
    with open(urdf_file, 'r') as f:
        robot_desc = f.read()

    # 2. robot_state_publisher：解析 URDF，发布 robot_description 参数 + TF 树
    robot_state_publisher = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        parameters=[{'robot_description': robot_desc}],
        output='screen'
    )

    # 3. rviz2：自动加载保存好的可视化配置（含 RobotModel + TF 显示）
    rviz_config = os.path.join(pkg_share, 'rviz', 'first_create.rviz')
    rviz2 = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen'
    )

    return LaunchDescription([
        robot_state_publisher,
        rviz2
    ])
