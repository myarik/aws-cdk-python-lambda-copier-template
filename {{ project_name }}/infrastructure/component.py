"""
Service stack
"""

import getpass

from aws_cdk import Stack, Tags, Duration
from constructs import Construct

import infrastructure.constants as constants
from infrastructure.basic_lambda.construct import DemoLambdaConstruct
from infrastructure.monitoring import MonitoringDashboard


class PythonDemoStack(Stack):
    """
    Python Demo Stack - Lambda function only
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self._add_stack_tags()

        # Create a simple lambda function
        demo_lambda_construct = DemoLambdaConstruct(
            self,
            f"{construct_id}-hello_lambda",
        )

        self.lambda_function = demo_lambda_construct.lambda_function
        self.lambda_construct_id = demo_lambda_construct.construct_id

    def _add_stack_tags(self) -> None:
        # best practice to help identify resources in the console
        Tags.of(self).add(constants.PROJECT_NAME_TAG, constants.PROJECT_NAME)
        Tags.of(self).add(constants.OWNER_TAG, getpass.getuser())


class PythonDemoMonitoringStack(Stack):
    """
    Monitoring Stack - dashboard, SNS topic, alarms
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        lambda_stack: PythonDemoStack,
        **kwargs,
    ) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self._add_stack_tags()

        monitoring_dashboard = MonitoringDashboard(
            self,
            f"{construct_id}-monitoring",
            "Observation",
        )

        monitoring_dashboard.add_lambda_function_metrics(lambda_stack.lambda_function)
        monitoring_dashboard.add_p90_latency_lambda_alarm(
            lambda_stack.lambda_construct_id,
            lambda_stack.lambda_function,
            threshold_duration=Duration.seconds(30),
        )
        monitoring_dashboard.add_error_rate_lambda_alarm(
            lambda_stack.lambda_construct_id,
            lambda_stack.lambda_function,
            threshold_max_count=2,
        )

    def _add_stack_tags(self) -> None:
        Tags.of(self).add(constants.PROJECT_NAME_TAG, constants.PROJECT_NAME)
        Tags.of(self).add(constants.OWNER_TAG, getpass.getuser())
