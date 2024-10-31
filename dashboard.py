from flask import Flask, render_template, request, jsonify
import yagmail
import RPi.GPIO as GPIO
from Freenove_DHT import DHT
import time


app = Flask(__name__)


# LED setup
LED_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
# Initial LED state
led_state = False
GPIO.output(LED_PIN, GPIO.LOW)


# DHT11 sensor setup
DHT_PIN = 17
dht_sensor = DHT(DHT_PIN)


# Motor setup
ENA = 22  # Enable Pin
IN1 = 27  # Input Pin
IN2 = 17  # Input Pin
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)

@app.route('/')
def dashboard():
    GPIO.output(LED_PIN, GPIO.LOW)
    return render_template('index.html')


## TODO: implement the logic for the led turning on
@app.route('/toggle-led', methods=['POST'])
def toggle_led():
    #get current LED status
    global led_state

    data = request.get_json()
    #parse json data
    switch_state = data['state'] #Get the state value

    if switch_state:
        GPIO.output(LED_PIN, GPIO.HIGH) #Turn on LED if switch state is true
        led_state = True #Update led_state to follow that LED is now on
    else:
        GPIO.output(LED_PIN, GPIO.LOW) #Turn off LED if switch state is false
        led_state = False #Update led_state to follow that LED is now off

    return jsonify({'success': True, 'led_state': led_state}) # keep this line to indicate that the script passed and the led is turned on or off successfully, otherwise return False and include the current LED state in the response

# Data capture route for reading DHT11 sensor
@app.route('/read-sensor', methods=['GET'])
def read_sensor():
    for i in range(15):
        chk = dht_sensor.readDHT11()
        if chk == 0:
            humidity = dht_sensor.getHumidity()
            temperature = dht_sensor.getTemperature()
            if temperature > 24:
                send_email(temperature)

            return jsonify({'temperature': temperature, 'humidity': humidity})
        time.sleep(0.1)  # Short delay before retrying

    return jsonify({'error': 'Failed to retrieve data from sensor'}), 500


# Function to send email
def send_email(current_temp):
    sender_email = "iotdashboard2024@gmail.com"
    receiver_email = "iotdashboard2024@gmail.com"
    password = "dyqv qvrd yjzt eusa"
    yag = yagmail.SMTP(user=sender_email, password=password)

    subject = "Temperature Alert"
    body = f"The current temperature is {current_temp}. Would you like to turn on the fan?"
    yag.send(to=receiver_email, subject=subject, contents=body)
    print("Sent!")



# Function to turn the motor ON
def turn_motor_on():
    GPIO.output(ENA, GPIO.HIGH)  # Enable the motor
    GPIO.output(IN1, GPIO.LOW)   # Set direction
    GPIO.output(IN2, GPIO.HIGH)  # Set direction
    print("Motor is ON")

# Function to turn the motor OFF
def turn_motor_off():
    GPIO.output(ENA, GPIO.LOW)   # Disable the motor
    GPIO.output(IN1, GPIO.HIGH)  # Set to stop
    GPIO.output(IN2, GPIO.LOW)   # Set to stop
    print("Motor is OFF")

if __name__ == "__main__":
    app.run(port=5000)