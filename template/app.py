#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infrastructure.component import PythonDemoStack, PythonDemoMonitoringStack

from infrastructure.utils import get_stack_name, get_monitoring_stack_name

app = cdk.App()

env = cdk.Environment(
    account=os.getenv("AWS_DEFAULT_ACCOUNT"), region=os.getenv("AWS_DEFAULT_REGION")
)

lambda_stack = PythonDemoStack(
    app,
    get_stack_name(),
    env=env,
)

PythonDemoMonitoringStack(
    app,
    get_monitoring_stack_name(),
    lambda_stack=lambda_stack,
    env=env,
)

app.synth()
