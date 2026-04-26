import json
import os
import time
from flask import Flask, jsonify, request
from flask_cors import CORS

# Try to import Schwab client, but don't fail if it's not available
try:
    from clients.schwab_client import get_client

    SCHWAB_AVAILABLE = True
except ImportError:
    SCHWAB_AVAILABLE = False
    get_client = None

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

        # Check if Schwab is available and credentials are configured with real values (not dummy values)
        app_key = os.getenv("CS_APP_KEY", "")
        app_secret = os.getenv("CS_APP_SECRET", "")

        if (
            SCHWAB_AVAILABLE
            and app_key
            and app_secret
            and app_key != "dummy_key"
            and app_secret != "dummy_secret"
        ):
            # Try to get real market data from Schwab
            try:
                client = get_client()
                if not client:
                    raise Exception("Failed to initialize Schwab client")

                # Get price history from Schwab
                resp = client.price_history(
                    symbol=symbol,
                    periodType="day",
                    period=1,
                    frequencyType="minute",
                    frequency=1,
                    needExtendedHoursData=False,
                    needPreviousClose=False,
                )

                if resp.status_code != 200:
                    raise Exception(f"Failed to fetch market data: {resp.status_code}")

                data = resp.json()
                candles = data.get("candles", [])

                if not candles:
                    raise Exception("No market data available")

                # Get the most recent candle
                latest_candle = candles[-1]

                market_data = {
                    "symbol": symbol,
                    "price": float(latest_candle.get("close", 0)),
                    "open": float(latest_candle.get("open", 0)),
                    "high": float(latest_candle.get("high", 0)),
                    "low": float(latest_candle.get("low", 0)),
                    "volume": int(latest_candle.get("volume", 0)),
                    "timestamp": str(
                        latest_candle.get("datetime", int(time.time() * 1000))
                    ),
                    "change": "+0.0%",  # Would need previous close to calculate real change
                    "note": "Real Schwab data",
                }

                print(f"✅ Successfully retrieved real market data for {symbol}")
                return jsonify({"success": True, "data": market_data})

            except Exception as schwab_error:
                print(f"❌ Schwab client error: {schwab_error}")
                # Fall back to demo data if Schwab fails
                pass

        # Return demo data (either Schwab not available or credentials not configured)
        market_data = {
            "symbol": symbol,
            "price": round(150 + (hash(symbol) % 100) / 10, 2),
            "timestamp": str(int(time.time() * 1000)),
            "volume": 1000000,
            "change": "+0.5%",
            "note": "Demo mode - Schwab credentials not configured or client failed",
        }
        return jsonify({"success": True, "data": market_data})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/debug/schwab", methods=["GET"])
def debug_schwab():
    """Debug endpoint to test Schwab client integration"""
    try:
        app_key = os.getenv("CS_APP_KEY", "")
        app_secret = os.getenv("CS_APP_SECRET", "")

        debug_info = {
            "schwab_available": SCHWAB_AVAILABLE,
            "app_key_set": bool(app_key),
            "app_secret_set": bool(app_secret),
            "app_key_is_dummy": app_key == "dummy_key",
            "app_secret_is_dummy": app_secret == "dummy_secret",
            "should_use_real_data": SCHWAB_AVAILABLE
            and app_key
            and app_secret
            and app_key != "dummy_key"
            and app_secret != "dummy_secret",
        }

        if debug_info["should_use_real_data"]:
            try:
                client = get_client()
                debug_info["client_initialized"] = True

                accounts_resp = client.account_linked()
                accounts = accounts_resp.json()
                debug_info["accounts_count"] = len(accounts) if accounts else 0

                if accounts:
                    debug_info["first_account_hash"] = accounts[0]["hashValue"]

                    details_resp = client.account_details(accounts[0]["hashValue"])
                    details = details_resp.json()
                    debug_info["details_retrieved"] = bool(details)

                    if details:
                        securities_account = details.get("securitiesAccount", {})
                        initial_balances = securities_account.get("initialBalances", {})

                        debug_info["cash_balance"] = float(
                            initial_balances.get("cashBalance", 0)
                        )
                        debug_info["available_funds"] = float(
                            initial_balances.get("availableFunds", 0)
                        )
                        debug_info["buying_power"] = float(
                            initial_balances.get("buyingPower", 0)
                        )
                else:
                    debug_info["accounts_error"] = "No accounts found"

            except Exception as e:
                debug_info["client_error"] = str(e)

        return jsonify({"success": True, "data": debug_info})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/data/account", methods=["GET"])
