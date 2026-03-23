"""
Test Monitoring Stack
"""


def test_dashboard_created(monitoring_template):
    monitoring_template.resource_count_is("AWS::CloudWatch::Dashboard", 1)


def test_sns_topic_created(monitoring_template):
    monitoring_template.resource_count_is("AWS::SNS::Topic", 1)


def test_alarms_created(monitoring_template):
    # P90 latency alarm + error rate alarm
    monitoring_template.resource_count_is("AWS::CloudWatch::Alarm", 2)
