from pathlib import Path


class RelevantFileFinder:
    KEYWORD_GROUPS = {
        "login": {
            "login",
            "signin",
            "sign-in",
            "masuk",
        },
        "auth": {
            "auth",
            "authentication",
            "authenticate",
            "autentikasi",
            "password",
            "credential",
            "credentials",
            "session",
            "token",
            "user",
            "pengguna",
        },
        "api": {
            "api",
            "endpoint",
            "route",
            "routing",
            "rest",
        },
        "frontend": {
            "frontend",
            "front-end",
            "ui",
            "ux",
            "blade",
            "html",
            "css",
            "javascript",
            "js",
            "jsx",
            "tsx",
            "vue",
            "component",
            "view",
            "halaman",
            "page",
            "tampilan",
        },
        "backend": {
            "backend",
            "back-end",
            "controller",
            "model",
            "migration",
            "service",
            "repository",
            "middleware",
            "database",
            "db",
            "laravel",
            "php",
        },
    }

    KEYWORD_ALIASES = {
        "login": {
            "login",
            "signin",
            "sign-in",
            "masuk",
            "auth",
            "user",
            "session",
            "password",
        },
        "autentikasi": {
            "autentikasi",
            "auth",
            "authentication",
            "authenticate",
            "user",
            "session",
            "token",
            "password",
        },
        "api": {
            "api",
            "endpoint",
            "route",
            "routing",
            "controller",
            "rest",
        },
        "halaman": {
            "halaman",
            "page",
            "view",
            "blade",
            "html",
            "component",
        },
    }

    def __init__(self, files: list[str]):
        self.files = files

    def _task_keywords(self, task: str) -> set[str]:
        task_lower = task.lower()
        keywords = set()

        for group_keywords in self.KEYWORD_GROUPS.values():
            for keyword in group_keywords:
                if keyword in task_lower:
                    keywords.add(keyword)

        return keywords

    def _expand_keywords(
        self,
        task_keywords: set[str],
    ) -> set[str]:
        expanded = set(task_keywords)

        for keyword in task_keywords:
            aliases = self.KEYWORD_ALIASES.get(keyword, set())
            expanded.update(aliases)

        return expanded

    def _score_file(
        self,
        file_path: str,
        task_keywords: set[str],
    ) -> int:
        normalized_path = file_path.lower()
        filename = Path(file_path).name.lower()

        expanded_keywords = self._expand_keywords(task_keywords)

        score = 0

        # 1. Kecocokan nama file
        for keyword in expanded_keywords:
            if keyword in filename:
                score += 5
            elif keyword in normalized_path:
                score += 3

        # 2. Deteksi jenis task
        is_auth_task = bool(
            task_keywords.intersection({
                "login",
                "autentikasi",
                "auth",
                "authentication",
                "password",
                "credential",
                "session",
                "token",
            })
        )

        is_api_task = bool(
            task_keywords.intersection({
                "api",
                "endpoint",
                "route",
                "routing",
                "rest",
            })
        )

        is_frontend_task = bool(
            task_keywords.intersection({
                "frontend",
                "front-end",
                "ui",
                "ux",
                "blade",
                "html",
                "css",
                "javascript",
                "js",
                "jsx",
                "tsx",
                "vue",
                "component",
                "view",
                "halaman",
                "page",
                "tampilan",
            })
        )

                # 3. Auth → prioritaskan file autentikasi
        if is_auth_task:
            if "/auth/" in normalized_path or "\\auth\\" in normalized_path:
                score += 8

            if filename in {
                "auth.php",
                "user.php",
                "session.php",
            }:
                score += 7

            if "authcontroller" in filename:
                score += 10

            if "controller" in normalized_path:
                score += 3

            if "middleware" in normalized_path:
                score += 4

            if (
                "models" in normalized_path
                and "user" in filename
            ):
                score += 7

            if (
                "resources/views/" in normalized_path
                or "resources\\views\\" in normalized_path
            ):
                score += 2

        # 4. API → prioritaskan routes/controller
        if is_api_task:
            if (
                "/routes/" in normalized_path
                or "\\routes\\" in normalized_path
            ):
                score += 8

            if filename == "api.php":
                score += 10

            if filename == "web.php":
                score += 4

            if "controller" in normalized_path:
                score += 5

        # 5. Frontend → prioritaskan halaman frontend
        if is_frontend_task:
            if (
                "/resources/views/" in normalized_path
                or "resources\\views\\" in normalized_path
            ):
                score += 5

            if filename.endswith(".blade.php"):
                score += 2

            if filename.endswith((".html", ".css", ".js")):
                score += 2

            # Halaman umum tidak boleh mengalahkan file
            # yang memiliki konteks login/auth.
            if is_auth_task:
                if filename in {
                    "welcome.blade.php",
                    "index.blade.php",
                }:
                    score -= 5

        # 6. Penalti provider AI
        if (
            "/providers/" in normalized_path
            or "\\providers\\" in normalized_path
        ):
            score -= 5

        # 7. Penalti internal AI service
        if "ai-service" in normalized_path:
            score -= 3

        return max(score, 0)

    def find(
        self,
        task: str,
        limit: int = 10,
    ) -> list[dict]:
        task_keywords = self._task_keywords(task)

        scored_files = []

        for file_path in self.files:
            score = self._score_file(
                file_path,
                task_keywords,
            )

            if score <= 0:
                continue

            scored_files.append(
                {
                    "file": file_path,
                    "score": score,
                }
            )

        scored_files.sort(
            key=lambda item: (
                -item["score"],
                item["file"],
            )
        )

        return scored_files[:limit]