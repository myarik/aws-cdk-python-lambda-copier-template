import pytest

from service.handlers.demo_lambda import lambda_handler


def test_lambda_handler():
    event, context = {"title": "Test", "content": "Test message"}, {}
    response = lambda_handler(event, context)
    assert "Test" in response
    assert "Test message" in response

    with pytest.raises(Exception):
        lambda_handler({"title": "Te", "content": "message"}, {})
