# Digital Twin Project - Team 2

## Overview
This repository contains the project code, documentation, and resources for Team 2's **Digital Twin** project developed at the University of Massachusetts Boston. The project utilizes advanced sensor integration, machine learning, and real-time data visualization through Microsoft HoloLens 2.

## Project Objective
Create an accurate digital twin of UMass Boston's McCormack and Wheatley buildings to monitor real-time data such as:
- Occupancy
- Temperature
- Humidity
- CO₂ and CO levels

## Main Components
- **Sensors**: Thermal cameras (MLX90640), ultrasonic sensors, CO₂ and CO sensors
- **ESP32**: Capturing thermal images and transmitting via Bluetooth
- **Raspberry Pi**: Processing thermal images, running the ML model
- **ML Model**: CNN built using TensorFlow, optimized via Keras Tuner
- **Microsoft HoloLens 2**: Visualizing live building data in augmented reality

### Setup
## Clone the repository:
```bash
git clone https://github.com/mouratony/SD_TEAM2_Digital_Twin.git
cd SD_TEAM2_Digital_Twin
```
## Hardware Integration
- ESP32 scripts and BLE setup details are included.

## Team Members
- **Antonio Moura** 
- **Daniel Pena** 
- **Hassan Al-Jaber**
- **Abdeljalil Hamidi** 

## Project Status
The project is actively maintained and was successfully demonstrated at the Engineering Expo, showcasing comprehensive real-time sensor integration and AR visualization. Though it still in it's early stage!

## Future Plans
- Expand sensor integration and accuracy
- Enhanced geolocation features within HoloLens
- Real-world building integration and web application development

## Acknowledgements
Thanks to Prof. Materdey, Prof. Michael Rahaim, Director of Technical Ops Andrew Davis, and all contributing Engin 492 students.

## Video Demo
[Watch the demo](https://youtu.be/HxvDmOebCrY?si=8NDDNSrptHjOx1gC)

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
