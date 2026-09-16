from botocore.exceptions import ClientError
import pytest

from src.aws_budgets import get_budgets


class FailingBudgets:
    def describe_budgets(self, **kwargs):
        raise ClientError({"Error": {"Code": "AccessDeniedException", "Message": "secret details"}}, "DescribeBudgets")


def test_access_denied_is_safely_classified():
    with pytest.raises(RuntimeError, match="permissions"):
        get_budgets("123456789012", client=FailingBudgets())
