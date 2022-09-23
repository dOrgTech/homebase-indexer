venv-activate:
	source venv/bin/activate

install:
	pip install -r requirements.txt

start:
	dipdup -e .env run

wipe-schema:
	dipdup -e .env schema wipe