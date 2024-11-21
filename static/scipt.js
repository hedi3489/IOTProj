let switchState = false
let fanSwitchState = false

// Function for the LED switch widget 
function toggleSwitch() {
    switchState = !switchState
    const lightbulb = document.getElementById('lightbulb')

    // Update lightbulb image based on switch state
    if (switchState) {
        lightbulb.src = '../static/lighton.png'
    } else {
        lightbulb.src = '../static/lightoff.png'
    }

    // Send data to the server to control the LED
    fetch('/toggle-led', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({ state: switchState })
    })
}

// Function for the Fan switch widget 
function toggleFan() {
    fanSwitchState = !fanSwitchState;
    const fanImage = document.getElementById('fan');

    // Update fan image based on switch state
    if (fanSwitchState) {
        fanImage.src = '../static/fanon.png';
    } else {
        fanImage.src = '../static/fanoff.png';
    }

    // Send data to the server to control the fan
    fetch('/toggle-fan', {
        method: 'POST',
        headers: {
        'Content-Type': 'application/json'
        },
        body: JSON.stringify({ state: fanSwitchState })
    });
}

// Function for to update LED state 
function updateLEDState() {
    fetch('/led-state')
    .then(response => response.json())
    .then(data => {
        switchState = data.led_state; // Update the LED switch state based on the server response
        const lightbulb = document.getElementById('lightbulb');

        // Update lightbulb image based on switch state
        if (switchState) {
            lightbulb.src = '../static/lighton.png';
            document.getElementById('switchLED').checked = true; // Set the checkbox to checked
        } else {
            lightbulb.src = '../static/lightoff.png';
            switchLED.checked = false; // Set the checkbox to unchecked
        }
    })
    .catch(error => console.error('Error fetching LED state:', error));
}

// Function to update the Fan state 
function updateFanState() {
    fetch('/fan-state')
    .then(response => response.json())
    .then(data => {
        fanSwitchState = data.fan_state; // Update the fanSwitchState based on the server response
        const fanImage = document.getElementById('fan');

        // Update fan image based on switch state
        if (fanSwitchState) {
            fanImage.src = '../static/fanon.png';
            fanSwitch.checked = true; // Set the checkbox to checked
        } else {
            fanImage.src = '../static/fanoff.png';
            fanSwitch.checked = false; // Set the checkbox to checked
        }
    })
    .catch(error => console.error('Error fetching fan state:', error));
}

// Call this function when the page loads to check the initial fan state
window.onload = function() {
    updateFanState();
    updateLEDState();
};

// Set an interval to update fan reading every 2 seconds
setInterval(updateFanState, 2000);
setInterval(updateLEDState, 2000);

// Initialize JustGage for Temperature and Humidity
const temperatureGauge = new JustGage({
    id: "temperatureGauge",
    value: 0,
    min: -10,
    max: 50,
    title: "°C",
    label: "Temperature",
    gaugeWidthScale: 0.6,
    levelColors: ["#00bfae", "#f9a825", "#d50000"]
});

const humidityGauge = new JustGage({
    id: "humidityGauge",
    value: 0,
    min: 0,
    max: 100,
    title: "%",
    label: "Humidity",
    gaugeWidthScale: 0.6,
    levelColors: ["#2196f3", "#4caf50", "#ff9800"]
}); 

// Function to update the gauge values
function updateSensorData() {
    fetch('/read-sensor')
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        if (data.temperature && data.humidity) {
            temperatureGauge.refresh(data.temperature);
            humidityGauge.refresh(data.humidity);
        } else {
            console.error("Failed to fetch sensor data.");
        }
    })
    .catch(error => {
        console.error('There was a problem with the fetch operation:', error);
    });
}

// Set an interval to update sensor data every 5 seconds
setInterval(updateSensorData, 5000);
