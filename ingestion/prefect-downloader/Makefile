TAG = v0.0.1
REPO = dhidna.azurecr.io/prefect-scatterometry-downloader

register:
	python downloader.py
	echo "Remember to set the flow schedule from the web UI, from the flow settings"
build:
	docker build -t ${REPO}:${TAG} .
push:
	docker push ${REPO}:${TAG}
register-flow: build push register

.PHONY: register build push register-flow