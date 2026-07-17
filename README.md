# AI-Powered Smart Helmet with Accident Prediction and Emergency Alert System

A full-stack software prototype and demonstration dashboard designed for a college mini-project presentation. This system uses simulated sensor inputs to represent rider parameters, running a Random Forest Machine Learning classifier on the backend to predict safety levels, and displaying alerts and historical feeds in a modern React web interface.

---

## 📝 Abstract

Road safety for two-wheeler riders remains a critical global issue. Key hazards include overspeeding, riding under the influence of alcohol, and rider fatigue. To mitigate these risks and reduce the response lag of medical services (the "Golden Hour"), this project presents an **AI-Powered Smart Helmet**. The system integrates simulated IoT sensors (accelerometers, gyroscopes, gas sensors, and GPS localization modules) with an edge-like Machine Learning classifier. 

When a crash is predicted or impairment is detected, the system immediately locks the vehicle ignition, triggers alarms, and broadcasts coordinates in an emergency SOS SMS to rescue services and family contacts.

---

## 🚨 Problem Definition

Motorcycle riders represent a disproportionately high fraction of overall traffic fatalities. Major hazards include:
1. **Intoxicated Riding**: Alcohol usage compromises reflexes and motor controls.
2. **Drowsiness / Fatigue**: Rider exhaustion leads to micro-sleeps and swerving incidents.
3. **Golden Hour Delay**: Fatalities rise because emergency medical response is delayed, as accidents often occur without immediate bystanders.

---

## 👥 Project Team

| Name                    | Role         |
|-------------------------|--------------|
| Kamesh Kumar J          | Team Member  |
| Karthick S              | Team Member  |
| Midhun Sathishkumar     | Team Member  |

- **College**: Dr. M.G.R. Educational and Research Institute
- **Project Type**: College Mini Project
- **Domain**: AI, IoT, Machine Learning, Road Safety

---

## 🛠️ Technology Stack

- **Frontend**: React (Vite, JavaScript), Recharts (data visualizations), Lucide-React (vector iconography)
- **Styling**: Modern Vanilla CSS (dark mode theme, flexbox/grid, glassmorphism, keyframe alert animations)
- **Backend**: FastAPI (Python), Uvicorn (ASGI web server), scikit-learn & joblib (Machine Learning training & inference), pandas & numpy

---

## ✨ Features & Simulation Modes

1. **AI-Based Prediction**: Executes a real-time Random Forest Classifier predicting rider conditions: `Safe`, `At-Risk`, or `Danger`.
2. **Simulated Telemetry**: Feeds live speedometers, MQ-3 alcohol levels, blink fatigue indexes, vibration indexes, and 3-axis accelerometer/gyroscope signals.
3. **Emergency Alert Card**: Displays active crash details, Google Maps links, and GSM SIM800L dispatch logs during accidents.
4. **Interactive Demo Modes**:
   - `Safe`: Normal speed, low road vibrations, zero alcohol, alert eye blinks.
   - `Risky`: Overspeeding (85+ km/h), swerving orientation tilt angles.
   - `Drunk`: Elevated blood alcohol (MQ-3 gas index), triggering ignition lockout.
   - `Drowsy`: Fatigue blink rates (>80%), sounding warning buzzer alerts.
   - `Crash`: High vibration spike (>12 m/s²), high G-force acceleration, followed by speed drop to 0, sending emergency alerts.

---

## 🚀 Running the Project

### 1. Backend Setup & Run
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start backend server
python -m uvicorn main:app --host 127.0.0.1 --port 8080 --reload
```
The backend API documentation is available at `http://127.0.0.1:8080/docs`.

### 2. Frontend Setup & Run
```bash
# Navigate to frontend directory
cd frontend

# Install package dependencies
npm install

# Start local Vite development server
npm run dev
```
Open `http://localhost:5174/` in your web browser.

---

## 📸 Demo Screenshots to Capture

Use the following checklist for capturing screenshots during the live demonstration:

1. **Home Page** – Hero section with project title, abstract, and feature cards
2. **Home Page – Team** – The "Project Team" section showing college name and members
3. **Home Page – Hardware Flow** – The "Future Hardware Integration" flow diagram
4. **Dashboard – Safe Mode** – Green/cyan status, normal sensor readings
5. **Dashboard – Risky Mode** – Amber status, elevated speed and tilt
6. **Dashboard – Drunk Mode** – Red danger status, alcohol detection warning
7. **Dashboard – Drowsy Mode** – Fatigue warning, drowsiness alert active
8. **Dashboard – Crash Mode** – Crash detected SOS card, Google Maps link, emergency dispatch
9. **Modules Page** – Full list of 8 project modules

---

## 🎤 Presentation Demo Flow

Follow this sequence during the live project presentation:

1. **Open the Home page** → Explain the project title, abstract, and problem definition.
2. **Scroll to Project Team** → Show the team members and college affiliation.
3. **Scroll to Hardware Integration** → Walk through the future sensor-to-cloud architecture.
4. **Navigate to Live Dashboard** → Point out the prototype badge and simulation disclaimer.
5. **Start in Safe Mode** → Show the green "SAFE" prediction with stable sensors.
6. **Switch to Risky Mode** → Highlight the amber "AT-RISK" state with elevated speed.
7. **Switch to Drunk Mode** → Show "DANGER" state with alcohol detection warning.
8. **Switch to Drowsy Mode** → Demonstrate fatigue warning and drowsiness alerts.
9. **Switch to Crash Mode** → Showcase the emergency SOS card, Google Maps link, and GSM dispatch log.
10. **Reset to Safe Mode** → Confirm real-time mode switching.
11. **Navigate to Modules page** → Walk through all 8 project modules.
12. **Open Swagger Docs** (`http://127.0.0.1:8080/docs`) → Briefly show the live API endpoints.

---

## 🔧 Hardware Future Scope

For physical hardware prototyping, the software can be interfaced with microcontrollers using:
- **MPU6050 Accelerometer/Gyroscope**: Captures 3-axis linear acceleration and angular velocity.
- **MQ-3 Gas Sensor**: Measures blood alcohol concentration from breath.
- **SW-420 Sensor**: High-sensitivity vibration sensor to register physical impacts.
- **NEO-6M GPS Module**: Parses satellite coordinates.
- **SIM800L GSM Module**: Sends cellular SMS alerts containing GPS links.
- **Active Buzzer**: Sounds audible warning alerts inside the helmet.
- **ESP32 Microcontroller**: Central processing unit running firmware logic.
