# Running
start:
	docker-compose up --build -d

stop:
	docker-compose down

# Formatting
isort:
	docker-compose up -d app && docker exec -it app isort .

black:
	docker-compose up -d app && docker exec -it app black .

format: isort black

# Linting
flake8:
	docker-compose up -d app && docker exec -it app flake8 .

lint: flake8

# Testing
test:
	docker-compose up -d app && docker exec -it app pytest $(or $(target), tests) -p no:warnings -vvv

check: format lint test
