"""
Monitoring module for the infrastructure package.
"""

from aws_cdk import aws_cloudwatch as cloudwatch, Duration
from aws_cdk import aws_lambda as _lambda
from aws_cdk import aws_sns as sns
from aws_cdk import aws_cloudwatch_actions as cloudwatch_actions
from aws_cdk import aws_iam as iam
from constructs import Construct


class MonitoringDashboard(Construct):
    def __init__(
        self, scope: Construct, construct_id: str, dashboard_name: str
    ) -> None:
        super().__init__(scope, construct_id)
        self.construct_id = construct_id
        self.dashboard_name = dashboard_name
        self.dashboard = self._create_dashboard()
        self.alarm_topic = self._create_alarm_topic()

    def _create_dashboard(self) -> cloudwatch.Dashboard:
        """
        Create the dashboard
        """
        return cloudwatch.Dashboard(
            self,
            self.construct_id,
            dashboard_name=self.dashboard_name,
            start="-P24H",
        )

    def _create_alarm_topic(self) -> sns.Topic:
        """
        Create an SNS topic for alarms
        """
        topic = sns.Topic(
            self,
            f"{self.construct_id}AlarmTopic",
            topic_name=f"{self.construct_id}AlarmTopic",
        )
        # Grant CloudWatch permissions to publish to the SNS topic
        topic.add_to_resource_policy(
            statement=iam.PolicyStatement(
                actions=["sns:Publish"],
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal("cloudwatch.amazonaws.com")],
                resources=[topic.topic_arn],
            )
        )
        return topic

    def add_lambda_function_metrics(self, lambda_function: _lambda.Function) -> None:
        """
        Add graphs for the Lambda function's metrics:
            - invocations
            - concurrency
            - latency
            - errors
            - execution report
        """
        error_log_filter = (
            "filter (ispresent(log_level) and log_level = 'ERROR') "
            "or (ispresent(level) and level = 'ERROR')"
        )
        # noinspection PyTypeChecker
        self.dashboard.add_widgets(
            cloudwatch.TextWidget(
                markdown=f"## Lambda function -- {lambda_function.function_name}\n",
                width=24,
                height=2,
            ),
            cloudwatch.Row(
                cloudwatch.GraphWidget(
                    title="Invocations",
                    width=12,
                    left=[
                        lambda_function.metric_invocations(
                            label="Invocations",
                            statistic="Sum",
                            period=Duration.minutes(5),
                        ),
                        lambda_function.metric_all_concurrent_executions(
                            label="Concurrent executions",
                            statistic="Maximum",
                            period=Duration.minutes(5),
                        ),
                    ],
                ),
                cloudwatch.GraphWidget(
                    title="Latency",
                    width=12,
                    left=[
                        lambda_function.metric_duration(
                            label="P50", statistic="p50", period=Duration.minutes(5)
                        ),
                        lambda_function.metric_duration(
                            label="P90", statistic="p90", period=Duration.minutes(5)
                        ),
                        lambda_function.metric_duration(
                            label="P99", statistic="p99", period=Duration.minutes(5)
                        ),
                    ],
                ),
                cloudwatch.GraphWidget(
                    title="Errors",
                    width=12,
                    left=[
                        lambda_function.metric_errors(
                            label="Errors", statistic="Sum", period=Duration.minutes(5)
                        )
                    ],
                ),
                cloudwatch.LogQueryWidget(
                    title="Recent 20 Errors",
                    log_group_names=[lambda_function.log_group.log_group_name],
                    query_lines=[
                        "fields @timestamp, @message",
                        error_log_filter,
                        "sort @timestamp desc",
                        "limit 20",
                    ],
                    width=12,
                    height=6,
                ),
                cloudwatch.LogQueryWidget(
                    title="Execution Report",
                    log_group_names=[lambda_function.log_group.log_group_name],
                    query_lines=[
                        'filter @type = "REPORT"',
                        r"parse @message /Init Duration: (?<init>\S+)/",
                        "stats count() as total, \n"
                        "count(init) as coldStartCount, \n"
                        "coldStartCount/total*100 as coldPercent, \n"
                        "avg(init) as avgInitDuration, \n"
                        "max(init) as maxInitDuration, \n"
                        "min(@duration) as minDuration, \n"
                        "max(@duration) as maxDuration, \n"
                        "avg(@duration) as avgDuration, \n"
                        "avg(@maxMemoryUsed)/1024/1024 as memoryused \n"
                        "by bin (30min) #Group by 30 minute windows",
                    ],
                    width=24,
                    height=6,
                ),
            ),
        )

    def add_p90_latency_lambda_alarm(
        self,
        construct_id: str,
        lambda_function: _lambda.Function,
        threshold_duration: Duration,
    ) -> None:
        """
        Add P90 latency alarm for the lambda function
        """
        alarm = cloudwatch.Alarm(
            self,
            f"{self.dashboard_name}-{construct_id}-Latency-P90",
            alarm_name=f"{self.dashboard_name}-{construct_id}-Latency-P90",
            metric=lambda_function.metric_duration(
                label="P90", statistic="p90", period=Duration.minutes(5)
            ),
            threshold=threshold_duration.to_milliseconds(),
            evaluation_periods=2,
            datapoints_to_alarm=2,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            alarm_description="P90 latency is high.",
        )
        alarm.add_alarm_action(cloudwatch_actions.SnsAction(self.alarm_topic))

    def add_error_rate_lambda_alarm(
        self,
        construct_id: str,
        lambda_function: _lambda.Function,
        threshold_max_count: int,
    ) -> None:
        """
        Add error rate alarm for the lambda function
        """
        alarm = cloudwatch.Alarm(
            self,
            f"{self.dashboard_name}-{construct_id}-Error",
            alarm_name=f"{self.dashboard_name}-{construct_id}-Error",
            metric=lambda_function.metric_errors(
                label="Errors", statistic="Sum", period=Duration.minutes(10)
            ),
            threshold=threshold_max_count,
            evaluation_periods=1,
            datapoints_to_alarm=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            alarm_description="Error count is high.",
        )
        alarm.add_alarm_action(cloudwatch_actions.SnsAction(self.alarm_topic))
