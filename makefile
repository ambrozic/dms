REGISTRY:=ambrozic/dms
RELEASE:=0.0.1
IMAGE:=${REGISTRY}:${RELEASE}

.PHONY: init install build serve test coverage docs fmt compile image publish
.SILENT: init install build serve test coverage docs fmt compile image publish

init: build lint test coverage

install:
	pip install --upgrade pip setuptools wheel && pip install .[postgresql]

build:
	pip install --upgrade pip setuptools wheel && pip install -e .[postgresql,sqlite,tests,docs]

serve:
	uvicorn dms.app:app --debug

test:
	py.test tests --verbose --capture=no

coverage:
	py.test --cov-report=term --cov=dms tests

docs:
	mkdocs serve

fmt:
	isort --recursive --multi-line=3 --combine-as --trailing-comma .
	black setup.py dms tests

compile:
	rm -rf build dist dms.egg-info && python setup.py bdist_wheel

image:
	docker build --squash --file=etc/dockerfile --tag=${IMAGE} .

publish:
	pip install wheel twine
	python setup.py sdist bdist_wheel --universal
	twine upload dist/*
	rm -rf build dist dms.egg-info
