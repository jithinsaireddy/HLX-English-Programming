SHELL := /bin/bash

.PHONY: dev backend frontend prod down

nlp-model:
	python -m spacy download en_core_web_sm

dev:
	bash run_dev.sh

backend:
	FLASK_APP=english_programming/src/interfaces/web/web_app.py flask run --port 5000

frontend:
	cd ui/english-ui && npm i && npm run dev

prod:
	docker compose up --build web frontend broker

down:
	docker compose down


