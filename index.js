const express = require('express');
const cors = require('cors');
const BarnowlHci = require('barnowl-hci');

const app = express();
const port = 3001;

app.use(cors());
app.use(express.json());

let rssiValues = [];

let barnowl = new BarnowlHci();

barnowl.addListener(BarnowlHci.TestListener, {});

function scanForDevices(duration) {
  return new Promise((resolve) => {
    rssiValues = [];

    barnowl.on("raddec", (raddec) => {
      raddec.rssiSignature.forEach((entry) => {
        rssiValues.push(entry.rssi);
      });
    });

    setTimeout(() => {
      barnowl.removeAllListeners("raddec");
      resolve(rssiValues);
    }, duration);
  });
}

app.get('/api/devices', async (req, res) => {
  const duration = 5000;
  const threshold = parseInt(req.query.threshold, 10);
  const rssiData = await scanForDevices(duration);
  const filteredDevices = [];
  console.log(threshold);
  for (let i = 0; i < rssiData.length; i++) {
    console.log(rssiData[i]);
    if (rssiData[i] >= threshold) {
      filteredDevices.push(rssiData[i]);
    }
  }

  res.json({ count: filteredDevices.length });
});

app.listen(port, () => {
  console.log(`Node.js server running on http://localhost:${port}`);
});
