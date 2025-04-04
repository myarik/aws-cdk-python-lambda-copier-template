"""
Service stack
"""

import getpass

from aws_cdk import Stack, Tags, Duration, CfnOutput, aws_lambda_event_sources
from constructs import Construct
from aws_cdk import aws_apigateway as apigw, aws_sns as sns, aws_sns_subscriptions as subs, aws_sqs as sqs, \
    aws_iam as iam

import infrastructure.constants as constants
from infrastructure.lambdas import (
    LambdaConstruct,
    CommonLambdaLayerConstruct,
)

# Define the integration message template
message_template = (
    '{"body": $input.json(\'$\'), '
    '"auth": {"user_id": "$context.authorizer.user_id", "email": "$context.authorizer.email", '
    '"tier": "$context.authorizer.customer_tier"}, '
    '"request_time_epoch": "$context.requestTimeEpoch", '
    '"request_id": "$context.requestId"}'
)

class TicketRoutingStack(Stack):
    """
    Service to handle ticket routing
    """

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self._add_stack_tags()

        # Create common lambda layer
        lambda_layer = CommonLambdaLayerConstruct(
            self, f"{construct_id}-lambda-layer"
        )

        # Create the API Gateway
        api = apigw.RestApi(
            self,
            f"{construct_id}-rest-api",
            rest_api_name="Ticket Routing Rest API",
            description="The service handles user tickets /api/tickets",
            deploy_options=apigw.StageOptions(
                throttling_rate_limit=2,
                throttling_burst_limit=10,
            ),
        )
        # Add this after creating the API Gateway
        CfnOutput(
            self,
            "ApiGatewayUrl",
            value=api.url,
            description="URL of the API Gateway",
            export_name=f"{construct_id}-api-url",
        )

        # Create the lambda authorizer
        lambda_authorizer_construct = LambdaConstruct(
            self,
            f"{construct_id}-authorizer",
            f"{construct_id}-authorizer",
            "authorizer",
            layers=[lambda_layer.layer],
        )

        authorizer = apigw.TokenAuthorizer(
            self,
            "request-authorizer",
            handler=lambda_authorizer_construct.lambda_function,
            # Read the header "Token" to get the token
            identity_source=apigw.IdentitySource.header("Token"),
            # The name of the authorizer
            authorizer_name="RequestAuthorizer",
            # The TTL of the cache
            results_cache_ttl=Duration.seconds(constants.AUTHORIZER_CACHE_TTL),
        )

        # Create the requests resource
        api_resource = api.root.add_resource("tickets")

        # Creat the GET method

        # lambda to handle get method
        lambda_get_requests_constructor = LambdaConstruct(
            self,
            f"{construct_id}-user-tickets",
            f"{construct_id}-user-tickets",
            "tickets",
            layers=[lambda_layer.layer],
        )
        api_resource.add_method(
            "GET",
            apigw.LambdaIntegration(
                lambda_get_requests_constructor.lambda_function,
                proxy=True,
            ),
            authorizer=authorizer,
        )

        topic = sns.Topic(self, "TicketRouting", display_name="TicketRouting")

        # Create SQS queues and lambda functions to process the queues
        analytics_queue = sqs.Queue(
            self, "AnalyticsQueue", queue_name=f"{construct_id}-analytics"
        )
        analytics_constructor = LambdaConstruct(
            self,
            f"{construct_id}-analytics-processor",
            f"{construct_id}-analytics-processor",
            "processors.analytics",
            layers=[lambda_layer.layer],
        )

        priority_tickets_queue = sqs.Queue(
            self,
            "PriorityTicketsQueue",
            queue_name=f"{construct_id}-priority-tickets",
        )
        priority_channel_constructor = LambdaConstruct(
            self,
            f"{construct_id}-priority-channel-processor",
            f"{construct_id}-priority-channel-processor",
            "processors.priority_channel",
            layers=[lambda_layer.layer],
        )

        general_tickets_queue = sqs.Queue(
            self,
            "GeneralTicketsQueue",
            queue_name=f"{construct_id}-general-tickets"
        )
        general_channel_constructor = LambdaConstruct(
            self,
            f"{construct_id}-general-channel-processor",
            f"{construct_id}-general-channel-processor",
            "processors.general_channel",
            layers=[lambda_layer.layer],
        )

        # Set up event source mappings
        analytics_constructor.lambda_function.add_event_source(
            aws_lambda_event_sources.SqsEventSource(analytics_queue, batch_size=10)
        )
        priority_channel_constructor.lambda_function.add_event_source(
            aws_lambda_event_sources.SqsEventSource(
                priority_tickets_queue, batch_size=10
            )
        )
        general_channel_constructor.lambda_function.add_event_source(
            aws_lambda_event_sources.SqsEventSource(
                general_tickets_queue, batch_size=10
            )
        )

        # Subscribe the queues to the SNS topic with appropriate filter policies
        # All tickets
        topic.add_subscription(subs.SqsSubscription(analytics_queue))

        # Only gold tier tickets
        topic.add_subscription(
            subs.SqsSubscription(
                priority_tickets_queue,
                filter_policy={
                    "customer_tier": sns.SubscriptionFilter.string_filter(allowlist=["gold"])
                },
            )
        )
        # General tickets
        topic.add_subscription(
            subs.SqsSubscription(
                general_tickets_queue,
                filter_policy={
                    "customer_tier": sns.SubscriptionFilter.string_filter(denylist=["gold"])
                },
            )
        )

        ## Creat the POST method
        # Define the request template
        sns_request_template = (
            f"Action=Publish&"
            f"TopicArn=$util.urlEncode('{topic.topic_arn}')&"
            f"Message={message_template}&"
            f"MessageAttributes.entry.1.Name=customer_tier&"
            f"MessageAttributes.entry.1.Value.DataType=String&"
            f"MessageAttributes.entry.1.Value.StringValue=$context.authorizer.customer_tier"
        )

        # Create a model in API Gateway using the schema
        ticket_create_model = api.add_model(
            "TicketCreateModel",
            content_type="application/json",
            schema=apigw.JsonSchema(
                schema=apigw.JsonSchemaVersion.DRAFT4,
                title="TicketCreateModel",
                type=apigw.JsonSchemaType.OBJECT,
                properties={
                    "type": apigw.JsonSchemaType.STRING,
                    "message": apigw.JsonSchemaType.STRING,
                },
                required=["message", "type"],
            ),
        )

        ticket_create_validator = apigw.RequestValidator(
            self,
            "TicketCreateValidator",
            rest_api=api,
            # the properties below are optional
            request_validator_name="ticket-create-validator",
            validate_request_body=True,
        )

        # Create an IAM role for API Gateway to publish to SNS
        api_to_sns_role = iam.Role(
            self,
            "ApiToSnsRole",
            assumed_by=iam.ServicePrincipal("apigateway.amazonaws.com"),
        )
        topic.grant_publish(api_to_sns_role)

        # Create the POST method with SNS integration
        api_resource.add_method(
            "POST",
            apigw.AwsIntegration(
                service="sns",
                integration_http_method="POST",
                action="Publish",
                path="",
                options=apigw.IntegrationOptions(
                    credentials_role=api_to_sns_role,
                    passthrough_behavior=apigw.PassthroughBehavior.NEVER,
                    request_parameters={
                        "integration.request.header.Content-Type": "'application/x-www-form-urlencoded'"
                    },
                    request_templates={
                        "application/json": sns_request_template
                    },
                    integration_responses=[
                        apigw.IntegrationResponse(
                            status_code="200",
                            response_templates={"application/json": '{"message": "Ticket created successfully"}'},
                            response_parameters={
                                "method.response.header.Content-Type": "'application/json'",
                                "method.response.header.Access-Control-Allow-Origin": "'*'",
                                "method.response.header.Access-Control-Allow-Credentials": "'true'",
                            },
                        )
                    ],
                ),
            ),
            authorizer=authorizer,
            request_models={"application/json": ticket_create_model},
            request_validator=ticket_create_validator,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_parameters={
                        "method.response.header.Content-Type": True,
                        "method.response.header.Access-Control-Allow-Origin": True,
                        "method.response.header.Access-Control-Allow-Credentials": True,
                    },
                )
            ],
        )

    def _add_stack_tags(self) -> None:
        # best practice to help identify resources in the console
        Tags.of(self).add(constants.SERVICE_NAME_TAG, constants.SERVICE_NAME)
        Tags.of(self).add(constants.OWNER_TAG, getpass.getuser())
