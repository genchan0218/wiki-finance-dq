.PHONY: up down test lint run install

up:
	docker compose up -d --build

down:
	docker compose down -v

install:
	pip install -e ".[dev]"

lint:
	ruff check .

test:
	pytest -q

run:
	python -m src.main
