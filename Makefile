all:
	make build
	make up
	make backend-local

build:
	docker compose -f srcs/docker-compose.yml build

up:
	docker compose -f srcs/docker-compose.yml up

down:
	docker compose -f srcs/docker-compose.yml down

logs:
	docker compose logs -f

backend-local:
	cd srcs/backend && python3 -m venv venv && \
	bash -c "source venv/bin/activate && \
	pip install -r requirements.txt && \
	until nc -z localhost 5432; do sleep 1; done && \
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"


backend-shell:
	docker exec -it $$(docker ps -qf "name=backend") /bin/sh

frontend-shell:
	docker exec -it $$(docker ps -qf "name=frontend") /bin/sh

clean:
	docker compose -f srcs/docker-compose.yml down --rmi all --volumes --remove-orphans

.PHONY: all build up down clean backend-local