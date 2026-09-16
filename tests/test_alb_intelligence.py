from src.alb_intelligence import build_alb_intelligence


def test_alb_intelligence_flags_review_signals():
    inventory = [{
        "load_balancer_arn": "arn:aws:elasticloadbalancing:us-east-1:123:loadbalancer/app/demo/abc",
        "name": "demo",
        "type": "application",
        "scheme": "internet-facing",
        "state": "active",
    }]
    metrics = [{
        "load_balancer_arn": inventory[0]["load_balancer_arn"],
        "request_count_average": 0.5,
        "processed_bytes_average": 2_000_000_000.0,
        "active_connections_average": 4.0,
        "new_connections_average": 2.0,
        "target_response_time_average": 2.0,
    }]
    row = build_alb_intelligence(inventory, metrics)[0]
    assert "low-request-activity-review" in row["signals"]
    assert "high-processed-bytes-review" in row["signals"]
    assert "high-target-response-time-review" in row["signals"]


def test_missing_alb_metrics_are_not_zero():
    row = build_alb_intelligence(
        [{"load_balancer_arn": "arn:test", "state": "active"}], []
    )[0]
    assert row["metrics_status"] == "not-available"
    assert row["signals"] == ()
