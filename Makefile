SHELL := /bin/bash

.PHONY: dev backend frontend prod down gen-synonyms rebuild run-smoke

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

gen-synonyms:
	python -m english_programming.tools.generate_synonyms --output english_programming/config/synonyms.generated.yml --cap 1000

rebuild:
	docker compose build web frontend && docker compose up -d

run-smoke:
	@curl -sS -X POST -H 'Content-Type: application/json' \
	  --data '{"code":"create a list called xs\ninsert 9 into list xs\ncount of xs store in n\nprint n"}' \
	  http://localhost:5173/api/epl/exec | sed 's/\\n/\n/g' | head -200


