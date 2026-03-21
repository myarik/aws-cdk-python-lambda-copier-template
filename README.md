# AWS CDK Python Lambda — Copier Template

A [Copier](https://copier.readthedocs.io/) template for production-ready AWS Lambda services built with Python and AWS CDK.

## Features

- Python 3.14 Lambda with dependency Layer
- CloudWatch monitoring dashboard and alarms out of the box
- Pytest test suite for both infrastructure and service code
- Makefile automation for dev, test, build, and deploy workflows
- Pydantic input validation
- AWS Lambda Powertools integration (structured logging)
- Configurable license (30+ options)

## What You Get

The template generates a project with two CDK stacks:

**Lambda Stack**
- Python Lambda function with a dedicated dependency Layer
- CloudWatch Log Group (JSON format, 1-day retention)
- Environment variables pre-configured for Lambda Powertools

**Monitoring Stack**
- CloudWatch Dashboard — invocations, concurrency, latency percentiles (P50/P90/P99), errors, cold start analysis
- SNS Topic for alarm notifications
- CloudWatch Alarms — P90 latency > 30s, error count > 2 per 10 min

## Prerequisites

- Python 3.14+, [uv](https://docs.astral.sh/uv/), Node.js (for CDK CLI), AWS CLI with configured credentials
- [Copier](https://copier.readthedocs.io/)

Install Copier:

```bash
# With brew (recommended)
brew install copier
```

## Quick Start

**1. Generate a new project**

```bash
copier copy gh:myarik/aws-cdk-python-lambda-copier-template my-lambda-service
```

You'll be prompted for:

| Prompt | Description | Default |
|--------|-------------|---------|
| `project_name` | Project/service name | `my-lambda-service` |
| `author_name` | Author name | — |
| `author_email` | Author email | — |
| `copyright_holder` | Copyright holder | author name |
| `copyright_date` | Copyright year | `2026` |
| `copyright_license` | License type | `MIT` |

**2. Set up and run**

```bash
cd my-lambda-service
make dev          # Create venv & install dependencies
make test         # Run all tests
make deploy       # Build & deploy to AWS
```

## Generated Project Structure

```
my-lambda-service/
├── app.py                          # CDK app entry point
├── Makefile                        # Dev/build/deploy commands
├── pyproject.toml                  # Dependencies & project metadata
├── .envrc                          # direnv config (sets ENVIRONMENT=dev)
│
├── infrastructure/                 # AWS CDK infrastructure code
│   ├── component.py                # Main stack — Lambda + Layer
│   ├── monitoring.py               # Monitoring stack — dashboard & alarms
│   ├── constants.py                # Project-wide constants
│   └── basic_lambda/
│       └── construct.py            # Lambda construct definition
│
├── service/                        # Lambda application code
│   ├── handlers/
│   │   └── handler.py              # Lambda entry point
│   ├── models/
│   │   └── input.py                # Pydantic input model
│   └── logic/                      # Business logic (extend here)
│
└── tests/
    ├── infrastructure/             # CDK assertion tests
    │   ├── conftest.py             # Shared fixtures
    │   ├── test_lambda_stack.py    # Lambda stack tests
    │   └── test_monitoring_stack.py
    └── service/
        └── test_base_lambda_function.py  # Handler unit tests
```

## Available Make Commands

| Command | Description |
|---------|-------------|
| `make dev` | Create virtual environment and install dependencies |
| `make lint` | Run linting, formatting, and spell check |
| `make test` | Run all tests |
| `make test-infra` | Run infrastructure tests only |
| `make test-service` | Run service tests only |
| `make build` | Build Lambda package and dependency Layer |
| `make deploy` | Build and deploy all stacks to AWS |
| `make deploy-monitoring-dashboard` | Deploy monitoring stack only |
| `make destroy` | Destroy all deployed stacks |
| `make logs` | Fetch Lambda logs (`ENVIRONMENT=prod LAMBDA=hello_lambda make logs`) |

## Customization

| What | Where |
|------|-------|
| Add Lambda handlers | `service/handlers/` |
| Add business logic | `service/logic/` |
| Add/modify infrastructure | `infrastructure/` |
| Adjust monitoring & alarms | `infrastructure/monitoring.py` |
| Add dependencies | `pyproject.toml` |

## License

This template is available under the MIT License.

Generated projects use the license you select during setup.
