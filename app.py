#!/usr/bin/env python3
import os

import aws_cdk as cdk

from infrastructure.component import TicketRoutingStack
from infrastructure.constants import SERVICE_NAME

app = cdk.App()

TicketRoutingStack(
    app,
    SERVICE_NAME,
    env=cdk.Environment(
        account=os.getenv("AWS_DEFAULT_ACCOUNT"), region=os.getenv("AWS_DEFAULT_REGION")
    ),
)

app.synth()
