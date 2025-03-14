"""
Authorizer Lambda function
"""
from hmac import compare_digest
from typing import Any

from aws_lambda_powertools import Logger
from aws_lambda_powertools.utilities.typing import LambdaContext

logger: Logger = Logger(service="authorizer")


def generate_policy(
    principal_id: str, effect: str, resource: str, context=None
) -> dict:
    auth_response = {"principalId": principal_id}
    if effect and resource:
        policy_document = {
            "Version": "2012-10-17",
            "Statement": [
                {"Action": "execute-api:Invoke", "Effect": effect, "Resource": resource}
            ],
        }
        auth_response["policyDocument"] = policy_document
    if context:
        auth_response["context"] = context
    logger.debug("Generated auth response", extra={"auth_response": auth_response})
    return auth_response


def validate_token(token: str) -> bool:
    """
    Validate token
    """
    # Implement your token validation logic here
    return compare_digest(token, "QAB3RUYA4gsd") or compare_digest(token, "Avb3TU8O2ts1")


def get_user_information(token: str) -> dict[str, Any]:
    """
    Get user information
    """
    # Implement your user information retrieval logic here
    storage = {
        "QAB3RUYA4gsd": {
            "user_id": 3222,
            "email": "fakeuser123@example.com",
            "customer_tier": "silver"
        },
        "Avb3TU8O2ts1": {
            "user_id": 1234,
            "email": "fakeuser234@example.com",
            "customer_tier": "gold"
        }
    }

    return storage[token]


def lambda_handler(event: Any, context: LambdaContext):
    """
    Lambda function to authorize requests
    """
    if not validate_token(event["authorizationToken"]):
        return generate_policy("user", "Deny", event["methodArn"])
    return generate_policy(
        "user",
        "Allow",
        event["methodArn"],
        context=get_user_information(event["authorizationToken"]),
    )
