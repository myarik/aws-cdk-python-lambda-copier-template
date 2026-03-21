"""
Simple lambda handler
"""

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.parser import event_parser
from aws_lambda_powertools.utilities.typing import LambdaContext

from service.models.input import InputDataModel


logger: Logger = Logger()


@event_parser
def lambda_handler(event: InputDataModel, context: LambdaContext) -> str:
    """
    Simple lambda handler
    """
    logger.debug("Received event", extra={"event": event})
    return f"Hello Lambda!"
