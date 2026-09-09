import React from 'react';
import { HardHat, ShieldAlert, Cpu, HeartPulse, ShieldCheck, MapPin, Radio, AlertTriangle, Users, GraduationCap, ChevronDown, ArrowDown, Wifi, Brain, LayoutDashboard, Bell, Server } from 'lucide-react';
import BrandPowered from '../components/BrandPowered';

function Home({ setActiveTab }) {
  return (
    <div className="home-container">
      {/* 50% Working Software Prototype Badge + Disclaimer */}
      <div className="glass-card prototype-banner">
        <div className="prototype-badge-row">
          <span className="prototype-badge">50% Working Software Prototype</span>
          <span className="prototype-badge-sub">Simulated Sensor Data</span>
        </div>
        <p className="prototype-note">
          This prototype demonstrates the software, AI prediction, simulated IoT sensor data, GPS tracking, and emergency SOS alert flow. Real hardware integration is planned in the next phase.
        </p>
      </div>

      {/* Hero Section */}
      <section className="hero-section glass-card">
        <div className="hero-text">
          <span className="project-tag">IoT & Machine Learning Integration</span>
          <h2 className="hero-title">AI-Powered Smart Helmet</h2>
          <div className="hero-brand-subtitle">
            <BrandPowered emphasis={true} className="hero-brand-powered" />
          </div>
          <p className="hero-abstract">
            An intelligent safety system that active-monitors motorcycle riders using integrated helmet sensors. By leveraging a Random Forest Machine Learning model, the helmet dynamically predicts accidents, detects rider impairment (alcohol/drowsiness), and dispatches automated emergency alerts via GSM/GPS in real-time.
          </p>
          <div className="hero-buttons">
            <button className="btn-primary" onClick={() => setActiveTab('dashboard')}>
              Launch Live Dashboard
            </button>
            <button className="btn-secondary" onClick={() => setActiveTab('modules')}>
              Explore Modules
            </button>
          </div>
        </div>

        <div className="hero-graphics">
          <div className="helmet-3d-mock">
            <div className="radar-ping"></div>
            <HardHat className="helmet-logo" />
            <div className="ring ring-1"></div>
            <div className="ring ring-2"></div>
          </div>
        </div>
      </section>

      {/* Problem Definition & Motivation */}
      <section className="home-split">
        <div className="glass-card problem-box">
          <h3 className="section-title">
            <ShieldAlert size={22} className="text-danger" />
            Problem Definition
          </h3>
          <p>
            Road accidents involving two-wheelers account for a major portion of overall traffic fatalities. Key contributing factors include speed violations, riding under the influence of alcohol, and rider drowsiness.
          </p>
          <p>
            Crucially, a significant portion of fatalities occurs due to the <strong>"Golden Hour" delay</strong>—the critical time lag between the accident event and the arrival of medical emergency services. Traditional systems rely on bystanders to report accidents, which is highly unreliable in remote or night-time conditions.
          </p>
        </div>

        <div className="glass-card">
          <h3 className="section-title">Helmet Monitoring Modules</h3>
          <div className="stats-grid home-stats-grid">
            <div className="home-stat-item">
              <ShieldCheck size={18} className="text-safe" />
              <span className="home-stat-lbl">Accident Risk Monitoring</span>
            </div>
            <div className="home-stat-item">
              <Radio size={18} className="text-safe" />
              <span className="home-stat-lbl">Emergency SOS Alert</span>
            </div>
            <div className="home-stat-item">
              <HeartPulse size={18} className="text-safe" />
              <span className="home-stat-lbl">Alcohol Detection</span>
            </div>
            <div className="home-stat-item">
              <MapPin size={18} className="text-safe" />
              <span className="home-stat-lbl">GPS Location Tracking</span>
            </div>
            <div className="home-stat-item">
              <Cpu size={18} className="text-safe" />
              <span className="home-stat-lbl">AI-Based Risk Prediction</span>
            </div>
            <div className="home-stat-item">
              <HardHat size={18} className="text-safe" />
              <span className="home-stat-lbl">Real-Time Helmet Monitoring</span>
            </div>
          </div>
        </div>
      </section>

      {/* Core Features */}
      <section className="features-section">
        <h3 className="section-title">
          <ShieldCheck size={22} className="text-safe" />
          System Core Features
        </h3>
        <div className="features-grid">
          <div className="glass-card feature-card safe-feat">
            <div className="feature-icon">
              <Cpu size={24} />
            </div>
            <h3>Real-time ML Classification</h3>
            <p>Runs a Random Forest machine learning model backend using accelerometers, gyroscopes, speed, and environmental variables to predict rider safety levels.</p>
          </div>

          <div className="glass-card feature-card alert-feat">
            <div className="feature-icon">
              <Radio size={24} />
            </div>
            <h3>Emergency Alert System</h3>
            <p>In case of a detected crash, the system instantly triggers an automated SOS sequence, simulating emergency GSM SMS transmission to contacts and hospitals.</p>
          </div>

          <div className="glass-card feature-card">
            <div className="feature-icon">
              <HeartPulse size={24} />
            </div>
            <h3>Impairment Detection</h3>
            <p>Monitors alcohol levels inside the helmet cavity using gas sensors and analyzes drowsiness metrics to prevent riding when fatigued or intoxicated.</p>
          </div>

          <div className="glass-card feature-card">
            <div className="feature-icon">
              <MapPin size={24} />
            </div>
            <h3>GPS Coordinate Broadcasting</h3>
            <p>Continuous GPS coordinate logging enables pinpoint accuracy for locating the accident site on a graphical map interface for quick ambulance response.</p>
          </div>
        </div>
      </section>

      {/* Project Team Section */}
      <section className="team-section">
        <h3 className="section-title">
          <Users size={22} className="text-safe" />
          Project Team
        </h3>
        <div className="team-grid">
          {/* College Card */}
          <div className="glass-card team-college-card">
            <GraduationCap size={32} style={{ color: 'var(--gold)', marginBottom: '0.75rem' }} />
            <h4 className="team-college-name">Dr. M.G.R. Educational and Research Institute</h4>
            <div className="team-meta-tags">
              <span className="team-meta-tag">College Mini Project</span>
              <span className="team-meta-tag">AI &bull; IoT &bull; ML &bull; Road Safety</span>
            </div>
          </div>

          {/* Members */}
          {[
            { 
              name: 'Karthick S', 
              icon: <Brain size={24} className="team-member-icon" />, 
              badge: 'AI Prediction & Dashboard' 
            },
            { 
              name: 'Midhun Sathishkumar', 
              icon: <Cpu size={24} className="team-member-icon" />, 
              badge: 'IoT Sensors & Hardware' 
            },
            { 
              name: 'Kamesh Kumar J', 
              icon: <Server size={24} className="team-member-icon" />, 
              badge: 'Backend & Emergency Alert' 
            }
          ].map((member, idx) => (
            <div key={idx} className="glass-card team-member-card">
              <div className="team-avatar-container">
                <div className="team-avatar-glow"></div>
                <div className="team-avatar">{member.icon}</div>
              </div>
              <h4 className="team-member-name">{member.name}</h4>
              <div className="team-contrib-badge">{member.badge}</div>
              <span className="team-member-role">Team Member</span>
            </div>
          ))}
        </div>
      </section>

      {/* Future Hardware Integration Flow Diagram */}
      <section className="hw-flow-section">
        <h3 className="section-title">
          <Wifi size={22} className="text-safe home-hw-title-icon" />
          Future Hardware Integration
        </h3>
        <p className="home-hw-desc">
          System architecture showing how physical helmet sensors will connect through the microcontroller to the cloud backend and dashboard.
        </p>

        {/* Flow Diagram */}
        <div className="hw-flow-diagram">
          <div className="hw-flow-step">
            <div className="glass-card hw-flow-card">
              <HardHat size={28} style={{ color: 'var(--primary-red)' }} />
              <h4>Helmet Sensors</h4>
              <p>MPU6050, MQ-3, SW-420, NEO-6M GPS, Buzzer</p>
            </div>
            <ArrowDown size={24} className="hw-flow-arrow" />
          </div>

          <div className="hw-flow-step">
            <div className="glass-card hw-flow-card">
              <Cpu size={28} style={{ color: 'var(--gold)' }} />
              <h4>ESP32 / Arduino</h4>
              <p>Microcontroller Unit</p>
            </div>
            <ArrowDown size={24} className="hw-flow-arrow" />
          </div>

          <div className="hw-flow-step">
            <div className="glass-card hw-flow-card">
              <Wifi size={28} style={{ color: 'var(--primary-red)' }} />
              <h4>FastAPI Backend</h4>
              <p>Data Ingestion & API</p>
            </div>
            <ArrowDown size={24} className="hw-flow-arrow" />
          </div>

          <div className="hw-flow-step">
            <div className="glass-card hw-flow-card">
              <Brain size={28} style={{ color: 'var(--gold)' }} />
              <h4>AI/ML Risk Prediction</h4>
              <p>Random Forest Classifier</p>
            </div>
            <ArrowDown size={24} className="hw-flow-arrow" />
          </div>

          <div className="hw-flow-step">
            <div className="glass-card hw-flow-card">
              <LayoutDashboard size={28} style={{ color: 'var(--primary-red)' }} />
              <h4>React Live Dashboard</h4>
              <p>Real-time Monitoring UI</p>
            </div>
            <ArrowDown size={24} className="hw-flow-arrow" />
          </div>

          <div className="hw-flow-step">
            <div className="glass-card hw-flow-card hw-flow-card-alert">
              <Bell size={28} style={{ color: 'var(--color-danger)' }} />
              <h4>Emergency Alert</h4>
              <p>GPS + GSM SMS + SOS</p>
            </div>
          </div>
        </div>

        {/* Hardware Component Tags */}
        <div className="hw-components-list">
          <h4 className="home-hw-tag-header">Hardware Components</h4>
          <div className="hw-tags">
            {[
              'MPU6050 Accelerometer/Gyroscope',
              'MQ-3 Alcohol Sensor',
              'SW-420 Vibration Sensor',
              'NEO-6M GPS Module',
              'SIM800L GSM Module',
              'Buzzer',
              'ESP32 / Arduino'
            ].map((comp, idx) => (
              <span key={idx} className="hw-tag">{comp}</span>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
}

export default Home;
