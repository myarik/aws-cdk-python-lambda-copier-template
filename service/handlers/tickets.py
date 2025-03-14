"""
Returns mock user tickets
"""

import random
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, List

from aws_lambda_powertools import Logger
from aws_lambda_powertools.event_handler import APIGatewayRestResolver
from aws_lambda_powertools.utilities.typing import LambdaContext
from pydantic import BaseModel, Field

logger: Logger = Logger(service="tickets")
app = APIGatewayRestResolver(enable_validation=True)


class TicketType(str, Enum):
    """
    Request type enum
    """

    FINANCE = "finance"
    GENERAL = "general"


class Ticket(BaseModel):
    """
    Ticket model
    """

    type: TicketType = Field(..., description="Ticket type (finance or general)")
    subject: str = Field(..., description="Subject")
    message: str = Field(..., description="Message")
    created_at: str = Field(..., description="Created at")


def get_data(user_id: str) -> List[Ticket]:
    """
    Return mock user tickets
    """
    logger.debug("Generating mock user tickets", extra={"user_id": user_id})
    finance_requests = [
        ("Tax calculation review", "Need assistance with annual tax calculation"),
        ("Budget planning", "Requesting support for Q2 budget planning"),
        ("Investment strategy", "Looking for advice on portfolio diversification"),
        ("Expense report", "Monthly expense report needs verification"),
        ("Financial audit", "Request for internal audit documentation"),
    ]

    general_requests = [
        ("Account access", "Unable to access my dashboard"),
        ("Documentation help", "Need help finding user guides"),
        ("Service inquiry", "Questions about available services"),
        ("Update contact", "Need to update contact information"),
        ("Meeting request", "Scheduling a consultation call"),
    ]

    response = []
    for _ in range(5):
        # Randomly choose request type
        request_type = random.choice(list(TicketType))
        # Select appropriate request based on type
        subject, message = random.choice(
            finance_requests
            if request_type == TicketType.FINANCE
            else general_requests
        )
        # Generate random date within last 30 days
        created_at = (
            datetime.now() - timedelta(days=random.randint(0, 30))
        ).isoformat()

        record = Ticket(
            type=request_type, subject=subject, message=message, created_at=created_at
        )
        response.append(record)
    return response


@app.get("/tickets")
def get_requests() -> List[Ticket]:
    """
    Return user tickets
    """
    authorizer_data = app.current_event.request_context.authorizer
    return get_data(authorizer_data["user_id"])


def lambda_handler(event: Any, context: LambdaContext) -> str:
    """
    Return user tickets
    """
    return app.resolve(event, context)
