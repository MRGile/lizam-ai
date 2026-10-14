
from app.agents.qa import QAAgent


def test_all_routes_reviewed():
    result = QAAgent._calculate_route_coverage(
        ["routes/web.php", "routes/api.php"],
        {"routes/web.php", "routes/api.php"},
        True,
    )

    assert result["route_files_missing"] == []
    assert result["routing_review_incomplete"] is False
    print("PASS: Semua route sudah direview")


def test_some_routes_missing():
    result = QAAgent._calculate_route_coverage(
        ["routes/web.php", "routes/api.php"],
        {"routes/web.php"},
        True,
    )

    assert result["route_files_missing"] == ["routes/api.php"]
    assert result["routing_review_incomplete"] is True
    print("PASS: Route yang terlewat terdeteksi")


def test_no_route_available():
    result = QAAgent._calculate_route_coverage(
        [],
        set(),
        True,
    )

    assert result["route_files_missing"] == []
    assert result["routing_review_incomplete"] is True
    print("PASS: Task routing tanpa file route ditandai incomplete")


def test_not_routing_task():
    result = QAAgent._calculate_route_coverage(
        ["routes/web.php", "routes/api.php"],
        {"routes/web.php"},
        False,
    )

    assert result["route_files_missing"] == ["routes/api.php"]
    assert result["routing_review_incomplete"] is False
    print("PASS: Task non-routing tidak ditandai incomplete")


if __name__ == "__main__":
    test_all_routes_reviewed()
    test_some_routes_missing()
    test_no_route_available()
    test_not_routing_task()
