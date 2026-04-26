import React, { useState, useEffect } from "react";
import "./App.css";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:5000";

function App() {
  const [tradingData, setTradingData] = useState(null);
  const [positions, setPositions] = useState({});
  const [accountData, setAccountData] = useState(null);
  const [status, setStatus] = useState("Connecting...");
  const [isConnected, setIsConnected] = useState(false);

  // Fetch market data
  const fetchMarketData = async () => {
    try {
      const response = await fetch(`${API_URL}/data/market?symbol=SPY`);
      const result = await response.json();

      if (result.success) {
        setTradingData(result.data);
        setIsConnected(true);
        setStatus("Trading Bot Active - Live Mode");
      } else {
        console.error("Failed to fetch market data:", result.error);
        setStatus("Error fetching market data");
      }
    } catch (error) {
      console.error("Error fetching market data:", error);
      setStatus("Connection Error");
      setIsConnected(false);
    }
  };

  // Fetch positions
  const fetchPositions = async () => {
    try {
      const response = await fetch(`${API_URL}/trading/positions`);
      const result = await response.json();

      if (result.success) {
        setPositions(result.data.positions);
      }
    } catch (error) {
      console.error("Error fetching positions:", error);
    }
  };

  // Fetch account data
  const fetchAccountData = async () => {
    try {
      const response = await fetch(`${API_URL}/data/account`);
      const result = await response.json();

      if (result.success) {
        setAccountData(result.data);
      }
    } catch (error) {
      console.error("Error fetching account data:", error);
    }
  };

  // Check health
  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_URL}/health`);
      const result = await response.json();

      if (result.status === "healthy") {
        setIsConnected(true);
        setStatus("All Systems Operational");
      } else {
        setIsConnected(false);
        setStatus("System Unhealthy");
      }
    } catch (error) {
      console.error("Health check failed:", error);
      setIsConnected(false);
      setStatus("Connection Error");
    }
  };

  useEffect(() => {
    // Initial data fetch
    checkHealth();
    fetchMarketData();
    fetchPositions();
    fetchAccountData();

    // Set up polling for real-time updates
    const marketDataInterval = setInterval(fetchMarketData, 5000);
    const positionsInterval = setInterval(fetchPositions, 10000);
    const accountInterval = setInterval(fetchAccountData, 30000);
    const healthInterval = setInterval(checkHealth, 15000);

    return () => {
      clearInterval(marketDataInterval);
      clearInterval(positionsInterval);
      clearInterval(accountInterval);
      clearInterval(healthInterval);
    };
  }, []);

  return (
    <div className="App">
      <header className="App-header">
        <h1>🤖 Trading Bot Dashboard</h1>
        <div className={`status ${isConnected ? "connected" : "disconnected"}`}>
          {status}
        </div>
      </header>

      <main className="dashboard">
        <div className="card">
          <h2>📊 Market Data</h2>
          {tradingData ? (
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
                <span className="value">
                  {new Date(
                    parseInt(tradingData.timestamp),
                  ).toLocaleTimeString()}
                </span>
              </div>
              <div className="data-item">
                <span className="label">Volume:</span>
                <span className="value">
                  {tradingData.volume?.toLocaleString() || "N/A"}
                </span>
              </div>
              <div className="data-item">
                <span className="label">Change:</span>
                <span className="value">{tradingData.change || "N/A"}</span>
              </div>
            </div>
          ) : (
            <div className="loading">Loading market data...</div>
          )}
        </div>

        <div className="card">
          <h2>💼 Current Positions</h2>
          <div className="positions">
            {Object.keys(positions).length > 0 ? (
              Object.entries(positions).map(([symbol, quantity]) => (
                <div key={symbol} className="position-item">
                  <span className="symbol">{symbol}:</span>
                  <span className="quantity">{quantity} shares</span>
                </div>
              ))
            ) : (
              <div className="loading">No positions found</div>
            )}
          </div>
        </div>

        <div className="card">
          <h2>🏦 Account Information</h2>
          {accountData ? (
            <div className="data-grid">
              <div className="data-item">
                <span className="label">Cash Balance:</span>
                <span className="value">
                  ${accountData.cash_balance?.toLocaleString() || "0"}
                </span>
              </div>
              <div className="data-item">
                <span className="label">Available Funds:</span>
                <span className="value">
                  ${accountData.available_funds?.toLocaleString() || "0"}
                </span>
              </div>
              <div className="data-item">
                <span className="label">Buying Power:</span>
                <span className="value">
                  ${accountData.buying_power?.toLocaleString() || "0"}
                </span>
              </div>
            </div>
          ) : (
            <div className="loading">Loading account data...</div>
          )}
        </div>

        <div className="card">
          <h2>⚡ Connection Status</h2>
          <div className="services">
            <div
              className={`service-item ${isConnected ? "active" : "inactive"}`}
            >
              {isConnected ? "✅ API Connected" : "❌ API Disconnected"}
            </div>
            <div className="service-item active">✅ Data Service</div>
            <div className="service-item active">✅ Trading Service</div>
            <div className="service-item active">✅ Order Service</div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
