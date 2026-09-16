from botocore.exceptions import BotoCoreError, ClientError

from src.aws_resilience import (
    AWSObservationError,
    RETRY_CONFIG,
    classify_aws_error,
    observe,
    safe_error_message,
)


def client_error(code: str) -> ClientError:
    return ClientError({"Error": {"Code": code, "Message": "sensitive service detail"}}, "GetMetricData")


def test_retry_config_uses_standard_bounded_retries():
    assert RETRY_CONFIG.retries["mode"] == "standard"
    assert RETRY_CONFIG.retries["max_attempts"] == 5
    assert RETRY_CONFIG.connect_timeout == 10
    assert RETRY_CONFIG.read_timeout == 30


def test_throttling_is_classified_separately():
    failure = classify_aws_error(client_error("ThrottlingException"))
    assert failure.category == "throttled"
    assert "sensitive" not in failure.message


def test_access_denied_is_classified_without_raw_error_details():
    failure = classify_aws_error(client_error("AccessDeniedException"))
    assert failure.category == "access-denied"
    assert failure.message == "AWS permissions do not allow this read-only observation."


def test_validation_and_not_found_are_distinct():
    assert classify_aws_error(client_error("ValidationException")).category == "validation"
    assert classify_aws_error(client_error("ResourceNotFoundException")).category == "not-found"


def test_transport_errors_are_explicit():
    failure = classify_aws_error(BotoCoreError())
    assert failure.category == "transport-error"


def test_observe_converts_aws_failures_to_safe_application_errors():
    try:
        observe(lambda: (_ for _ in ()).throw(client_error("ThrottlingException")))
    except AWSObservationError as exc:
        assert exc.failure.category == "throttled"
        assert "sensitive" not in str(exc)
    else:
        raise AssertionError("expected AWSObservationError")


def test_safe_error_message_never_returns_raw_client_error():
    message = safe_error_message(client_error("InternalFailure"))
    assert message == "AWS returned a temporary service error."
    assert "sensitive" not in message
