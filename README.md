# ROS 2 学习记录

## 环境
- Ubuntu 22.04 (WSL2)
- ROS 2 Humble
- Python 3.10

## 包含节点
- `pose_subscriber.py`：订阅 `/turtle1/pose` 并打印位姿
- `square_driver.py`：开环控制，盲发指令画正方形
- `closed_loop_square.py`：闭环旋转90度（P控制）
- `closed_loop_square_full.py`：PI控制 + 超时检测，画完整正方形

## 运行方式
```bash
ros2 run turtlesim turtlesim_node
ros2 run my_robot_control closed_loop_square_full
本仓库为个人 ROS 2 学习过程记录。祝各位无限进步。



# 我的 ROS2 机器人学习记录

## 我学到了什么（这段时间）
- 通信模型：话题=发布订阅"暗号"，名字+类型都匹配才连上；写错名字会**静默失败**（不报错但没数据）
- 静默失败 vs 当场报错：话题写错→沉默；import 拼错→当场崩
- spin 是单线程事件调度员：回调被 sleep 卡住，整个节点被堵住
- 踩过的坑已经几乎填完了，自己靠AI一点点摸索下来，逐渐慢慢掌握ROS2的基本使用

## 我踩过的坑
- `geometry_msgs.msgs` 拼错 → ModuleNotFoundError
- 缺 `if __name__ == "__main__":` → 文件"静默地啥也不干"
- 给 `linear.x` 赋整数 `3` → AssertionError，必须 `3.0`
- `time.sleep(2)` 卡回调 → 海龟一顿一顿跳
- 明白了最基础的模板原理和使用方法，大规模套用这个模板
## 节点清单
（保留现有的，加上 circle_drive）

## 运行方式
（保留现有的）