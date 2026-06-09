import React, { useState, useEffect, useRef } from 'react';

const API_BASE = 'http://localhost:8000';
const WS_BASE = 'ws://localhost:8000/ws/mission';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [authView, setAuthView] = useState('login'); // login, register, otp
  
  // Local Engine Status State
  const [isEngineConnected, setIsEngineConnected] = useState(false);
  const [isCheckingEngine, setIsCheckingEngine] = useState(true);

  // Poll Local Engine
  useEffect(() => {
    const checkEngine = async () => {
      try {
        const res = await fetch(`${API_BASE}/api/health`);
        if (res.ok) {
          setIsEngineConnected(true);
        } else {
          setIsEngineConnected(false);
        }
      } catch (err) {
        setIsEngineConnected(false);
      }
      setIsCheckingEngine(false);
    };

    checkEngine();
    const interval = setInterval(checkEngine, 3000); // Check every 3 seconds
    return () => clearInterval(interval);
  }, []);

  // Auth Forms
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [otp, setOtp] = useState('');
  const [otpMessage, setOtpMessage] = useState('');
  
  // Modes Setup State
  const [showModeSelector, setShowModeSelector] = useState(false);
  const [selectedMode, setSelectedMode] = useState('online');

  // App Configuration State
  const [senderProfiles, setSenderProfiles] = useState([]);
  const [activeProfile, setActiveProfile] = useState('');
  const [sendgridKey, setSendgridKey] = useState('');
  const [host, setHost] = useState('smtp.gmail.com');
  const [port, setPort] = useState(587);
  const [appPassword, setAppPassword] = useState('');

  // Mission State
  const [subject, setSubject] = useState('');
  const [body, setBody] = useState('');
  const [csvFile, setCsvFile] = useState(null);
  const [csvCount, setCsvCount] = useState(0);
  const [delay, setDelay] = useState(1.0);
  const [batchSize, setBatchSize] = useState(50);
  const [batchPause, setBatchPause] = useState(60);
  const [personalize, setPersonalize] = useState(true);
  const [htmlMode, setHtmlMode] = useState(true);

  // Live Metrics
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState('Idle');
  const [logs, setLogs] = useState([]);
  const [sentCount, setSentCount] = useState(0);
  const [failCount, setFailCount] = useState(0);
  const [isTransmitting, setIsTransmitting] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);

  const logsEndRef = useRef(null);
  const wsRef = useRef(null);

  // Auto scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // Load profiles on auth success
  useEffect(() => {
    if (token) {
      fetchProfiles();
      connectWebSocket();
    }
    return () => wsRef.current?.close();
  }, [token]);

  const connectWebSocket = () => {
    const ws = new WebSocket(WS_BASE);
    wsRef.current = ws;

    ws.onopen = () => setWsConnected(true);
    ws.onclose = () => {
      setWsConnected(false);
      // Auto-reconnect safety guard
      setTimeout(connectWebSocket, 5000);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'log') {
        setLogs((prev) => [...prev, `[${new Date().toLocaleTimeString()}] ${data.message}`]);
      } else if (data.type === 'progress') {
        setProgress(data.progress);
        setStatusText(data.status);
      } else if (data.type === 'completion') {
        setIsTransmitting(false);
        setSentCount(data.sent);
        setFailCount(data.failed);
        alert(`Mission Completed!\nSent: ${data.sent}\nFailed: ${data.failed}`);
      }
    };
  };

  const fetchProfiles = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/config/get?token=${token}`);
      if (res.ok) {
        const data = await res.json();
        setSenderProfiles(data);
        if (data.length > 0) setActiveProfile(data[0].email);
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Auth Operations
  const handleRegister = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('email', email);
    formData.append('password', password);
    const res = await fetch(`${API_BASE}/api/auth/register`, { method: 'POST', body: formData });
    if (res.ok) {
      alert('Registration successful! Please login.');
      setAuthView('login');
    } else {
      const data = await res.json();
      alert(`Registration Failed: ${data.detail}`);
    }
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('email', email);
    formData.append('password', password);
    const res = await fetch(`${API_BASE}/api/auth/login`, { method: 'POST', body: formData });
    if (res.ok) {
      const data = await res.json();
      setOtpMessage(`Simulated Gateway OTP Dispatched: ${data.simulation_otp}`);
      setAuthView('otp');
    } else {
      const data = await res.json();
      alert(`Login Failed: ${data.detail}`);
    }
  };

  const handleVerifyOtp = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('email', email);
    formData.append('otp', otp);
    const res = await fetch(`${API_BASE}/api/auth/verify-otp`, { method: 'POST', body: formData });
    if (res.ok) {
      const data = await res.json();
      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
      setShowModeSelector(true); // First-time login selection prompt
    } else {
      alert('Invalid OTP Security Code.');
    }
  };

  const handleConfirmMode = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('token', token);
    formData.append('mode', selectedMode);
    
    const res = await fetch(`${API_BASE}/api/mission/setup-mode`, { method: 'POST', body: formData });
    if (res.ok) {
      alert(`Configured successfully for ${selectedMode === 'online' ? 'Online' : 'Local System'} Mode.`);
      setShowModeSelector(false);
      fetchProfiles();
      connectWebSocket();
    } else {
      const err = await res.json();
      alert(`Setup Failed: ${err.detail}`);
    }
  };

  // Save profile config
  const handleSaveConfig = async (e) => {
    e.preventDefault();
    const formData = new FormData();
    formData.append('token', token);
    formData.append('email', activeProfile || email);
    formData.append('host', host);
    formData.append('port', port);
    formData.append('app_password', appPassword);

    const res = await fetch(`${API_BASE}/api/config/save`, { method: 'POST', body: formData });
    if (res.ok) {
      alert('Sender credentials securely configured.');
      fetchProfiles();
    } else {
      alert('Failed to save config.');
    }
  };

  // CSV load
  const handleCsvUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setCsvFile(file);
    const formData = new FormData();
    formData.append('token', token);
    formData.append('file', file);

    const res = await fetch(`${API_BASE}/api/mission/upload-csv`, { method: 'POST', body: formData });
    if (res.ok) {
      const data = await res.json();
      setCsvCount(data.count);
      alert(`Loaded ${data.count} recipients successfully.`);
    } else {
      alert('CSV parsing error.');
    }
  };

  // Launch Mission
  const handleLaunch = async () => {
    if (!csvFile) {
      alert('Load a recipients CSV file first.');
      return;
    }
    setIsTransmitting(true);
    setLogs([]);
    setProgress(0);
    setStatusText('Launching...');

    const formData = new FormData();
    formData.append('token', token);
    formData.append('sender_email', activeProfile);
    formData.append('subject', subject);
    formData.append('body', body);
    formData.append('sendgrid_key', sendgridKey);
    formData.append('delay', delay);
    formData.append('batch_size', batchSize);
    formData.append('batch_pause', batchPause);
    formData.append('personalize', personalize);
    formData.append('html_mode', htmlMode);

    const res = await fetch(`${API_BASE}/api/mission/launch`, { method: 'POST', body: formData });
    if (!res.ok) {
      const data = await res.json();
      alert(`Launch Denied: ${data.detail}`);
      setIsTransmitting(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken('');
    setAuthView('login');
  };

  // --- RENDERING ---

  if (isCheckingEngine) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: '100vh', color: '#00E5FF' }}>
        <h2>Scanning for Local Engine...</h2>
      </div>
    );
  }

  if (!isEngineConnected) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', minHeight: '100vh' }}>
        <div className="glass-panel" style={{ padding: '40px', width: '500px', margin: 'auto', textAlign: 'center' }}>
          <h2 style={{ color: '#EF4444', margin: '0 0 15px 0' }}>⚠️ Local Engine Disconnected</h2>
          <p style={{ fontSize: '14px', color: '#8892B0', marginBottom: '30px', lineHeight: '1.6' }}>
            jBulkEmail is a Hybrid SaaS. To bypass browser security sandboxes and safely create files directly on your <b>Windows Desktop</b>, you must install the Local Connector Plugin.
          </p>
          <a href="/jBulkEmail_Connector.bat" download style={{ textDecoration: 'none' }}>
            <button className="btn-cyber" style={{ width: '100%', padding: '15px', fontSize: '16px', background: 'linear-gradient(90deg, #FF9800 0%, #FFD700 100%)', color: '#000', fontWeight: 'bold' }}>
              🔌 Download Connector Plugin
            </button>
          </a>
          <p style={{ fontSize: '12px', color: '#8892B0', marginTop: '20px' }}>
            <i>After downloading, double-click the script to run it. This page will automatically unlock once the connection is established!</i>
          </p>
        </div>
      </div>
    );
  }

  if (!token) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', minHeight: '100vh' }}>
        <div className="glass-panel" style={{ padding: '35px', width: '380px', margin: 'auto' }}>
          <h2 style={{ textAlign: 'center', color: '#00E5FF', margin: '0 0 10px 0' }}>🚀 Mission Access</h2>
          <p style={{ fontSize: '12px', textAlign: 'center', color: '#8892B0', margin: '0 0 25px 0' }}>
            Zero-Trust SaaS Verification Gateway
          </p>

          {authView === 'login' && (
            <form onSubmit={handleLogin}>
              <div style={{ marginBottom: '15px', display: 'flex', flexDirection: 'column' }}>
                <label style={{ fontSize: '12px', marginBottom: '5px' }}>Email</label>
                <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
              </div>
              <div style={{ marginBottom: '25px', display: 'flex', flexDirection: 'column' }}>
                <label style={{ fontSize: '12px', marginBottom: '5px' }}>Password</label>
                <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
              </div>
              <button type="submit" className="btn-cyber" style={{ width: '100%', marginBottom: '15px' }}>
                Generate Security OTP
              </button>
              <p style={{ textAlign: 'center', fontSize: '12px', color: '#8892B0' }}>
                New user? <span style={{ color: '#00E5FF', cursor: 'pointer' }} onClick={() => setAuthView('register')}>Register here</span>
              </p>
            </form>
          )}

          {authView === 'register' && (
            <form onSubmit={handleRegister}>
              <div style={{ marginBottom: '15px', display: 'flex', flexDirection: 'column' }}>
                <label style={{ fontSize: '12px', marginBottom: '5px' }}>Email</label>
                <input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} />
              </div>
              <div style={{ marginBottom: '25px', display: 'flex', flexDirection: 'column' }}>
                <label style={{ fontSize: '12px', marginBottom: '5px' }}>Password</label>
                <input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} />
              </div>
              <button type="submit" className="btn-cyber" style={{ width: '100%', marginBottom: '15px' }}>
                Sign Up Account
              </button>
              <p style={{ textAlign: 'center', fontSize: '12px', color: '#8892B0' }}>
                Have an account? <span style={{ color: '#00E5FF', cursor: 'pointer' }} onClick={() => setAuthView('login')}>Log in</span>
              </p>
            </form>
          )}

          {authView === 'otp' && (
            <form onSubmit={handleVerifyOtp}>
              <div style={{ backgroundColor: 'rgba(0,229,255,0.1)', padding: '10px', borderRadius: '6px', fontSize: '12px', color: '#00E5FF', marginBottom: '15px', wordBreak: 'break-all' }}>
                {otpMessage}
              </div>
              <div style={{ marginBottom: '25px', display: 'flex', flexDirection: 'column' }}>
                <label style={{ fontSize: '12px', marginBottom: '5px' }}>Enter 6-Digit OTP</label>
                <input type="text" required maxLength={6} value={otp} onChange={(e) => setOtp(e.target.value)} style={{ textAlign: 'center', letterSpacing: '8px', fontSize: '20px' }} />
              </div>
              <button type="submit" className="btn-cyber" style={{ width: '100%' }}>
                Verify & Authorize
              </button>
            </form>
          )}
        </div>
      </div>
    );
  }

  if (showModeSelector) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', minHeight: '100vh' }}>
        <div className="glass-panel" style={{ padding: '35px', width: '500px', margin: 'auto' }}>
          <h2 style={{ textAlign: 'center', color: '#00E5FF', margin: '0 0 10px 0' }}>⚙️ Choose Operation Mode</h2>
          <p style={{ fontSize: '12px', textAlign: 'center', color: '#8892B0', margin: '0 0 25px 0' }}>
            First-Boot Configuration Selector
          </p>

          <form onSubmit={handleConfirmMode}>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginBottom: '25px' }}>
              
              {/* Online Mode Option */}
              <label style={{ display: 'flex', gap: '15px', padding: '15px', borderRadius: '8px', border: selectedMode === 'online' ? '1px solid #00E5FF' : '1px solid rgba(255,255,255,0.1)', background: selectedMode === 'online' ? 'rgba(0,229,255,0.05)' : 'transparent', cursor: 'pointer' }}>
                <input type="radio" name="mode" value="online" checked={selectedMode === 'online'} onChange={() => setSelectedMode('online')} style={{ marginTop: '4px' }} />
                <div>
                  <strong style={{ color: '#00E5FF', display: 'block' }}>🌐 Online Mode</strong>
                  <span style={{ fontSize: '12px', color: '#8892B0' }}>
                    Creates local directory structure under system user home (<code>~/jBulkEmail</code>) for data files, running the web service engine synced from <code>https://github.com/jDroid-X/jBulkEmail</code>.
                  </span>
                </div>
              </label>

              {/* Local System Mode Option */}
              <label style={{ display: 'flex', gap: '15px', padding: '15px', borderRadius: '8px', border: selectedMode === 'local' ? '1px solid #FFD700' : '1px solid rgba(255,255,255,0.1)', background: selectedMode === 'local' ? 'rgba(255,215,0,0.05)' : 'transparent', cursor: 'pointer' }}>
                <input type="radio" name="mode" value="local" checked={selectedMode === 'local'} onChange={() => setSelectedMode('local')} style={{ marginTop: '4px' }} />
                <div>
                  <strong style={{ color: '#FFD700', display: 'block' }}>💻 Local System Mode</strong>
                  <span style={{ fontSize: '12px', color: '#8892B0' }}>
                    Runs local installation by downloading the full <code>jBulkEmail</code> package, python modules, and offline executable files to execute entirely locally on your PC.
                  </span>
                </div>
              </label>

            </div>

            <button type="submit" className="btn-cyber" style={{ width: '100%', padding: '12px', background: selectedMode === 'local' ? 'linear-gradient(90deg, #FF9800 0%, #FFD700 100%)' : undefined }}>
              Confirm & Launch
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div style={{ display: 'grid', gridTemplateColumns: '260px 1fr', gap: '20px', width: '1200px', margin: '30px auto', padding: '0 20px' }}>
      
      {/* Sidebar Command Console */}
      <div className="glass-panel" style={{ padding: '20px', height: 'fit-content' }}>
        <h3 style={{ color: '#00E5FF', marginTop: 0 }}>⚙️ Configurations</h3>
        
        <form onSubmit={handleSaveConfig} style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          <div>
            <label style={{ fontSize: '11px', display: 'block', marginBottom: '4px' }}>Sender Profiles</label>
            <select value={activeProfile} onChange={(e) => setActiveProfile(e.target.value)} style={{ width: '100%' }}>
              {senderProfiles.map((p) => (
                <option key={p.email} value={p.email}>{p.email}</option>
              ))}
              <option value="">+ Add New Profile</option>
            </select>
          </div>

          {!activeProfile && (
            <>
              <div>
                <label style={{ fontSize: '11px', display: 'block', marginBottom: '4px' }}>New Profile Email</label>
                <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} style={{ width: '90%' }} />
              </div>
              <div>
                <label style={{ fontSize: '11px', display: 'block', marginBottom: '4px' }}>SMTP Host</label>
                <input type="text" value={host} onChange={(e) => setHost(e.target.value)} style={{ width: '90%' }} />
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                <div>
                  <label style={{ fontSize: '11px', display: 'block', marginBottom: '4px' }}>Port</label>
                  <input type="number" value={port} onChange={(e) => setPort(Number(e.target.value))} style={{ width: '80%' }} />
                </div>
              </div>
            </>
          )}

          <div>
            <label style={{ fontSize: '11px', display: 'block', marginBottom: '4px' }}>App Password</label>
            <input type="password" placeholder="••••••••" value={appPassword} onChange={(e) => setAppPassword(e.target.value)} style={{ width: '90%' }} />
          </div>

          <button type="submit" className="btn-cyber" style={{ fontSize: '11px', padding: '8px' }}>
            Save Credentials
          </button>
        </form>

        <hr style={{ border: 'none', borderTop: '1px solid rgba(255,255,255,0.1)', margin: '20px 0' }} />

        <div>
          <label style={{ fontSize: '11px', display: 'block', marginBottom: '4px', color: '#FFD700' }}>SendGrid API Key (HTTP Relay)</label>
          <input type="password" placeholder="SG.••••" value={sendgridKey} onChange={(e) => setSendgridKey(e.target.value)} style={{ width: '90%' }} />
        </div>

        <button onClick={handleLogout} style={{ width: '100%', border: '1px solid #EF4444', background: 'transparent', color: '#EF4444', padding: '8px', borderRadius: '6px', cursor: 'pointer', marginTop: '30px', fontWeight: 'bold' }}>
          Logout Console
        </button>
      </div>

      {/* Main Workspace */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
        
        {/* Connection Status & HUD */}
        <div className="glass-panel" style={{ padding: '15px 25px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <h2 style={{ margin: 0, color: '#00E5FF' }}>🚀 Dashboard Dashboard</h2>
          <div style={{ display: 'flex', gap: '15px' }}>
            <span style={{ fontSize: '12px', padding: '4px 10px', borderRadius: '12px', background: wsConnected ? 'rgba(16,185,129,0.2)' : 'rgba(239,68,68,0.2)', color: wsConnected ? '#10B981' : '#EF6868' }}>
              {wsConnected ? 'WebSocket Connected' : 'WebSocket Reconnecting'}
            </span>
          </div>
        </div>

        {/* Setup and Composition deck */}
        <div className="glass-panel" style={{ padding: '25px', display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '20px' }}>
          
          {/* Editor Grid */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px' }}>
            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <label style={{ fontSize: '12px', marginBottom: '5px' }}>Subject Template (Supports &#123;name&#125;, &#123;email&#125;)</label>
              <input type="text" value={subject} onChange={(e) => setSubject(e.target.value)} style={{ width: '95%' }} />
            </div>

            <div style={{ display: 'flex', flexDirection: 'column' }}>
              <label style={{ fontSize: '12px', marginBottom: '5px' }}>Email Content (HTML Enabled)</label>
              <textarea rows={10} value={body} onChange={(e) => setBody(e.target.value)} placeholder="Dear {name}, thank you for choosing our services..." style={{ width: '95%', fontFamily: 'inherit' }} />
            </div>
          </div>

          {/* Load Deck */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', borderLeft: '1px solid rgba(255,255,255,0.1)', paddingLeft: '20px' }}>
            <h4 style={{ margin: 0, color: '#00E5FF' }}>📋 Load Target List</h4>
            
            <div style={{ border: '2px dashed #3A506B', borderRadius: '8px', padding: '20px', textAlign: 'center', cursor: 'pointer' }}>
              <input type="file" accept=".csv" onChange={handleCsvUpload} style={{ display: 'none' }} id="csv-upload" />
              <label htmlFor="csv-upload" style={{ cursor: 'pointer', display: 'block' }}>
                <div style={{ fontSize: '24px', marginBottom: '5px' }}>📂</div>
                <div style={{ fontSize: '12px' }}>{csvFile ? csvFile.name : 'Choose CSV File'}</div>
              </label>
            </div>
            
            <div style={{ fontSize: '12px', color: '#8892B0' }}>
              Recipients Queue Size: <span style={{ color: '#00E5FF', fontWeight: 'bold' }}>{csvCount}</span>
            </div>

            <hr style={{ border: 'none', borderTop: '1px solid rgba(255,255,255,0.1)' }} />

            <div>
              <label style={{ fontSize: '11px', display: 'block', marginBottom: '4px' }}>Send Delay (Seconds)</label>
              <input type="number" step="0.1" value={delay} onChange={(e) => setDelay(Number(e.target.value))} style={{ width: '80%' }} />
            </div>

            <button onClick={handleLaunch} disabled={isTransmitting} className="btn-cyber" style={{ marginTop: 'auto', width: '100%', padding: '12px' }}>
              {isTransmitting ? 'Transmitting...' : '🚀 Launch Mission'}
            </button>
          </div>
        </div>

        {/* Live console monitor */}
        <div className="glass-panel" style={{ padding: '20px' }}>
          <h3 style={{ marginTop: 0, color: '#FFD700', display: 'flex', justifyContent: 'space-between' }}>
            <span>📺 Live Transmission Monitor</span>
            <span style={{ fontSize: '12px', color: '#8892B0' }}>{statusText}</span>
          </h3>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '15px', marginBottom: '20px' }}>
            <div style={{ background: 'rgba(0,229,255,0.05)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(0,229,255,0.1)' }}>
              <div style={{ fontSize: '12px', color: '#8892B0' }}>Global Progress</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#00E5FF' }}>{progress}%</div>
            </div>
            <div style={{ background: 'rgba(16,185,129,0.05)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(16,185,129,0.1)' }}>
              <div style={{ fontSize: '12px', color: '#8892B0' }}>Success Despatched</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#10B981' }}>{sentCount}</div>
            </div>
            <div style={{ background: 'rgba(239,68,68,0.05)', padding: '12px', borderRadius: '8px', border: '1px solid rgba(239,68,68,0.1)' }}>
              <div style={{ fontSize: '12px', color: '#8892B0' }}>Bounced Fails</div>
              <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#EF4444' }}>{failCount}</div>
            </div>
          </div>

          <div className="terminal-screen" style={{ height: '180px' }}>
            {logs.length === 0 ? (
              <div style={{ color: '#8892B0', fontStyle: 'italic' }}>Terminal silent. Awaiting queue trigger...</div>
            ) : (
              logs.map((log, idx) => <div key={idx}>{log}</div>)
            )}
            <div ref={logsEndRef} />
          </div>
        </div>

      </div>
    </div>
  );
}
