# Running
start:
	docker-compose up --build -d

stop:
	docker-compose down

# Formatting
isort:
	docker-compose up -d app && docker exec -it template_app isort .

black:
	docker-compose up -d app && docker exec -it template_app black .

format: isort black

# Linting
flake8:
	docker-compose up -d app && docker exec -it template_app flake8 .

lint: flake8

# Testing
test:
	docker-compose up -d app && \
	docker exec -it template_app \
	pytest $(or $(target), tests) -p no:warnings -vv \
		   $(or $(foreach var, $(ignore), --ignore=$(var)), --ignore=tests/legacy) \
		   --cov=app --cov-report=term-missing

check: format lint test
