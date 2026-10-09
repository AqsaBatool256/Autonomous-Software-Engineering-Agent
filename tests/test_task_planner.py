from app.core.task_planner import create_fallback_plan


def test_fallback_plan_preserves_task():
    plan = create_fallback_plan("Add division-by-zero handling")

    assert plan.objective == "Add division-by-zero handling"


def test_fallback_plan_has_steps():
    plan = create_fallback_plan("Improve calculator")

    assert len(plan.steps) > 0


def test_fallback_plan_has_testing_strategy():
    plan = create_fallback_plan("Improve calculator")

    assert len(plan.testing_strategy) > 0


def test_fallback_plan_includes_safety_risks():
    plan = create_fallback_plan("Improve calculator")

    assert len(plan.risks) > 0
