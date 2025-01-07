import pytest
from pipeline.headers import HeadersBuilder

def test_add_correlation_id():
    builder = HeadersBuilder()
    correlation_id = "1234abcd"

    builder.addCorrelationId(correlation_id)

    headers = builder.build()
    assert len(headers) == 1
    assert headers[0] == ("X-Correlation-ID", b"1234abcd")

def test_add_error_message():
    builder = HeadersBuilder()
    error_message = "Something went wrong"

    builder.addErrorMessage(error_message)

    headers = builder.build()
    assert len(headers) == 1
    assert headers[0] == ("X-Error-Message", b"Something went wrong")

def test_add_correlation_id_multiple_calls():
    builder = HeadersBuilder()
    builder.addCorrelationId("1234abcd")
    builder.addCorrelationId("5678efgh")

    headers = builder.build()
    assert len(headers) == 2
    assert headers[0] == ("X-Correlation-ID", b"1234abcd")
    assert headers[1] == ("X-Correlation-ID", b"5678efgh")

def test_add_error_message_multiple_calls():
    builder = HeadersBuilder()
    builder.addErrorMessage("Error 1")
    builder.addErrorMessage("Error 2")

    headers = builder.build()
    assert len(headers) == 2
    assert headers[0] == ("X-Error-Message", b"Error 1")
    assert headers[1] == ("X-Error-Message", b"Error 2")

def test_build_empty_headers():
    builder = HeadersBuilder()

    headers = builder.build()
    assert len(headers) == 0
