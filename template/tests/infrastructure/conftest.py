"""
Shared fixtures for infrastructure tests
"""

import pytest
import aws_cdk as core
import aws_cdk.assertions as assertions

from infrastructure.component import PythonDemoMonitoringStack, PythonDemoStack


@pytest.fixture(scope="session")
def _stacks():
    app = core.App()
    lambda_stack = PythonDemoStack(app, "demo-cdk-test")
    monitoring_stack = PythonDemoMonitoringStack(
        app, "demo-cdk-monitoring-test", lambda_stack=lambda_stack
    )
    return lambda_stack, monitoring_stack


@pytest.fixture(scope="session")
def lambda_template(_stacks):
    return assertions.Template.from_stack(_stacks[0])


@pytest.fixture(scope="session")
def monitoring_template(_stacks):
    return assertions.Template.from_stack(_stacks[1])
