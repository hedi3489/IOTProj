from flask import Flask, render_template, request, jsonify
import yagmail
import RPi.GPIO as GPIO
from Freenove_DHT import DHT
import time
import imaplib
import email
from email.header import decode_header
import threading

app = Flask(__name__)

# LED setup
LED_PIN = 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
# Initial LED state
led_state = False
GPIO.output(LED_PIN, GPIO.LOW)


# DHT11 sensor setup
DHT_PIN = 16
dht_sensor = DHT(DHT_PIN)

# Add a global variable to track the last email sent time
last_email_sent_time = 0  # Timestamp of the last email sent
email_cooldown = 5  # Cooldown period in seconds
email_lock = threading.Lock()  # Lock to ensure thread safety
last_brightness_state = False
subject = ''
body = ''


# Motor setup
ENA = 22  # Enable Pin
IN1 = 27  # Input Pin
IN2 = 17  # Input Pin
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(ENA, GPIO.OUT)
GPIO.setup(IN1, GPIO.OUT)
GPIO.setup(IN2, GPIO.OUT)
fan_state = False  # Initial fan state

@app.route('/')
def dashboard():
    GPIO.output(LED_PIN, GPIO.LOW)
    return render_template('index.html')

@app.route('/led-state', methods=['GET'])
def get_led_state():
    global led_state  # Make sure you have a variable to track the LED state
    return jsonify({'led_state': led_state})  # Return the current LED state


@app.route('/toggle-led', methods=['POST'])
def toggle_led():
    global led_state, last_brightness_state, subject, body, last_email_sent_time

    data = request.get_json()
    led_state = data['state']  # Update the LED state based on the request

    # Code to physically turn the LED on or off using GPIO
    if led_state and not last_brightness_state:
        # Turn on the LED
        GPIO.output(LED_PIN, GPIO.HIGH)
        subject = "Brightness"
        body = "It's gotten dark. Lights are turned on."
        send_email_with_cooldown(subject, body)  # Use cooldown-protected email sending
        last_brightness_state = led_state  # Update the brightness state
    elif not led_state and last_brightness_state:
        # Turn off the LED
        GPIO.output(LED_PIN, GPIO.LOW)
        subject = "Brightness"
        body = "It's bright in here. Lights off."
        send_email_with_cooldown(subject, body)  # Use cooldown-protected email sending
        last_brightness_state = led_state  # Update the brightness state

    return jsonify({'status': 'success', 'led_state': led_state})

def send_email_with_cooldown(subject, body):
    """Send email only if cooldown period has elapsed."""
    global last_email_sent_time

    with email_lock:  # Ensure only one thread can send emails at a time
        current_time = time.time()
        if current_time - last_email_sent_time > email_cooldown:
            # Cooldown has elapsed, send the email
            send_email(subject, body, False)
            last_email_sent_time = current_time  # Update the last email sent time
            print(f"Email sent: {subject}")
        else:
            # Cooldown is still active
            print(f"Email not sent due to cooldown. Time remaining: {email_cooldown - (current_time - last_email_sent_time):.2f} seconds")

# Toggling Fan
@app.route('/toggle-fan', methods=['POST'])
def toggle_fan():
    # fan control
    global fan_state

    data = request.get_json()
    # Parse JSON data
    switch_state = data['state']  # Get the state value

    if switch_state:
        turn_motor_on()  # Turn on fan
    else:
        turn_motor_off()  # Turn off fan

    fan_state = switch_state  # Update fan_state
    return jsonify({'success': True, 'fan_state': fan_state})  # Indicate success and return current fan state


@app.route('/fan-state', methods=['GET'])
def get_fan_state():
    global fan_state
    return jsonify({'fan_state': fan_state})  # Return the current fan state

# Data capture route for reading DHT11 sensor
@app.route('/read-sensor', methods=['GET'])
def read_sensor_once():
    for _ in range(15):  # Attempt to read sensor up to 15 times
        if dht_sensor.readDHT11() == 0:  # Only proceed if read is successful
            humidity = dht_sensor.getHumidity()
            temperature = dht_sensor.getTemperature()
            return jsonify({'temperature': temperature, 'humidity': humidity})
        time.sleep(0.1)  # Short delay before retrying

    return jsonify({'error': 'Failed to retrieve data from sensor'}), 500

# Function to send email
#def send_email(current_temp):
 #   yag = yagmail.SMTP(user="belhassinehedi308@gmail.com", password="mdmk palo kswz vyvj")
#
 #   subject = "Temperature Alert"
  #  body = f"The current temperature is {current_temp}. Would you like to turn on the fan?"
   # yag.send(to="belhassinehedi308@gmail.com", subject=subject, contents=body)
    #print("Sent!")
    #receive_emails()

# Function to send email
def send_email(title, message, receive_needed):
    yag = yagmail.SMTP(user="belhassinehedi308@gmail.com", password="mdmk palo kswz vyvj")
    yag.send(to="belhassinehedi308@gmail.com", subject=subject, contents=body)
    print("Sent!")
    if (receive_needed):
        receive_emails()

def check_email_response():
    yag = yagmail.SMTP('belhassinehedi308@gmail.com', 'mdmk palo kswz vyvj')

    while True:
        time.sleep(60)  # Check every minute
        try:
            inbox = yag.get_inbox(search_expression='UNSEEN')  # Fetch unread emails

            for email in inbox:
                if 'Temperature Alert' in email.subject:
                    if 'Yes' in email.body:
                        print("YES received")
                        turn_motor_on()
                    elif 'No' in email.body:
                        print("NO received")
                        turn_motor_off()
                    return  # Exit after handling the response
        except Exception as e:
            print(f"Error checking email: {e}")


def receive_emails():
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

# Function to read sensor and start a separate thread
def read_sensor_thread():
    while True:
        for _ in range(15):  # Attempt to read sensor up to 15 times
            if dht_sensor.readDHT11() == 0:  # Only proceed if read is successful
                humidity = dht_sensor.getHumidity()
                temperature = dht_sensor.getTemperature()

                # Check temperature and send email alert if needed
                if temperature > 24:
                    send_email(temperature)
                break
            time.sleep(0.1)  # Short delay before retrying

        time.sleep(60)  # Wait 1 minute before the next reading

# Function to turn the motor ON
def turn_motor_on():
    GPIO.output(ENA, GPIO.HIGH)  # Enable the motor
    GPIO.output(IN1, GPIO.LOW)   # Set direction
    GPIO.output(IN2, GPIO.HIGH)  # Set direction
    global fan_state
    fan_state = True
    print("Fan is ON")

# Function to turn the motor OFF
def turn_motor_off():
    GPIO.output(ENA, GPIO.LOW)   # Disable the motor
    GPIO.output(IN1, GPIO.HIGH)  # Set to stop
    GPIO.output(IN2, GPIO.LOW)   # Set to stop
    global fan_state
    fan_state = False
    print("Fan is OFF")

def cleanup():
    GPIO.cleanup()
    print("GPIO cleanup done")

if __name__ == "__main__":
    try:
        # Start the background thread for continuous sensor monitoring
        threading.Thread(target=read_sensor_thread, daemon=True).start()
        # Run the Flask app
        app.run(host="0.0.0.0", port=5000)
    except KeyboardInterrupt:
        cleanup()