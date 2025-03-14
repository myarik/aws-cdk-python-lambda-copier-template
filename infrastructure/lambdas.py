"""
Simple Lambda Construct
"""

from typing import Any

from aws_cdk import aws_lambda as _lambda, Duration, RemovalPolicy
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from aws_cdk.aws_logs import RetentionDays
from constructs import Construct

import infrastructure.constants as constants


class CommonLambdaLayerConstruct(Construct):
    """
    Common Lambda Layer Construct
    """

    def __init__(self, scope: Construct, construct_id: str) -> None:
        super().__init__(scope, construct_id)
        self.construct_id = construct_id
        self.layer = self._build_lambda_layer()

    def _build_lambda_layer(self) -> PythonLayerVersion:
        """
        Build a Lambda Layer
        """
        return PythonLayerVersion(
            self,
            f"{self.construct_id}_layer",
            entry=constants.LAYER_BUILD_FOLDER,
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            removal_policy=RemovalPolicy.DESTROY,
        )


class LambdaConstruct(Construct):
    """
    Lambda Construct
    """

    def __init__(
        self,
        scope: Construct,
        construct_id: str,
        name: str,
        file_name: str,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        """
        Initialize Lambda Construct
        """
        super().__init__(scope, construct_id)
        self.construct_id = construct_id
        self.lambda_function = self._build_lambda_function(
            name, file_name, *args, **kwargs
        )

    def _build_lambda_function(
        self, name: str, file_name: str, *args: Any, **kwargs: Any
    ) -> _lambda.Function:
        """
        Basic Python Lambda Function
        """
        return _lambda.Function(
            self,
            name,
            function_name=self.construct_id,
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset(constants.BUILD_FOLDER),
            handler=f"service.handlers.{file_name}.lambda_handler",
            environment={
                "POWERTOOLS_SERVICE_NAME": self.construct_id,  # for logger, tracer and metrics
                "POWERTOOLS_TRACE_DISABLED": "true",  # for tracer
                "AWS_LAMBDA_LOG_LEVEL": constants.LOG_LEVEL,  # for logger
            },
            tracing=_lambda.Tracing.DISABLED,
            retry_attempts=0,
            timeout=Duration.seconds(constants.HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.HANDLER_LAMBDA_MEMORY_SIZE,
            layers=kwargs.get("layers", []),
            log_retention=RetentionDays.ONE_DAY,
            log_format=_lambda.LogFormat.JSON.value,
            system_log_level_v2=_lambda.SystemLogLevel.INFO,
            application_log_level_v2=_lambda.ApplicationLogLevel.DEBUG,
        )
