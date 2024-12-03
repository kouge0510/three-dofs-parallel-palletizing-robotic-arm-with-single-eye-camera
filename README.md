# Four-Axis Parallel Palletizing Robot Arm


## Overview

This project is a four-axis parallel robot arm equipped with a suction cup as the end-effector, controlled via an electromagnet valve. The system runs on a Linux-based environment and introduces several advanced
And I really think National University Internet of Things Design Competition is such a stupid ass that invited a lot of freshman to be the judge.Such a funny story !
## thanks for @wissem01chiha's devotion!
## the project is based on  https://github.com/wissem01chiha/robotic-arm-manipulator  ,and we transferred the code into C++ and Python.
## features:

- **Arduino**: Controls the suction cup and electromagnet valve.
- **Embedded Development Board**: Handles the motion control of the arm.
- **YOLOv5**: Used for detecting packaging damage.
- **Machine Vision**: For recognizing QR codes on items.
- **SQLite Database**: For storing data related to detected damages, QR codes, and operational logs.





## New Features

1. **Package Damage Detection (YOLOv5)**: The system uses YOLOv5, a real-time object detection algorithm, to detect if any packaging is damaged before palletizing.
2. **QR Code Recognition**: Machine vision algorithms are integrated to scan and identify QR codes on items.
3. **Data Storage**: Detected damage reports and QR code information are stored in an SQLite database for later retrieval and analysis.


## File Structure

- **Arduino File**: Code for controlling the electromagnet valve, located with the `arduino` tag.
- **ARM File**: Code for controlling the arm's movement, located with the `arm` tag.
- The system runs on **Linux**, where you can execute the control scripts.

## Hardware Setup

1. Connect the suction cup and electromagnet valve to the Arduino.
2. Connect the motors for the three-axis parallel mechanism to the embedded development board.
3. Set up a camera for capturing images for damage detection and QR code scanning.

## Usage

1. Power on the Arduino and the embedded development board.
2. Run the control script on the Linux system to operate the robot arm.


This simplified version should match your expectations more closely. Let me know if any additional changes are needed!
## Video

https://github.com/user-attachments/assets/ff2da048-5606-41ff-be5a-901702e168f5