def get_account_data():
    """Get account details"""
    try:
        # Check if Schwab is available and credentials are configured with real values (not dummy values)
        app_key = os.getenv("CS_APP_KEY", "")
        app_secret = os.getenv("CS_APP_SECRET", "")

        print(
            f"DEBUG: SCHWAB_AVAILABLE={SCHWAB_AVAILABLE}, app_key_set={bool(app_key)}, app_secret_set={bool(app_secret)}"
        )
        print(
            f"DEBUG: app_key_is_dummy={app_key == 'dummy_key'}, app_secret_is_dummy={app_secret == 'dummy_secret'}"
        )

        if (
            SCHWAB_AVAILABLE
            and app_key
            and app_secret
            and app_key != "dummy_key"
            and app_secret != "dummy_secret"
        ):
            print("DEBUG: Attempting to use real Schwab data")
            # Try to get real account data from Schwab
            try:
                client = get_client()
                if not client:
                    raise Exception("Failed to initialize Schwab client")

                # Get account details from Schwab
                accounts_resp = client.account_linked()
                accounts = accounts_resp.json()
                if not accounts:
                    raise Exception("No accounts found")

                account_hash = accounts[0]["hashValue"]

                # Get detailed account information
                details_resp = client.account_details(account_hash)
                details = details_resp.json()
                if not details:
                    raise Exception("Failed to get account details")

                securities_account = details.get("securitiesAccount", {})
                initial_balances = securities_account.get("initialBalances", {})

                account_data = {
                    "account_hash": account_hash,
                    "cash_balance": float(initial_balances.get("cashBalance", 0)),
                    "available_funds": float(initial_balances.get("availableFunds", 0)),
                    "buying_power": float(initial_balances.get("buyingPower", 0)),
                    "timestamp": str(int(time.time() * 1000)),
                    "note": "Real Schwab data",
                }

                print(f"✅ Successfully retrieved real account data for {account_hash}")
                return jsonify({"success": True, "data": account_data})

            except Exception as schwab_error:
                print(f"❌ Schwab client error: {schwab_error}")
                # Fall back to demo data if Schwab fails
                pass

        print("DEBUG: Falling back to demo data")
        # Return demo account data (either Schwab not available or credentials not configured)
        account_data = {
            "account_hash": "demo-account",
            "cash_balance": 10000.00,
            "available_funds": 8500.00,
            "buying_power": 17000.00,
            "timestamp": str(int(time.time() * 1000)),
            "note": "Demo mode - Schwab credentials not configured or client failed",
        }
        return jsonify({"success": True, "data": account_data})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/trading/positions", methods=["GET"])
def get_positions():
    """Get current positions"""
    try:
        # This would typically query DynamoDB
        # For now, return a placeholder
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

        # Publish trading signal
        messaging.publish_signal("start_trading", {"symbol": symbol})

        return jsonify({"success": True, "message": f"Trading started for {symbol}"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


@app.route("/trading/stop", methods=["POST"])
def stop_trading():
    """Stop trading bot"""
    try:
        messaging.publish_signal("stop_trading", {})

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

        # Publish order event
        messaging.publish_order_event(order_data)

        return jsonify(
            {"success": True, "message": "Order created", "order": order_data}
        )
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
