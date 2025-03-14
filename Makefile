.PHONY: format format-fix build deploy destroy
PYTHON := ".venv/bin/python3"
.ONESHELL:  # run all commands in a single shell, ensuring it runs within a local virtual env

format:
	uvx ruff check . --fix

format-fix:
	uvx ruff format .

build:
	mkdir -p .build/lambdas ; cp -r service .build/lambdas
	mkdir -p .build/layers ; uv export --frozen --no-emit-workspace --no-dev --no-editable -o .build/layers/requirements.txt

deploy: build
	npx cdk deploy --app="${PYTHON} ${PWD}/app.py" --require-approval=never

destroy:
	npx cdk destroy --app="${PYTHON} ${PWD}/app.py" --force
