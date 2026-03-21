""" """

import os
import infrastructure.constants as constants


def get_stack_name() -> str:
    """
    Returns a stack name
    """
    cicd_environment = os.getenv("ENVIRONMENT", "dev")
    return f"{constants.PROJECT_NAME}--{cicd_environment}"


def get_monitoring_stack_name() -> str:
    """
    Returns the monitoring stack name
    """
    cicd_environment = os.getenv("ENVIRONMENT", "dev")
    return f"{constants.PROJECT_NAME}-monitoring--{cicd_environment}"
