up:
	docker compose -f docker-compose-local.yaml up -d

up-test:
	docker compose -f docker-compose-local-test.yaml up -d

build:
	python3 ./back_end/build.py -p
	./version.sh
	docker compose -f docker-compose-local.yaml up -d --build

build-without-d:
	python3 ./back_end/build.py -p
	./version.sh
	docker compose -f docker-compose-local.yaml up --build

build-test:
	python3 ./back_end/build.py
	./version.sh
	docker compose -f docker-compose-local-test.yaml up -d --build

build-test-without-d:
	python3 ./back_end/build.py
	./version.sh
	docker compose -f docker-compose-local-test.yaml up --build

down:
	docker compose -f docker-compose-local.yaml down && docker network prune --force

down-test:
	docker compose -f docker-compose-local-test.yaml down && docker network prune --force
