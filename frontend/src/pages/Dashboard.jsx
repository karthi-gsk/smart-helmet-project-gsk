import React, { useState, useEffect } from 'react';
import { 
  fetchLiveData, 
  fetchAlert, 
  setDemoMode, 
  resetAlert 
} from '../api';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip 
} from 'recharts';
import { 
  Gauge, 
  Activity, 
  Flame, 
  MapPin, 
  ShieldAlert, 
  Navigation, 
  Eye, 
  RefreshCw,
  Send,
  AlertTriangle,
  ServerCrash
} from 'lucide-react';

function Dashboard() {
  const [liveData, setLiveData] = useState(null);
  const [alertData, setAlertData] = useState(null);
  const [activeMode, setActiveMode] = useState('safe');
  const [apiError, setApiError] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);

  // Poll server for data
  useEffect(() => {
    let active = true;

    const getData = async () => {
      try {
        const data = await fetchLiveData();
        const alert = await fetchAlert();
        if (active) {
          setLiveData(data);
          setAlertData(alert);
          setActiveMode(data.demo_mode);
          setApiError(false);
        }
      } catch (err) {
        console.error(err);
        if (active) {
          setApiError(true);
        }
      }
    };

    // Initial fetch
    getData();

    const interval = setInterval(getData, 1000);

    return () => {
      active = false;
      clearInterval(interval);
    };
  }, []);

  const handleModeChange = async (mode) => {
    setActionLoading(true);
    // Clear prediction status to avoid showing stale state
    setLiveData(prev => prev ? {
      ...prev,
      prediction: {
        status: 'Loading...',
        class_probabilities: { Safe: 0, 'At-Risk': 0, Danger: 0 }
      }
    } : null);
    try {
      await setDemoMode(mode);
      setActiveMode(mode);
      // Fetch latest data immediately!
      const data = await fetchLiveData();
      const alert = await fetchAlert();
      setLiveData(data);
      setAlertData(alert);
    } catch (err) {
      console.error(err);
      alert(`Error toggling mode: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  const handleResetAlert = async () => {
    setActionLoading(true);
    try {
      await resetAlert();
      setActiveMode('safe');
      const data = await fetchLiveData();
      const alert = await fetchAlert();
      setLiveData(data);
      setAlertData(alert);
    } catch (err) {
      console.error(err);
      alert(`Error resetting alert: ${err.message}`);
    } finally {
      setActionLoading(false);
    }
  };

  if (apiError) {
    return (
      <div className="glass-card" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem', textAlign: 'center', gap: '1.5rem' }}>
        <ServerCrash size={64} className="text-danger" style={{ animation: 'swing 1.5s infinite alternate' }} />
        <h2>Backend Connection Offline</h2>
        <p style={{ color: '#9ca3af', maxWidth: '400px' }}>
          Could not establish connection to the FastAPI server at `localhost:8080`. Please make sure the Python server is running.
        </p>
        <button className="btn-primary" onClick={() => window.location.reload()}>
          <RefreshCw size={16} style={{ marginRight: '0.5rem', display: 'inline-block', verticalAlign: 'middle' }} />
          Retry Connection
        </button>
      </div>
    );
  }

  if (!liveData || !alertData) {
    return (
      <div className="glass-card" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', padding: '6rem' }}>
        <div className="pulse-dot" style={{ width: '20px', height: '20px', backgroundColor: '#00f2fe' }}></div>
        <span style={{ marginLeft: '1rem' }}>Initializing sensor feeds...</span>
      </div>
    );
  }

  const { sensor_data, prediction, history } = liveData;
  const { status, class_probabilities } = prediction;
  const isAlertActive = alertData.is_active;

  const chartData = (history && history.length > 0) ? history : [
    { timestamp: '00:00', speed: 0, vibration: 0 }
  ];

  const getStatusClass = () => {
    if (status === 'Safe') return 'status-safe';
    if (status === 'At-Risk') return 'status-at-risk';
    if (status === 'Danger') return 'status-danger';
    return '';
  };

  return (
    <div className="dashboard-container">
      {/* Simulation Disclaimer banner */}
      <div className="glass-card" style={{ borderLeft: '4px solid var(--gold)', background: 'rgba(212, 175, 55, 0.04)', padding: '1rem 1.5rem', borderRadius: '12px', display: 'flex', alignItems: 'center', gap: '1rem' }}>
        <AlertTriangle className="text-safe" size={20} style={{ flexShrink: 0 }} />
        <div style={{ flex: 1 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.35rem', flexWrap: 'wrap' }}>
            <span className="prototype-badge" style={{ fontSize: '0.7rem', padding: '0.25rem 0.6rem' }}>50% Working Software Prototype</span>
            <span className="prototype-badge-sub" style={{ fontSize: '0.65rem', padding: '0.2rem 0.5rem' }}>Simulated Sensor Data</span>
          </div>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', margin: 0, lineHeight: '1.4' }}>
            <strong>Software Prototype Notice:</strong> This demo uses simulated sensor data. Real hardware integration is planned using MPU6050 accelerometer/gyroscope, MQ-3 alcohol sensor, NEO-6M GPS module, SIM800L GSM module, SW-420 vibration sensor, buzzer, and microcontroller.
          </p>
        </div>
      </div>

      {/* Demo Controls Bar */}
      <section className="glass-card demo-bar">
        <div className="demo-title-group">
          <h2>Rider Simulation Modes</h2>
          <p>Toggle rider behaviors to simulate different sensor values and AI predictions in real-time.</p>
        </div>
        <div className="demo-buttons-group">
          {['Safe', 'Risky', 'Drunk', 'Drowsy', 'Crash'].map((mode) => (
            <button
              key={mode}
              className={`btn-demo ${activeMode === mode.toLowerCase() ? 'active' : ''}`}
              data-mode={mode.toLowerCase()}
              disabled={actionLoading}
              onClick={() => handleModeChange(mode.toLowerCase())}
            >
              {mode}
            </button>
          ))}
        </div>
      </section>

      {/* AI Prediction Status Card */}
      <section className={`glass-card prediction-status-card ${getStatusClass()}`}>
        <div className="pred-info">
          <h3>AI Prediction Engine (Random Forest)</h3>
          <div className="pred-status-value">
            <span className="pulse-dot"></span>
            <span>RIDER STATE: {status.toUpperCase()}</span>
          </div>
          <p style={{ fontSize: '0.8rem', color: '#9ca3af', marginTop: '0.5rem' }}>
            {status === 'Safe' && 'Rider condition normal. All sensor values are within safe limits.'}
            {status === 'At-Risk' && 'Rider warning triggered: speed thresholds or sway vectors exceed safe margins.'}
            {status === 'Danger' && (
              activeMode === 'drunk' ? 'CRITICAL DANGER: Intoxication / Alcohol Detected.' :
              activeMode === 'drowsy' ? 'CRITICAL DANGER: Drowsiness / High Fatigue Warning.' :
              activeMode === 'crash' ? 'CRITICAL DANGER: Crash Detected!' : 'CRITICAL DANGER: Impairment or collision warning.'
            )}
          </p>
        </div>
        
        {/* Confidence Bars */}
        <div className="pred-confidence">
          <div className="confidence-bar-group">
            <div className="confidence-label">
              <span>Safe</span>
              <span>{Math.round(class_probabilities.Safe * 100)}%</span>
            </div>
            <div className="confidence-bg">
              <div 
                className="confidence-fill fill-safe" 
                style={{ width: `${class_probabilities.Safe * 100}%` }}
              ></div>
            </div>
          </div>
          
          <div className="confidence-bar-group">
            <div className="confidence-label">
              <span>At-Risk</span>
              <span>{Math.round(class_probabilities['At-Risk'] * 100)}%</span>
            </div>
            <div className="confidence-bg">
              <div 
                className="confidence-fill fill-risk" 
                style={{ width: `${class_probabilities['At-Risk'] * 100}%` }}
              ></div>
            </div>
          </div>
          
          <div className="confidence-bar-group">
            <div className="confidence-label">
              <span>Danger</span>
              <span>{Math.round(class_probabilities.Danger * 100)}%</span>
            </div>
            <div className="confidence-bg">
              <div 
                className="confidence-fill fill-danger" 
                style={{ width: `${class_probabilities.Danger * 100}%` }}
              ></div>
            </div>
          </div>
        </div>
      </section>

      {/* Sensor Cards Grid */}
      <section className="sensor-grid">
        {/* Speed Card */}
        <div className="glass-card sensor-card highlight">
          <div className="sensor-card-header">
            <span className="sensor-label">Speedometer</span>
            <Gauge className="sensor-icon" size={18} />
          </div>
          <div className="sensor-value-area">
            <span className="sensor-value">{sensor_data.speed}</span>
            <span className="sensor-unit">km/h</span>
          </div>
          <div className={`sensor-subtext ${activeMode === 'crash' ? 'warning-text' : (sensor_data.speed > 80 ? 'warning-text' : 'safe-text')}`}>
            {activeMode === 'crash' ? 'Vehicle stopped after impact' : (sensor_data.speed > 80 ? 'OVERSPEEDING (>80)' : 'Safe speed limits')}
          </div>
        </div>

        {/* Alcohol level Card */}
        <div className="glass-card sensor-card warning">
          <div className="sensor-card-header">
            <span className="sensor-label">Alcohol Sensor (MQ-3)</span>
            <Flame className="sensor-icon" size={18} />
          </div>
          <div className="sensor-value-area">
            <span className="sensor-value">{sensor_data.alcohol_level}</span>
            <span className="sensor-unit">mg/L</span>
          </div>
          <div className={`sensor-subtext ${activeMode === 'crash' ? 'safe-text' : (sensor_data.alcohol_level >= 0.35 ? 'warning-text' : (sensor_data.alcohol_level >= 0.15 ? 'risk-text' : 'safe-text'))}`}>
            {activeMode === 'crash' ? 'Sober / Zero alcohol' : (sensor_data.alcohol_level >= 0.35 ? 'INTOXICATED: IGNITION LOCKED' : (sensor_data.alcohol_level >= 0.15 ? 'Moderate alcohol' : 'Sober / Zero alcohol'))}
          </div>
        </div>

        {/* Drowsiness Card */}
        <div className="glass-card sensor-card">
          <div className="sensor-card-header">
            <span className="sensor-label">Drowsiness Tracker</span>
            <Eye className="sensor-icon" size={18} />
          </div>
          <div className="sensor-value-area">
            <span className="sensor-value">{Math.round(sensor_data.drowsy_score * 100)}</span>
            <span className="sensor-unit">% Fatigue</span>
          </div>
          <div className={`sensor-subtext ${activeMode === 'crash' ? 'safe-text' : (sensor_data.drowsy_score >= 0.75 ? 'warning-text' : (sensor_data.drowsy_score >= 0.5 ? 'risk-text' : 'safe-text'))}`}>
            {activeMode === 'crash' ? 'Not primary trigger' : (sensor_data.drowsy_score >= 0.75 ? 'DROWSY: ALERT ACTIVE' : (sensor_data.drowsy_score >= 0.5 ? 'Fatigued eye blinks' : 'Rider alert'))}
          </div>
        </div>

        {/* Vibration Card */}
        <div className="glass-card sensor-card">
          <div className="sensor-card-header">
            <span className="sensor-label">Mechanical Vibration</span>
            <Activity className="sensor-icon" size={18} />
          </div>
          <div className="sensor-value-area">
            <span className="sensor-value">{sensor_data.vibration}</span>
            <span className="sensor-unit">m/s²</span>
          </div>
          <div className={`sensor-subtext ${activeMode === 'crash' ? 'warning-text' : (sensor_data.vibration > 12.0 ? 'warning-text' : 'safe-text')}`}>
            {activeMode === 'crash' ? 'IMPACT DETECTED' : (sensor_data.vibration > 12.0 ? 'IMPACT DETECTED' : 'Normal road vibrations')}
          </div>
        </div>
      </section>

      {/* Axis Arrays Sensors */}
      <section className="sensor-grid" style={{ gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))' }}>
        {/* Accelerometer card */}
        <div className="glass-card sensor-card">
          <div className="sensor-card-header">
            <span className="sensor-label">3-Axis Accelerometer (MPU6050)</span>
            <Activity size={18} />
          </div>
          <div className="vector-display">
            <div className="vector-axis">
              <span className="axis-lbl">X-Axis (Lateral Tilt)</span>
              <span className="axis-val">{sensor_data.accel_x} G</span>
            </div>
            <div className="vector-axis">
              <span className="axis-lbl">Y-Axis (Longitudinal)</span>
              <span className="axis-val">{sensor_data.accel_y} G</span>
            </div>
            <div className="vector-axis">
              <span className="axis-lbl">Z-Axis (Vertical Force)</span>
              <span className="axis-val">{sensor_data.accel_z} G</span>
            </div>
          </div>
          <span className="sensor-subtext">Reports impact accelerations in G units.</span>
        </div>

        {/* Gyroscope Card */}
        <div className="glass-card sensor-card">
          <div className="sensor-card-header">
            <span className="sensor-label">3-Axis Gyroscope (Tilt Angles)</span>
            <Navigation size={18} />
          </div>
          <div className="vector-display">
            <div className="vector-axis">
              <span className="axis-lbl">Pitch (Front/Back Tilt)</span>
              <span className="axis-val">{sensor_data.gyro_x}°/s</span>
            </div>
            <div className="vector-axis">
              <span className="axis-lbl">Roll (Side Swerve)</span>
              <span className="axis-val">{sensor_data.gyro_y}°/s</span>
            </div>
            <div className="vector-axis">
              <span className="axis-lbl">Yaw (Heading Rotation)</span>
              <span className="axis-val">{sensor_data.gyro_z}°/s</span>
            </div>
          </div>
          <span className="sensor-subtext">Monitors angular speed and helmet orientation.</span>
        </div>
      </section>

      {/* Emergency Section & Maps */}
      <section className="alert-section">
        {/* Emergency Alert Panel */}
        <div className={`glass-card alert-panel ${isAlertActive ? 'active' : ''}`}>
          <div className="alert-header">
            <div className="alert-bell">
              {isAlertActive ? <AlertTriangle size={24} /> : <ShieldAlert size={24} />}
            </div>
            <div>
              <h3>Emergency SOS Status</h3>
              <p>{isAlertActive ? '🚨 Crash Detected' : 'Monitoring helmet sensor streams.'}</p>
            </div>
          </div>

          <div className="alert-grid">
            <div className="alert-info-box">
              <div className="alert-lbl">Alert Active</div>
              <div className="alert-val" style={{ color: isAlertActive ? '#ff0844' : '#10b981' }}>
                {isAlertActive ? 'True' : 'False'}
              </div>
            </div>

            <div className={`alert-info-box ${isAlertActive ? 'danger-highlight' : ''}`}>
              <div className="alert-lbl">Crash Severity</div>
              <div className="alert-val severity-high" style={{ color: isAlertActive ? '#ff0844' : '#fff' }}>
                {isAlertActive ? alertData.severity : 'N/A'}
              </div>
            </div>

            <div className="alert-info-box">
              <div className="alert-lbl">SMS Dispatch</div>
              <div className="alert-val" style={{ color: isAlertActive ? '#10b981' : '#fff' }}>
                {isAlertActive ? 'Sent' : 'Inactive'}
              </div>
            </div>

            <div className="alert-info-box">
              <div className="alert-lbl">System Notice</div>
              <div className="alert-val">
                {isAlertActive ? 'Emergency contacts notified' : 'Inactive'}
              </div>
            </div>

            <div className="alert-info-box gsm-details-box">
              <div className="alert-lbl">GSM SMS Dispatch (SIM800L Simulation)</div>
              <div className={`alert-val ${isAlertActive ? 'gsm-sent' : ''}`} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                {isAlertActive ? (
                  <>
                    <Send size={14} />
                    <span style={{ color: '#10b981', fontWeight: 'bold' }}>Emergency SMS Sent Successfully</span>
                  </>
                ) : 'Inactive'}
              </div>
              {isAlertActive && (
                <div className="gsm-sms-preview">
                  <strong>SMS Dispatch Payload:</strong><br />
                  🚨 [CRITICAL ACCIDENT DETECTED] 🚨<br />
                  Rider Location: {alertData.latitude.toFixed(6)}, {alertData.longitude.toFixed(6)}<br />
                  Google Maps: https://www.google.com/maps?q={alertData.latitude.toFixed(6)},{alertData.longitude.toFixed(6)}<br />
                  Crash Impact Severity: {alertData.severity}<br />
                  Impact Force Vector: {alertData.impact_force}<br />
                  Timestamp: {alertData.timestamp}
                </div>
              )}
            </div>
          </div>

          {isAlertActive && (
            <div className="reset-btn-wrapper">
              <button 
                className="btn-reset-alert" 
                onClick={handleResetAlert}
                disabled={actionLoading}
              >
                Clear Crash Notification
              </button>
            </div>
          )}
        </div>

        {/* GPS location and Map */}
        <div className="glass-card map-card">
          <div className="sensor-card-header">
            <span className="sensor-label">Live GPS Navigation (NEO-6M GPS)</span>
            <MapPin size={18} />
          </div>
          
          <div className="vector-display" style={{ marginTop: '0.5rem' }}>
            <div className="vector-axis">
              <span className="axis-lbl">Latitude</span>
              <span className="axis-val">{sensor_data.latitude.toFixed(6)}</span>
            </div>
            <div className="vector-axis">
              <span className="axis-lbl">Longitude</span>
              <span className="axis-val">{sensor_data.longitude.toFixed(6)}</span>
            </div>
          </div>

          <div className="map-wrapper">
            <div className="mock-map">
              <div className="map-road road-h"></div>
              <div className="map-road road-v"></div>
              
              {/* Radar/Pin */}
              <div className={`map-pin ${isAlertActive ? 'crash-site' : ''}`}>
                {isAlertActive && <div className="radar-ping"></div>}
                <MapPin className="pin-icon" size={32} fill={isAlertActive ? '#D71920' : '#D4AF37'} />
                <div className="map-label">
                  {isAlertActive ? 'CRASH SITE DETECTED' : 'Rider Navigating'}
                </div>
              </div>
              
              {isAlertActive && (
                <div style={{ position: 'absolute', bottom: '40px', left: '50%', transform: 'translateX(-50%)', zindex: 20 }}>
                  <a 
                    href={`https://www.google.com/maps?q=${alertData.latitude.toFixed(6)},${alertData.longitude.toFixed(6)}`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="btn-primary"
                    style={{ fontSize: '0.75rem', padding: '0.4rem 0.8rem', borderRadius: '6px', display: 'flex', alignItems: 'center', gap: '0.25rem', textDecoration: 'none' }}
                  >
                    <MapPin size={12} />
                    Open Google Maps Link
                  </a>
                </div>
              )}

              <div className="map-controls">
                Zoom: Live Feed
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Historical charts */}
      <section className="charts-grid">
        {/* Speed Chart */}
        <div className="glass-card chart-card">
          <h3>Speed Analysis Trend (km/h)</h3>
          <div style={{ width: '100%', height: 220 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                <defs>
                  <linearGradient id="speedGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#D4AF37" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#D4AF37" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="timestamp" stroke="#6b7280" fontSize={10} />
                <YAxis stroke="#6b7280" domain={[0, 120]} fontSize={10} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: 'rgba(255,255,255,0.1)', color: '#fff' }}
                  labelStyle={{ color: '#9ca3af' }}
                />
                <Area type="monotone" dataKey="speed" stroke="#D4AF37" strokeWidth={2} fillOpacity={1} fill="url(#speedGrad)" name="Speed" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Vibration Chart */}
        <div className="glass-card chart-card">
          <h3>Mechanical Vibration Trend (SW-420)</h3>
          <div style={{ width: '100%', height: 220 }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData} margin={{ top: 5, right: 10, left: -20, bottom: 5 }}>
                <defs>
                  <linearGradient id="vibGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#D71920" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#D71920" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                <XAxis dataKey="timestamp" stroke="#6b7280" fontSize={10} />
                <YAxis stroke="#6b7280" domain={[0, 20]} fontSize={10} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', borderColor: 'rgba(255,255,255,0.1)', color: '#fff' }}
                  labelStyle={{ color: '#9ca3af' }}
                />
                <Area type="monotone" dataKey="vibration" stroke="#D71920" strokeWidth={2} fillOpacity={1} fill="url(#vibGrad)" name="Vibration" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>
      </section>
    </div>
  );
}

export default Dashboard;
