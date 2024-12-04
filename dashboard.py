from flask import Flask, render_template, request, jsonify
import yagmail
import RPi.GPIO as GPIO
from Freenove_DHT import DHT
import time
import imaplib
import email
from email.header import decode_header
import threading
import requests
from DatabaseHelper import DBHelper

app = Flask(__name__)

# === GPIO Setup ===
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LED setup
LED_PIN = 18
GPIO.setup(LED_PIN, GPIO.OUT)
led_state = False
GPIO.output(LED_PIN, GPIO.LOW)

# DHT11 sensor setup
DHT_PIN = 20
dht_sensor = DHT(DHT_PIN)
temperature_threshold = 24

# Motor (fan) setup
ENA = 22
IN1 = 27
IN2 = 17
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
fan_state = False

# === Global Variables ===
last_email_sent_time = 0
email_cooldown = 5  # Cooldown period in seconds
email_lock = threading.Lock()
last_brightness_state = False
subject = ''
body = ''
db_helper = DBHelper('users.db')

# === Routes ===

@app.route('/get_user_data', methods=['POST'])
def get_user_data():
    rfid_uid = request.json.get('rfid_uid')  # Get the UID from the request body
    global temperature_threshold
    if not rfid_uid:
        return jsonify({"error": "Missing RFID UID"}), 400
    
    user_record = db_helper.fetch_by_rfid(rfid_uid)
    if user_record:
        # Structure the data as a JSON object
        user_data = {
            "rfid_id": user_record[0],
            "temperature_threshold": user_record[1],
            "light_intensity_threshold": user_record[2]
        }
        temperature_threshold = int(user_record[1])
        if temperature_threshold < 24 :
            print(temperature_threshold)
            send_email_with_cooldown("Someone's home", "Hedi just came home. Adjusting thresholds.")
        elif  temperature_threshold > 24 :
            send_email_with_cooldown("Someone's home", "Youssef just came home. Adjusting thresholds.")
        return jsonify(user_data), 200
    else:
        return jsonify({"error": "RFID not found"}), 404


@app.route('/')
def dashboard():
    """Serve the dashboard."""
    GPIO.output(LED_PIN, GPIO.LOW)
    return render_template('index.html')

@app.route('/led-state', methods=['GET'])
def get_led_state():
    """Return the current LED state."""
    return jsonify({'led_state': led_state})

@app.route('/toggle-led', methods=['POST'])
def toggle_led():
    """Toggle the LED state and send email notifications with cooldown."""
    global led_state, last_brightness_state

    data = request.get_json()
    led_state = data['state']

    if led_state and not last_brightness_state:
        GPIO.output(LED_PIN, GPIO.HIGH)
        send_email_with_cooldown("Brightness", "It's gotten dark. Lights are turned on.")
        last_brightness_state = led_state
    elif not led_state and last_brightness_state:
        GPIO.output(LED_PIN, GPIO.LOW)
        send_email_with_cooldown("Brightness", "It's bright in here. Lights off.")
        last_brightness_state = led_state

    return jsonify({'status': 'success', 'led_state': led_state})

@app.route('/toggle-fan', methods=['POST'])
def toggle_fan():
    """Toggle the fan state."""
    global fan_state

    data = request.get_json()
    fan_state = data['state']

    if fan_state:
        turn_motor_on()
    else:
        turn_motor_off()

    return jsonify({'success': True, 'fan_state': fan_state})

@app.route('/fan-state', methods=['GET'])
def get_fan_state():
    """Return the current fan state."""
    return jsonify({'fan_state': fan_state})

@app.route('/read-sensor', methods=['GET'])
def read_sensor_once():
    """Read temperature and humidity data from the sensor."""
    for _ in range(15):
        if dht_sensor.readDHT11() == 0:
            return jsonify({'temperature': dht_sensor.getTemperature(), 'humidity': dht_sensor.getHumidity()})
        time.sleep(0.1)

    return jsonify({'error': 'Failed to retrieve data from sensor'}), 500

@app.route('/devices', methods=['GET'])
def get_devices():
    """Fetch device information from a remote API."""
    try:
        threshold = request.args.get('threshold', default=-100, type=int)
        response = requests.get(f'http://localhost:3001/api/devices?threshold={threshold}')
        return jsonify(response.json())
    except requests.exceptions.RequestException:
        return jsonify({'error': 'Could not fetch devices'}), 500

