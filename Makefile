# Running
start:
	docker-compose up --build -d

stop:
	docker-compose down

# Formatting
isort:
	docker-compose up -d app && docker exec -it carts isort .

black:
	docker-compose up -d app && docker exec -it carts black .

format: isort black

# Linting
flake8:
	docker-compose up -d app && docker exec -it carts flake8 .

imports:
	docker-compose up -d app && docker exec -it carts lint-imports

lint: flake8 imports

# Testing
test:
	docker-compose up -d app && \
	docker exec -it carts \
	pytest $(or $(target), tests) -p no:warnings -vv \
		   $(or $(foreach var, $(ignore), --ignore=$(var)), --ignore=tests/legacy) \
		   --cov=app --cov-report=term-missing

# DB utils
migration:
	docker-compose up -d app && \
	docker exec -it carts \
	alembic revision --autogenerate --message $(message)

migrate:
	docker-compose up -d app && \
	docker exec -it carts \
	alembic upgrade head

downgrade:
	docker-compose up -d app && \
	docker exec -it carts \
	alembic downgrade -1

clear-db:
	docker-compose up -d app && \
	docker exec -it carts \
	alembic downgrade base

check: format lint test
