cmake_minimum_required(VERSION 3.0.2)
project(ros_data_logger_visualizer)

find_package(catkin REQUIRED COMPONENTS
  rospy
  std_msgs
  message_runtime
)

catkin_package()

catkin_install_python(PROGRAMS
  scripts/data_logger.py
  DESTINATION ${CATKIN_PACKAGE_BIN_DESTINATION}
)

install(DIRECTORY config launch
  DESTINATION ${CATKIN_PACKAGE_SHARE_DESTINATION}
)
