# 我的 ROS2 机器人学习记录

个人 ROS 2 学习过程记录，目标方向：机器人感知 → 具身智能。

## 环境
- Ubuntu 22.04 (WSL2)
- ROS 2 Humble
- Python 3.10
- Gazebo（gazebo_ros）、rviz2

## 我学到了什么
- 通信模型：话题 = 发布/订阅的"暗号"，**话题名 + 消息类型都匹配**才会连上；写错话题名会**静默失败**（不报错但收不到数据）
- 静默失败 vs 当场报错：话题写错 → 沉默等待；import 模块拼错 → 当场崩溃（ModuleNotFoundError）
- `rclpy.spin(node)` 是**单线程事件调度员**：它负责检查定时器/消息/服务，有事件就调用对应回调；没有它节点不干活
- 回调里不能放 `time.sleep()` 等阻塞操作：单线程下会卡住整个节点，导致定时器触发被跳过后合并、机器人一顿一顿
- ROS2 Python 节点万能骨架：`class 节点类(Node)` + `def main()` + `if __name__ == "__main__"`；`main` 负责 init → 建节点 → spin → shutdown
- Twist 消息是两层结构：`linear.x`（前进速度）/ `angular.z`（角速度，绕 Z 轴转，正=逆时针）；ROS2 消息字段是强类型 float，整数要写成 `3.0`

## 第4课：差速底盘运动学（正解 / 逆解）
- 差速底盘的两种轮速合成一个整体运动：**线速度 v = (v左 + v右) / 2**，**角速度 ω = (v右 - v左) / L**（L 是轮距）
- 逆运动学（我想让车怎么走 → 俩轮子各转多快）：**v左 = v - ω×L/2**，**v右 = v + ω×L/2**
- 直觉：两轮同速 → 直行；两轮反速 → 原地转；一快一慢 → 转弯
- Gazebo 的差速插件（libgazebo_ros_diff_drive）内部就是拿上面这套公式把 `/cmd_vel` 翻译成两个轮子的转速

## 第5课：URDF 建模 + Gazebo 仿真
- **URDF 只有两个核心概念**：`link` = 零件（刚体），`joint` = 零件之间的连接方式（决定能不能动、怎么动）
- 每个 link 要写三段：`visual`（长什么样，给人看）、`collision`（碰撞形状，给物理引擎看）、`inertial`（质量 + 转动惯量）
- **★最容易漏的是 `inertial`★**：漏了质量/转动惯量，模型在 Gazebo 里会乱飘、抖动甚至报错
- `joint` 的 `origin` 写子零件相对父零件的偏移；`type="continuous"` 表示可绕轴无限旋转（驱动轮用），`type="fixed"` 表示焊死不动（万向轮用）
- 圆柱默认是"竖着"的（轴沿 z），要用 `rpy="1.5708 0 0"`（= 绕 x 转 90°）把它放倒，才像一个立在地上的轮子
- **轮的转轴 `axis` 方向极其关键**：写反了车就"倒着跑"或转不起来
- 差速插件的 `wheel_separation`（轮距）和 `wheel_diameter`（轮径）**必须和 URDF 里画的几何对得上**，否则里程计（odom）会算错
- `launch` 文件 = 把"要启动的好几个程序"打包成一条命令（复用别人的 `IncludeLaunchDescription` + 用 `spawn_entity.py` 把车投放进 Gazebo）
- 用 `odom` 做闭环画正方形：状态机 **FWD（直行）/ TURN（转向）** 两态循环，靠"起点到当前位置的直线距离"判断走没走够一边，靠"yaw 角变化"判断转没转够 90°
- **角度归一化**：yaw 在 ±180° 处会突然跳变，裸减法会算出 ±300° 这种假值，要强行掰回 (-π, π] 区间
- 用 `robot_state_publisher` + rviz2 可以直接可视化 URDF 模型，不做仿真也能检查模型对不对

