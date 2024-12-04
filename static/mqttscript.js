const mqttBrokerURL = 'ws://172.20.10.3:9001';  // Replace with the WebSocket port of your broker
const client = mqtt.connect(mqttBrokerURL);
let brightness;  // Declare the variable
let light_intensity_threshold;
light_intensity_threshold =  400;

client.on('connect', function () {
    console.log('Connected to MQTT broker');
    // Subscribe to the brightness and lights topics
    client.subscribe('home/brightness', function (err) {
        if (!err) {
            console.log('Subscribed to home/brightness topic');
        } else {
            console.error('Subscription error:', err);
        }
    });client.subscribe('home/rfid', function (err) {
        if (!err) {
            console.log('Subscribed to home/rfid topic');
        } else {
            console.error('Subscription error:', err);
        }
    });
});

client.on('message', function (topic, message) {

    // Parse and handle the message
    if (topic === 'home/brightness') {
        brightness = parseInt(message.toString(), 10);
        console.log('Received brightness:', brightness);

        // Update the HTML element with the brightness value
        document.getElementById('brightness').innerText = brightness;

        // Automatically toggle LED based on brightness
        if (brightness < light_intensity_threshold) {
            toggleLED(true);  // Turn on LED
            
        } else {
            toggleLED(false); // Turn off LED
        }
    }
    // if (topic === 'home/rfid') {
    //     console.log(message.toString());
    //     ID = JSON.parse(message.toString());
    //     fetch('http://127.0.0.1:5000/mqtt-data', {
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/json',
    //         },
    //         body: JSON.stringify(ID),
    //     })
    //     .then(response => response.json())
    //     .then(result => console.log('Data sent to Flask:', result))
    //     .catch(error => console.error('Error sending data:', error));
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

client.on('message', (topic, message) => {
    if (topic === 'home/rfid') {
        try {
            const parsedMessage = JSON.parse(message.toString());
            const rfidUid = parsedMessage.uid;
            console.log("RFID UID Received:", rfidUid);

            // Call the function to fetch user data
            handleRFIDRead(rfidUid);
        } catch (err) {
            console.error("Error parsing message:", err);
        }
    }
});


const handleRFIDRead = (rfidUid) => {
    // Send the UID to the backend
    fetch('http://127.0.0.1:5000/get_user_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ rfid_uid: rfidUid })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Failed to fetch user data');
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            console.error("Error:", data.error);
        } else {
            console.log("User Data:", data);
            // Update the dashboard with user data
            document.getElementById('user').innerText = data.rfid_id;
            document.getElementById('tempThreshold').innerText = data.temperature_threshold;
            document.getElementById('lightThreshold').innerText = data.light_intensity_threshold;
            light_intensity_threshold = data.light_intensity_threshold;
            profileIcon = document.querySelector('.profile-icon img');
            if(data.rfid_id == "A3:D6:D4:24"){
                profileIcon.src = "../static/hedi.jpg";
            }
            if(data.rfid_id == "03:97:CB:F7"){
                profileIcon.src = "../static/uzi.jpg";
            }
            
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
};