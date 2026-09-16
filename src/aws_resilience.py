from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, TypeVar

from botocore.config import Config
from botocore.exceptions import BotoCoreError, ClientError

T = TypeVar("T")

RETRY_CONFIG = Config(
    retries={"mode": "standard", "max_attempts": 5},
    connect_timeout=10,
    read_timeout=30,
)


@dataclass(frozen=True)
class AWSFailure:
    category: str
    message: str


class AWSObservationError(RuntimeError):
    """Safe, classified error raised by read-only AWS observation code."""

    def __init__(self, failure: AWSFailure):
        super().__init__(failure.message)
        self.failure = failure


def aws_client(service_name: str, region: str):
    """Create a read-only-use AWS client with bounded standard retries."""
    import boto3

    return boto3.client(service_name, region_name=region, config=RETRY_CONFIG)


def classify_aws_error(exc: BaseException) -> AWSFailure:
    """Map an AWS/client failure to a stable, non-sensitive application state."""
    if isinstance(exc, ClientError):
        error = exc.response.get("Error", {})
        code = str(error.get("Code", ""))
        lowered = code.lower()
        if "throttl" in lowered or lowered in {"requestlimitexceeded", "toomanyrequests"}:
            return AWSFailure("throttled", "AWS API request was throttled after retry handling.")
        if "accessdenied" in lowered or lowered in {"unauthorizedoperation", "unrecognizedclientexception"}:
            return AWSFailure("access-denied", "AWS permissions do not allow this read-only observation.")
        if "notfound" in lowered or lowered in {"resourcenotfoundexception", "invalidinstanceid.notfound"}:
            return AWSFailure("not-found", "The requested AWS resource was not found.")
        if "validation" in lowered or lowered.startswith("invalid"):
            return AWSFailure("validation", "AWS rejected the observation request parameters.")
        if code.startswith("5") or "internal" in lowered or "serviceunavailable" in lowered:
            return AWSFailure("service-error", "AWS returned a temporary service error.")
        return AWSFailure("aws-error", "AWS rejected the read-only observation request.")
    if isinstance(exc, BotoCoreError):
        return AWSFailure("transport-error", "The AWS API could not be reached or completed the request.")
    return AWSFailure("unknown", "The AWS observation could not be completed.")


def observe(operation: Callable[[], T]) -> T:
    """Execute an observation and convert AWS failures to safe application errors."""
    try:
        return operation()
    except AWSObservationError:
        raise
    except (ClientError, BotoCoreError) as exc:
        raise AWSObservationError(classify_aws_error(exc)) from exc


def safe_error_message(exc: BaseException) -> str:
    """Return a dashboard-safe message without exposing raw AWS response data."""
    if isinstance(exc, AWSObservationError):
        return exc.failure.message
    return classify_aws_error(exc).message
