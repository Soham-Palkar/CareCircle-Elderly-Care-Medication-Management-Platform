.PHONY: up down migrate seed test lint shell

up:
	docker compose up -d

down:
	docker compose down

migrate:
	docker compose exec api alembic upgrade head

seed:
	docker compose exec api python -m scripts.seed_demo

test:
	cd backend && pytest

lint:
	cd backend && ruff check . && black --check .

shell:
	docker compose exec api bash
