"""
Test Lambda Stack
"""


def test_lambda_created(lambda_template):
    # Extra function for log rotation
    lambda_template.resource_count_is("AWS::Lambda::Function", 2)


def test_no_monitoring_resources(lambda_template):
    lambda_template.resource_count_is("AWS::CloudWatch::Dashboard", 0)
    lambda_template.resource_count_is("AWS::SNS::Topic", 0)
    lambda_template.resource_count_is("AWS::CloudWatch::Alarm", 0)
