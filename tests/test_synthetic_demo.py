from src.synthetic_demo import make_synthetic_panel, run_synthetic_demo


def test_synthetic_demo_is_deterministic_and_labeled() -> None:
    assert make_synthetic_panel().equals(make_synthetic_panel())
    result = run_synthetic_demo()
    assert result["data"] == "synthetic_only"
    assert result["evaluation_sessions"] > 0
    assert result["baseline_qlike"] > 0
