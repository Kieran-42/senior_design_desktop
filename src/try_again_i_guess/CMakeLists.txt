cmake_minimum_required(VERSION 3.8)

project(try_again_i_guess)

find_package(ament_cmake REQUIRED)

install(DIRECTORY
  config
  launch
  meshes
  urdf
  DESTINATION share/${PROJECT_NAME}
)

# Install gait scripts
install(PROGRAMS
  scripts/trotting_gait.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
