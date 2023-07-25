# makefile for weather



check:
	vulture --exclude .venv,mapnik,weather/settings.py .

install:
	npm install --save-dev @types/leaflet
	npm install --save-dev @types/bootstrap
