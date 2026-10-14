
from app.tools.workspace import Workspace
from app.tools.relevant_files import RelevantFileFinder
import os


def test_qa_auth_ranking():
    files = [
        r"routes\web.php",
        r"routes\api.php",
        r"app\Http\Controllers\Controller.php",
        r"app\Http\Controllers\Auth\LoginController.php",
        r"app\Http\Middleware\Authenticate.php",
        r"app\Models\User.php",
        r"config\auth.php",
        r"config\session.php",
    ]

    finder = RelevantFileFinder(files)
    results = finder.find(
        "Review keamanan autentikasi, password, session, dan user.",
        limit=8,
        role="qa",
    )

    ranked_files = [item["file"] for item in results]

    assert r"app\Http\Controllers\Auth\LoginController.php" in ranked_files
    assert ranked_files.index(
        r"app\Http\Controllers\Auth\LoginController.php"
    ) < ranked_files.index(r"app\Http\Controllers\Controller.php")

    print("PASS: Ranking autentikasi")


def test_qa_routing_ranking():
    files = [
        r"routes\web.php",
        r"routes\api.php",
        r"app\Http\Controllers\Controller.php",
        r"app\Http\Controllers\Auth\LoginController.php",
        r"app\Http\Middleware\Authenticate.php",
    ]

    finder = RelevantFileFinder(files)
    results = finder.find(
        "Review routing dan endpoint API pada project Laravel.",
        limit=5,
        role="qa",
    )

    ranked_files = [item["file"] for item in results]
    route_files = [r"routes\api.php", r"routes\web.php"]

    assert all(path in ranked_files for path in route_files)

    for route_file in route_files:
        assert ranked_files.index(route_file) < ranked_files.index(
            r"app\Http\Controllers\Controller.php"
        )

    print("PASS: Ranking routing")


def test_qa_combined_ranking():
    files = [
        r"routes\web.php",
        r"routes\api.php",
        r"app\Http\Controllers\Controller.php",
        r"app\Http\Controllers\Auth\LoginController.php",
        r"app\Http\Middleware\Authenticate.php",
        r"app\Models\User.php",
        r"config\auth.php",
        r"config\session.php",
    ]

    finder = RelevantFileFinder(files)
    results = finder.find(
        "Review keamanan dan potensi bug pada autentikasi dan routing Laravel.",
        limit=8,
        role="qa",
    )

    ranked_files = [item["file"] for item in results]

    expected_files = [
        r"routes\web.php",
        r"routes\api.php",
        r"app\Http\Controllers\Auth\LoginController.php",
        r"app\Http\Middleware\Authenticate.php",
        r"app\Models\User.php",
    ]

    assert all(path in ranked_files for path in expected_files)

    print("PASS: Ranking autentikasi dan routing")


def show_existing_agent_ranking():
    root = os.getenv("WORKSPACE_PATH", os.path.dirname(os.getcwd()))
    workspace = Workspace(root)
    files = sorted(workspace.list_files())
    finder = RelevantFileFinder(files)

    task = "Perbaiki halaman login dan API autentikasi"

    for role in ("frontend", "backend"):
        print(f"\n=== {role.upper()} AGENT ===")
        results = finder.find(task, limit=5, role=role)

        if not results:
            print("Tidak ada file yang cocok.")
            continue

        for item in results:
            print(f'{item["score"]:>3} | {item["file"]}')


if __name__ == "__main__":
    test_qa_auth_ranking()
    test_qa_routing_ranking()
    test_qa_combined_ranking()
    show_existing_agent_ranking()
