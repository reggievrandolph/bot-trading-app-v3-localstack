COMPOSE_FILE := docker-compose.yml
TICKER = SPY

# Define shared services
SHARED_SERVICES := ui-api strategy trader_bot order_management frontend account

.PHONY: live simulated start stop frontend down

live:
	@echo "🚀 Starting in LIVE mode with TICKER=$(TICKER)"
	MODE=live TICKER=$(TICKER) docker compose --profile live up --build -d redis data_ingestion $(SHARED_SERVICES)
	@echo "🌍 Opening frontend..."
	open http://localhost:3000

simulated:
	@echo "🧪 Starting in SIMULATED mode with TICKER=$(TICKER)"
	MODE=simulated TICKER=$(TICKER) docker compose up --build -d redis simulated_data_ingestion $(SHARED_SERVICES)
	@echo "🌍 Opening frontend..."
	open http://localhost:3000

stop:
	@echo "🛑 Stopping all services..."
	docker compose -f $(COMPOSE_FILE) down

frontend:
	@echo "🔄 Rebuilding and restarting frontend only..."
	docker compose up --build -d frontend
	open http://localhost:3000
