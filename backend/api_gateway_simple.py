import json
import os
import time
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for frontend

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    try:
        return jsonify(
            {
                "status": "healthy",
                "timestamp": str(int(time.time() * 1000)),
                "services": {
                    "data_service": "active",
                    "trading_service": "active",
                    "order_service": "active",
                    "circuit_breaker": "active",
                },
            }
        )
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route("/data/market", methods=["GET"])
def get_market_data():
    """Get current market data"""
    try:
        symbol = request.args.get("symbol", "SPY")
        
        # Return demo data
        market_data = {
            "symbol": symbol,
            "price": round(150 + (hash(symbol) % 100) / 10, 2),
            "timestamp": str(int(time.time() * 1000)),
            "volume": 1000000,
            "change": "+0.5%",
            "note": "Demo mode - Schwab credentials not configured",
        }
        return jsonify({"success": True, "data": market_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/data/account", methods=["GET"])
def get_account_data():
    """Get account details"""
    try:
        # Return demo account data
        account_data = {
            "account_hash": "demo-account",
            "cash_balance": 10000.00,
            "available_funds": 8500.00,
            "buying_power": 17000.00,
            "timestamp": str(int(time.time() * 1000)),
            "note": "Demo mode - Schwab credentials not configured",
        }
        return jsonify({"success": True, "data": account_data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/trading/positions", methods=["GET"])
def get_positions():
    """Get current positions"""
    try:
        # Return demo positions
        return jsonify(
            {"success": True, "data": {"positions": {"SPY": 100, "QQQ": 50}}}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/trading/start", methods=["POST"])
def start_trading():
    """Start trading bot"""
    try:
        data = request.get_json()
        symbol = data.get("symbol", "SPY")
        
        return jsonify({"success": True, "message": f"Trading started for {symbol}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/trading/stop", methods=["POST"])
def stop_trading():
    """Stop trading bot"""
    try:
        return jsonify({"success": True, "message": "Trading stopped"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route("/order", methods=["POST"])
def create_order():
    """Create new order"""
    try:
        data = request.get_json()
        order_data = {
            "symbol": data.get("symbol"),
            "quantity": data.get("quantity"),
            "order_type": data.get("order_type", "MARKET"),
            "side": data.get("side", "BUY"),
        }
        
        return jsonify(
            {"success": True, "message": "Order created", "order": order_data}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
