import React from 'react';
import { 
  Cpu, 
  Eye, 
  AlertTriangle, 
  Smartphone, 
  Map, 
  Activity, 
  Database,
  Flame,
  HardHat,
  Bell
} from 'lucide-react';

function Modules() {
  const modulesList = [
    {
      title: "Sensor Monitoring System",
      icon: <Cpu size={24} />,
      desc: "Integrates multiple safety and physiological sensors inside the helmet cavity, polling helmet data at a high frequency (Hz) to capture mechanical movements, surrounding air composition, and optical readings.",
      specs: ["MPU6050 Accelerometer/Gyro", "MQ-3 Ethanol Vapor Sensor", "SW-420 Mechanical Sensor"]
    },
    {
      title: "AI/ML Risk Prediction using Random Forest",
      icon: <Activity size={24} />,
      desc: "Processes 10-dimensional feature arrays (accelerations, speeds, tilts, drowsiness scores, and alcohol metrics) through a trained Random Forest model to instantly predict rider risk states: Safe, At-Risk, or Danger.",
      specs: ["Random Forest Classifier", "Feature Matrix Mapping", "Edge AI Inference Pipeline"]
    },
    {
      title: "Alcohol Detection using MQ-3",
      icon: <Flame size={24} />,
      desc: "Uses anMQ-3 gas sensor inside the chin-guard to detect blood alcohol concentration (BAC) from the rider's breath. If values cross 0.35 mg/L, the system triggers an ignition lockout relay.",
      specs: ["Ethanol Vapor Calibration", "Ignition Relay Interlock", "Buzzer Warning Trigger"]
    },
    {
      title: "Drowsiness Detection",
      icon: <Eye size={24} />,
      desc: "Simulates blink patterns and eye-closure index. If eyelids remain closed for consecutive frames (representing sleep or fatigue), a high-pitch warning alarm sounds inside the helmet to wake the rider.",
      specs: ["Optical IR Sensor Tracker", "Eye Closure Duration Index", "Local Buzzer Alarm"]
    },
    {
      title: "Crash and Impact Detection",
      icon: <AlertTriangle size={24} />,
      desc: "Analyzes vertical and lateral G-forces. When an acceleration impulse exceeds 4.0G coupled with a massive mechanical vibration spike (>12 m/s²), the system automatically flags a crash event.",
      specs: ["SW-420 Vibration Spike", "MPU6050 Impulse Peak (>4G)", "Tilt Spillover Gyro Rates"]
    },
    {
      title: "GPS Location Tracking",
      icon: <Map size={24} />,
      desc: "Continuously tracks and buffers current latitude and longitude coordinates. Provides exact coordinates to coordinate rescue efforts in case of an accident.",
      specs: ["NEO-6M GPS Receiver", "NMEA Coordinate Parsing", "Dynamic Drift Tracking"]
    },
    {
      title: "GSM Emergency SMS Alert",
      icon: <Smartphone size={24} />,
      desc: "Instantly formats and transmits an SOS SMS to pre-saved emergency contacts and ambulance services. Includes a direct Google Maps link of the crash site.",
      specs: ["SIM800L GSM Transceiver", "AT SMS Command Pipeline", "Emergency Location Broadcasting"]
    },
    {
      title: "Data Logging / Dashboard Monitoring",
      icon: <Database size={24} />,
      desc: "Ingests and stores real-time telemetry datasets. Renders live graphs, status indicators, and emergency indicators in a clean, modern interface for remote safety monitoring.",
      specs: ["Time-Series Data Buffer", "Recharts Visual Analytics", "FastAPI Data Streams"]
    }
  ];

  const hardwareFutureScope = [
    { component: "MPU6050 Module", purpose: "Tracks 3-axis acceleration and gyroscope data to detect high-impact falls and swerving movements." },
    { component: "MQ-3 Sensor", purpose: "Calibrated to detect breath alcohol levels inside the helmet cavity to prevent drunk riding." },
    { component: "SW-420 Sensor", purpose: "Registers high mechanical vibration shock waves caused by sudden collisions or tarmac impact." },
    { component: "NEO-6M GPS", purpose: "Captures satellite localization data to broadcast coordinates to emergency systems." },
    { component: "SIM800L GSM", purpose: "Houses a cellular SIM card to send text messages (SMS) to designated contacts during emergencies." },
    { component: "Local Buzzer", purpose: "Sounds an loud, immediate alarm inside the helmet for drowsiness and intoxication alerts." },
    { component: "ESP32 / Arduino", purpose: "Acts as the central microcontroller unit to process sensor inputs, run logic, and coordinate modules." }
  ];

  return (
    <div className="modules-container">
      <section className="glass-card">
        <h2 className="hero-title" style={{ fontSize: '2.2rem', marginBottom: '0.5rem' }}>Project Modules</h2>
        <p className="hero-abstract" style={{ fontSize: '0.95rem', margin: 0 }}>
          Detailed technical breakdown of the hardware components, firmware algorithms, and artificial intelligence interfaces used to construct the Smart Helmet prototype.
        </p>
      </section>

      <div className="modules-grid">
        {modulesList.map((mod, idx) => (
          <div key={idx} className="glass-card module-card">
            <div className="module-head">
              <div className="module-icon-wrap">
                {mod.icon}
              </div>
              <h3>{mod.title}</h3>
            </div>
            <p className="module-desc">{mod.desc}</p>
            <div className="module-spec">
              <div className="spec-title">Technical Stack</div>
              <div className="spec-list">
                {mod.specs.map((spec, sIdx) => (
                  <span key={sIdx} className="spec-tag">{spec}</span>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Hardware Integration - Future Scope Section */}
      <section className="glass-card" style={{ marginTop: '1.5rem' }}>
        <h3 className="section-title">
          <HardHat size={22} className="text-safe" />
          Hardware Integration – Future Scope
        </h3>
        <p className="home-hw-desc" style={{ marginBottom: '1.5rem' }}>
          While this prototype demonstrates the complete software orchestration, prediction engine, and alert systems, a physical hardware prototype can be constructed using the following components:
        </p>
        <div className="hw-future-grid">
          {hardwareFutureScope.map((hw, idx) => (
            <div key={idx} className="hw-future-card">
              <div className="hw-future-header">
                <span className="hw-future-dot"></span>
                <h4 className="hw-future-name">{hw.component}</h4>
              </div>
              <p className="hw-future-desc">{hw.purpose}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}

export default Modules;
