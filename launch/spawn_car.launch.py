# ============================================================================
# spawn_car.launch.py —— 一条命令，启动 Gazebo + 把这台小车"放"进去
#
# launch 文件的作用：把"要启动的好几个程序"打包成一个命令。
# 这里我们要启动两个东西：
#   1) Gazebo（空世界）                         ← 提供物理环境
#   2) spawn_entity.py                          ← 把 URDF 描述的车"投放"进去
# ============================================================================
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    # get_package_share_directory 拿到本功能包"安装后"的目录路径。
    # 注意：要读的是 install 目录里的文件，不是 src 里的源码目录。
    pkg_share = get_package_share_directory('my_robot_control')

    # 拼出 URDF 文件的完整路径： <包安装目录>/urdf/diff_car.urdf
    urdf_file = os.path.join(pkg_share, 'urdf', 'diff_car.urdf')

    # ---- 要启动的第 1 个东西：Gazebo 空世界 ----
    # "IncludeLaunchDescription" = 复用别人写好的 launch 文件。
    # 这里复用的是 gazebo_ros 自带的 gazebo.launch.py，它会自动：
    #   - 启动 gzserver（物理仿真核心）
    #   - 启动 gzclient（可视化窗口）
    #   - 加载 gazebo_ros 的工厂插件（这样 /spawn_entity 服务才存在）
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('gazebo_ros'),
                'launch', 'gazebo.launch.py'
            )
        )
    )

    # ---- 要启动的第 2 个东西：把车投放进 Gazebo ----
    # spawn_entity.py 是 gazebo_ros 提供的一个工具节点。
    # arguments 里每一项的含义：
    #   -file   后面跟 URDF 文件路径（从这里读车的样子）
    #   -entity 给这台车起个名字（在 Gazebo 里显示为 diff_car）
    #   -z 0.15 投放高度：从离地 0.15m 处落下，避免一开始就卡进地面
    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=['-file', urdf_file, '-entity', 'diff_car', '-z', '0.15'],
        output='screen'   # 把它打印的日志直接显示到终端，方便看是否成功
    )

    # LaunchDescription 是"清单"：里面列的程序会被启动
    return LaunchDescription([gazebo, spawn_entity])