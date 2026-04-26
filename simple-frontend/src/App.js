import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [tradingData, setTradingData] = useState(null);
  const [positions, setPositions] = useState({});
  const [status, setStatus] = useState('Connecting...');

  useEffect(() => {
    // Simulate real-time trading data
    const interval = setInterval(() => {
      setTradingData({
        symbol: 'SPY',
        price: (150 + Math.random() * 10).toFixed(2),
        timestamp: new Date().toLocaleTimeString(),
        ema_fast: (148 + Math.random() * 5).toFixed(2),
        ema_slow: (147 + Math.random() * 5).toFixed(2)
      });
      
      setPositions({
        SPY: Math.floor(Math.random() * 100)
      });
      
      setStatus('Trading Bot Active - Simulated Mode');
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 Trading Bot Dashboard</h1>
        <div className="status">{status}</div>
      </header>
      
      <main className="dashboard">
        <div className="card">
          <h2>📊 Market Data</h2>
          {tradingData && (
            <div className="data-grid">
              <div className="data-item">
                <span className="label">Symbol:</span>
                <span className="value">{tradingData.symbol}</span>
              </div>
              <div className="data-item">
                <span className="label">Price:</span>
                <span className="value">${tradingData.price}</span>
              </div>
              <div className="data-item">
                <span className="label">Time:</span>
                <span className="value">{tradingData.timestamp}</span>
              </div>
              <div className="data-item">
                <span className="label">EMA Fast:</span>
                <span className="value">${tradingData.ema_fast}</span>
              </div>
              <div className="data-item">
                <span className="label">EMA Slow:</span>
                <span className="value">${tradingData.ema_slow}</span>
              </div>
            </div>
          )}
        </div>

        <div className="card">
          <h2>💼 Current Positions</h2>
          <div className="positions">
            {Object.entries(positions).map(([symbol, quantity]) => (
              <div key={symbol} className="position-item">
                <span className="symbol">{symbol}:</span>
                <span className="quantity">{quantity} shares</span>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <h2>⚡ Services Status</h2>
          <div className="services">
            <div className="service-item active">✅ Data Service</div>
            <div className="service-item active">✅ Trading Service</div>
            <div className="service-item active">✅ Order Service</div>
            <div className="service-item active">✅ Circuit Breaker</div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
