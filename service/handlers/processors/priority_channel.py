from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.batch import (
    BatchProcessor,
    EventType,
    process_partial_response,
)
from aws_lambda_powertools.utilities.data_classes.sqs_event import SQSRecord
from aws_lambda_powertools.utilities.typing import LambdaContext

processor = BatchProcessor(event_type=EventType.SQS)
logger = Logger(service="priority_channel")


def record_handler(record: SQSRecord):
    """
    Process SQS record
    """
    payload: str = record.json_body
    logger.info("Send request to priority channel", extra={"record": payload["Message"]})


@logger.inject_lambda_context(log_event=False)
def lambda_handler(event, context: LambdaContext):
    return process_partial_response(
        event=event,
        record_handler=record_handler,
        processor=processor,
        context=context,
    )