## 我踩过的坑
- `from geometry_msgs.msgs import Twist` 拼错 → ModuleNotFoundError（正确是 `geometry_msgs.msg`）
- 缺 `if __name__ == "__main__": main()` → 文件被读取一遍但**什么都不执行**（静默失败）
- 给 `msg.linear.x = 3` 赋整数 → AssertionError，必须 `msg.linear.x = 3.0`
- 在回调里 `time.sleep(2)` → spin 单线程被卡死，海龟每 2 秒才跳一次半圈
- 忘记删除多余的 import（如 `turtlesim.msg`、`math`）→ 代码残留垃圾，读起来混乱
- URDF 的 link 漏写 `inertial` → Gazebo 里模型乱飘 / 抖动 / 报错（质量、转动惯量是物理引擎的必需品）
- URDF 里轮子的 `axis` 方向写错 → 车"倒着跑"或转不起来（隐蔽的方向类错误）
- **后台残留的发布者进程干扰 `/cmd_vel`**：之前用 `ros2 topic pub ... /cmd_vel` 做测试忘了关，它一直在后台发速度指令，和当前控制节点"抢着发"，导致车**走走停停、画出圆圈而不是正方形**。排查方法：`ros2 topic info /cmd_vel -v` 看发布者数量，不正常就去 kill 掉残留进程（教训：单话题被多个发布者同时发指令时，行为不可控）
- rviz2 里视角距离太远（Distance 23.7 米）→ 半径 0.3 米的小模型根本看不见，按 F 键聚焦即可

## 节点清单
- `pose_subscriber.py`：订阅 `/turtle1/pose` 并打印位姿
- `square_driver.py`：开环控制，盲发指令画正方形
- `closed_loop_square.py`：闭环旋转 90 度（P 控制）
- `closed_loop_square_full.py`：PI 控制 + 超时检测，画完整正方形
- `circle_drive.py`：发布 `/turtle1/cmd_vel`，让海龟画圆（第一个独立调试、亲手踩坑修好的节点）
- `MY_control.py`：`AddTwoInts` 服务端示例（服务名 `add_two_ints`，注册为 `add_server`）
- `gazebo_square.py`：在 Gazebo 差速小车仿真中，订阅 `/odom`、发布 `/cmd_vel`，用 FWD/TURN 状态机画正方形（第一个跑在 Gazebo 里的闭环节点）

## 模型与配置文件
- `urdf/turtle_base.urdf`：第一版机器人模型（圆柱底盘 + 摄像头方块，fixed joint），用于 rviz2 可视化
- `urdf/diff_car.urdf`：两轮差速小车（车体 + 左右驱动轮 + 前万向轮 + diff_drive 插件），用于 Gazebo 仿真
- `launch/display_turtle.launch.py`：启动 `robot_state_publisher` + rviz2，可视化 URDF 模型
- `launch/spawn_car.launch.py`：启动 Gazebo 空世界并把差速小车投放进去
- `launch/turtle_square.launch.py`：启动 turtlesim + `closed_loop_square`
- `rviz/first_create.rviz`：rviz2 配置（Fixed Frame: base_link、RobotModel、TF）

## 运行方式
```bash
# 先编译并 source
colcon build --packages-select my_robot_control
source ~/ros2_ws/install/setup.bash

# —— 海龟篇 ——
ros2 run turtlesim turtlesim_node                   # 终端1：海龟仿真
ros2 run my_robot_control closed_loop_square_full   # 终端2：画正方形
ros2 run my_robot_control circle_drive              # 终端2：画圆

# —— Gazebo 差速小车篇 ——
ros2 launch my_robot_control spawn_car.launch.py    # 终端1：启动 Gazebo 并投放小车
ros2 run my_robot_control gazebo_square             # 终端2：让小车画正方形

# —— 可视化模型篇 ——
ros2 launch my_robot_control display_turtle.launch.py   # rviz2 中查看 URDF 模型
```
