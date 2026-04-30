cmake_minimum_required(VERSION 3.8)

project(urdf_color)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  config
  launch
  meshes
  urdf
  worlds
  DESTINATION share/${PROJECT_NAME}
)

# Install gait scripts
install(PROGRAMS
  scripts/trotting_gait.py
  scripts/motor_command.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
