DOCKER_REPO=ghcr.io/wayhomeuk/random-price-index-service

build:
	docker build -f Dockerfile.updater --tag ${DOCKER_REPO}/updater:latest .
	docker build -f Dockerfile.api --tag ${DOCKER_REPO}/api:latest .

push:
	docker push ${DOCKER_REPO}/updater:latest
	docker push ${DOCKER_REPO}/api:latest
