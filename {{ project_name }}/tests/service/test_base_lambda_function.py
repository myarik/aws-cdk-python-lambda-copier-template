from service.handlers.handler import lambda_handler


def test_lambda_handler():
    event, context = {"title": "Test", "content": "Test message"}, {}
    response = lambda_handler(event, context)
    assert "Hello Lambda!" in response
