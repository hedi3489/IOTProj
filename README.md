# Smart Home IoT Simulation
A smart home simulation built using a Raspberry Pi 400 and a breadboard.  
The project models real-world home automation by integrating sensors, actuators, user preferences, and a web-based dashboard.

The system was developed in four incremental phases, focusing on hardware–software integration and automation logic.

## Features
- LED used as a simulated light bulb
- DC motor used as a simulated fan
- Temperature and humidity sensing using a DHT11 sensor
- Ambient light sensing using a photoresistor
- Automatic control logic based on sensor thresholds
- Web-based dashboard to monitor and control system state
- Email notifications when temperature or light levels fall below thresholds
- User confirmation via email (Yes / No) to activate components
- RFID-based identification of household members
- Per-user preferred temperature and light thresholds

## System Architecture

The system consists of the following components:

1. Hardware Layer  
   - Raspberry Pi 400
   - Breadboard-based circuit
   - LED (light simulation)
   - DC motor (fan simulation)
   - DHT11 temperature and humidity sensor
   - Photoresistor for ambient light sensing
   - RFID reader for user identification

2. Backend Logic  
   - Sensor data collection and processing
   - Automation rules based on temperature and light thresholds
   - User-specific preferences loaded via RFID identification
   - Email notification and response handling

3. Dashboard Interface  
   - Displays live sensor readings
   - Shows current state of devices
   - Allows manual control of the light and fan
  
## Automation Logic

- When ambient light falls below a user-defined threshold, the system turns the LED on.
- When temperature drops below a user-defined threshold, the DC motor (fan) state is adjusted.
- Each household member has personalized thresholds, loaded via RFID.
- If sensor values fall outside acceptable ranges, the system sends an email alert.
- Users can respond with "Yes" or "No" to confirm whether the system should activate the components.

## What I Learned

- Designing an end-to-end smart home automation system
- Integrating sensors, actuators, and user input into a unified workflow
- Implementing automation logic with personalized user preferences
- Building a monitoring and control dashboard for hardware systems
- Managing asynchronous events such as sensor updates and email responses
