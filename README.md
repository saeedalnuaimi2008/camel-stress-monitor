# Camel Stress Monitor

### The ultimate smart telemetry and heat stress tracker built to keep camels healthy, hydrated, and performing at their peak.

---

## What Is This?

Ever wondered how camel farmers or race trainers know if their camels are getting dangerously overheated before it is too late?

Camels are tough, so they do not show when they are struggling until they are severely exhausted. Camel Stress Monitor solves that. It is a real-time web dashboard that takes temperature and humidity data from the air, combines it with how much the camel is actually moving around, and gives farmers an instant, easy-to-read health status.

No complex math degree needed—just clean visuals, auto-alerts, and real-time updates.

---

## Key Features

- Instant Heat Risk Score: Automatically combines heat and humidity into a single risk number so you know if the weather is safe or dangerous.
- Smart Movement Tracking: Compares a camel movement over the past week against its normal monthly baseline. If movement drops hard during a heatwave, the app flags it immediately.
- Plain English Alerts: No confusing technical terms. The dashboard tells farm hands directly: "STATUS GOOD", "HEAT WARNING: FILL WATER TROUGHS", or "HIGH RISK ALERT: CHECK CAMEL NOW".
- Live Hardware Ready: Switch seamlessly between testing on 60 days of simulated data or plugging in an actual ESP32 microchip sensor setup via USB.

---

## How It Works (In Simple Terms)

1. Weather Check: It reads ambient temperature and humidity to figure out how hot it actually feels to livestock.
2. Activity Check: It monitors daily movement. If a camel is moving way less than usual (like dropping below 70% of its normal routine), something is wrong.
3. The Warning Engine: High Heat + Low Movement = Immediate Alert. The app flags potential heat sickness or weakness early so farm managers can step in before it becomes an emergency.

---

## Project Structure

```text
camel-stress-monitor/
├── modules/
│   ├── generator.py      # Generates 60 days of realistic test telemetry
│   └── math_engine.py    # Math logic for heat indexes and movement averages
├── app.py                # Main Streamlit dashboard interface
├── requirements.txt      # List of required Python packages
├── .gitignore            # Keeps junk files off Git
└── README.md             # You are here
```

---

## Quick Start Guide

Want to run this on your computer? Here is how to set it up in under 2 minutes:

1. Clone the repo:
   ```bash
   git clone [https://github.com/YOUR_GITHUB_USERNAME/camel-stress-monitor.git](https://github.com/YOUR_GITHUB_USERNAME/camel-stress-monitor.git)
   cd camel-stress-monitor
   ```

2. Spin up your virtual environment & install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Launch the dashboard:
   ```bash
   streamlit run app.py
   ```

Open up http://localhost:8501 in your browser and check it out.