@app.route('/mqtt-data', methods=['POST'])
def handle_mqtt_data():
    try:
        data = request.get_json()
        topic = data['topic']
        rfid_id = data['payload']

        # Use your database library to store the data
        if (db_helper.fetch_by_rfid(rfid_id)):
            print('row exists')

        return jsonify({'status': 'success', 'message': 'Data saved successfully'}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# === Helper Functions ===
def send_email_with_cooldown(subject, body):
    """Send an email with a cooldown to prevent spam."""
    global last_email_sent_time

    with email_lock:
        current_time = time.time()
        if current_time - last_email_sent_time > email_cooldown:
            send_email(subject, body, receive_needed=False)
            last_email_sent_time = current_time
            print(f"Email sent: {subject}")
        else:
            print(f"Email not sent due to cooldown. Time remaining: {email_cooldown - (current_time - last_email_sent_time):.2f} seconds")

def send_email(subject, body, receive_needed):
    """Send an email and optionally check for responses."""
    try:
        yag = yagmail.SMTP(user="belhassinehedi308@gmail.com", password="mdmk palo kswz vyvj")
        yag.send(to="belhassinehedi308@gmail.com", subject=subject, contents=body)
        print("Email sent!")
        if receive_needed:
            check_email_response()
    except Exception as e:
        print(f"Failed to send email: {e}")

def check_email_response():
    """Check email responses to control the fan."""
    # Email configuration
    SRVR = 'imap.gmail.com'
    PORT = 993
    MAIL = 'belhassinehedi308@gmail.com'
    PSWD = 'mdmk palo kswz vyvj'

    # Connect to the server
    mail = imaplib.IMAP4_SSL(SRVR, PORT)
    while True:
        time.sleep(20)
        try:
            mail.login(MAIL, PSWD)
            mail.select("inbox")
            status, data = mail.search(None, '(SUBJECT "Temperature Alert")')  # Search for emails with the subject "Temperature Alert"
            email_ids = data[0].split()  # Get the list of email IDs matching the search
            if email_ids:
                latest_email_id = email_ids[-1]  # Fetch the latest "Temperature Alert" email
                status, msg_data = mail.fetch(latest_email_id, '(RFC822)')
                for response_part in msg_data:
                    if isinstance(response_part, tuple):
                        msg = email.message_from_bytes(response_part[1])
                        subject, encoding = decode_header(msg['Subject'])[0]
                        if isinstance(subject, bytes):
                            subject = subject.decode(encoding if encoding else 'utf-8')

                        print(f"Subject: {subject}")
                        # Check if the email is multipart
                        if msg.is_multipart():
                            for part in msg.walk():
                                content_type = part.get_content_type()
                                content_disposition = str(part.get('Content-Disposition'))
                                if 'attachment' not in content_disposition:
                                    body = part.get_payload(decode=True)
                                    if body:
                                        body = body.decode()  # Decode to string
                                        print(f"Body: {body}")
                                        # Check for 'Y' in the body
                                        if 'Y' in body:
                                            turn_motor_on()
                                        elif 'n' in body:
                                            turn_motor_off()
                        else:
                            # Handle single-part email
                            body = msg.get_payload(decode=True)
                            if body:
                                body = body.decode()
                                print(f"Body: {body}")
                                # Check for 'Y' in the body
                                if 'Y' in body:
                                    turn_motor_on()
                                elif 'n' in body:
                                    turn_motor_off()
            else:
                print("No 'Temperature Alert' emails found.")
        except Exception as e:
            print(f"Failed to receive emails: {e}")
        finally:
            mail.logout()  # Logout and close the connection

def turn_motor_on():
    """Turn the motor on."""
    GPIO.output(ENA, GPIO.HIGH)
    GPIO.output(IN1, GPIO.LOW)
    GPIO.output(IN2, GPIO.HIGH)
    global fan_state
    fan_state = True
    print("Fan is ON")

def turn_motor_off():
    """Turn the motor off."""
    GPIO.output(ENA, GPIO.LOW)
    GPIO.output(IN1, GPIO.HIGH)
    GPIO.output(IN2, GPIO.LOW)
    global fan_state
    fan_state = False
    print("Fan is OFF")

# === Background Threads ===
def read_sensor_thread():
    print("reading temp")
    global temperature_threshold
    """Continuously monitor the sensor and send alerts."""
    while True:
        for _ in range(15):
            if dht_sensor.readDHT11() == 0:
                temp = dht_sensor.getTemperature()
                time.sleep(5)
                print(temperature_threshold)
                if temp >= temperature_threshold:
                    send_email("Temperature Alert", f"The current temperature is {temp}. Would you like to turn on the fan?", receive_needed=True)
                break
            time.sleep(0.1)
        time.sleep(60)

# === Cleanup ===
def cleanup():
    """Cleanup GPIO resources on exit."""
    GPIO.cleanup()
    print("GPIO cleanup done")

# === Main Entry Point ===
if __name__ == "__main__":
    try:
        threading.Thread(target=read_sensor_thread, daemon=True).start()
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        cleanup()
