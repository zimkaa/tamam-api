up:
	docker compose -f docker-compose-local.yaml up -d

up-test:
	docker compose -f docker-compose-local-test.yaml up -d

build:
	docker compose -f docker-compose-local.yaml up -d --build

build-test:
	docker compose -f docker-compose-local-test.yaml up -d --build

down:
	docker compose -f docker-compose-local.yaml down && docker network prune --force

down-test:
	docker compose -f docker-compose-local-test.yaml down && docker network prune --force
