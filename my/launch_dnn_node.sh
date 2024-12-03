#!/bin/bash

# Source the ROS2 setup script
source /opt/tros/setup.bash

# Set the camera type environment variable
export CAM_TYPE=usb

# Launch the ROS2 node with the specified configuration
ros2 launch dnn_node_example dnn_node_example.launch.py \
  dnn_example_config_file:=config/fcosworkconfig.json \
  dnn_example_image_width:=480 \
  dnn_example_image_height:=272

