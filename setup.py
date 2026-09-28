from setuptools import find_packages, setup

package_name = 'my_robot_control'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='robot_linux',
    maintainer_email='robot_linux@todo.todo',
    description='ROS2 learning: closed-loop control',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'square_driver = my_robot_control.square_driver:main',
            'closed_loop_square = my_robot_control.closed_loop_square:main',
            'pose_subscriber = my_robot_control.pose_subscriber:main',
            'closed_loop_square_full = my_robot_control.closed_loop_square_full:main',
        ],
    },
)
