REGISTRY = dhidna.azurecr.io
REPO = scatterometry-downloader
TAG = v0.0.1

build-dev:
	docker build -t ${REPO}:${TAG} .
build:
	docker build -t ${REGISTRY}/${REPO}:${TAG} .
push:
	docker push ${REGISTRY}/${REPO}:${TAG}

build-push: build push

.PHONY: build push build-push
