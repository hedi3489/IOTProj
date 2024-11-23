const mqttBrokerURL = 'ws://172.20.10.2:9001';  // Replace with the WebSocket port of your broker
const client = mqtt.connect(mqttBrokerURL);
let brightness;  // Declare the variable

client.on('connect', function () {
    console.log('Connected to MQTT broker');
    // Subscribe to the brightness and lights topics
    client.subscribe('home/brightness', function (err) {
        if (!err) {
            console.log('Subscribed to home/brightness topic');
        } else {
            console.error('Subscription error:', err);
        }
    });
    // client.subscribe('home/lights', function (err) {
    //     if (!err) {
    //         console.log('Subscribed to home/lights topic');
    //     } else {
    //         console.error('Subscription error:', err);
    //     }
    // });
});

client.on('message', function (topic, message) {

    // Parse and handle the message
    if (topic === 'home/brightness') {
        brightness = parseInt(message.toString(), 10);
        console.log('Received brightness:', brightness);

        // Update the HTML element with the brightness value
        document.getElementById('brightness').innerText = brightness;

        // Automatically toggle LED based on brightness
        if (brightness < 400) {
            toggleLED(true);  // Turn on LED
            
        } else {
            toggleLED(false); // Turn off LED
        }
    }

    // if (topic === 'home/lights') {
    //     const lightStatus = message.toString();
    //     console.log('Lights status:', lightStatus);

    //     // If lights are turned on, trigger an email to notify
    //     if (lightStatus === "on") {
    //         sendEmail("The lights have been turned on due to low brightness.");
    //     }
    // }
});

// Function to toggle LED through Flask backend
function toggleLED(state) {
    fetch('/toggle-led', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: state })
    })
    .then(response => response.json())
    .then(data => console.log('LED toggled:', data))
    .catch(error => console.error('Error toggling LED:', error));
}

// Function to send an email to notify that lights are turned on
// function sendEmail(message) {
//     fetch('/send-email-lights', {
//         method: 'POST',
//         headers: { 'Content-Type': 'application/json' },
//         body: JSON.stringify({ message: message })
//     })
//     .then(response => response.json())
//     .then(data => console.log('Email sent:', data))
//     .catch(error => console.error('Error sending email:', error));
// }

// client.on('error', function (error) {
//     console.error('MQTT Error:', error);
// });
