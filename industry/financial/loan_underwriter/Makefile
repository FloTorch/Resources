# Default target
.DEFAULT_GOAL := help

# Colors
CYAN  := \033[36m
RESET := \033[0m

# Run prod services
start:
	@echo "$(CYAN)🚀 Starting production services...$(RESET)"
	docker compose up --build

# Clean up containers/volumes
clean:
	@echo "$(CYAN)🧹 Cleaning up containers and volumes...$(RESET)"
	docker compose down -v

# Show help
help:
	@echo "Usage:"
	@echo "  make start      - Build and run services"
	@echo "  make clean      - Stop and remove containers + volumes"
