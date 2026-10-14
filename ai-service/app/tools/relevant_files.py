
from pathlib import Path


class RelevantFileFinder:
    KEYWORD_GROUPS = {
        "login": {"login", "signin", "sign-in", "masuk"},
        "auth": {
            "auth", "authentication", "authenticate", "autentikasi",
            "password", "credential", "credentials", "session",
            "token", "user", "pengguna",
        },
        "api": {"api", "endpoint", "route", "routing", "rest"},
        "frontend": {
            "frontend", "front-end", "ui", "ux", "blade", "html",
            "css", "javascript", "js", "jsx", "tsx", "vue",
            "component", "view", "halaman", "page", "tampilan",
        },
        "backend": {
            "backend", "back-end", "controller", "model", "migration",
            "service", "repository", "middleware", "database", "db",
            "laravel", "php",
        },
        
        "qa": {
            "qa",
            "test",
            "testing",
            "testing",
            "review",
            "bug",
            "debug",
            "security",
            "keamanan",
            "vulnerability",
            "kerentanan",
            "quality",
            "kualitas",
        },
        
        "keamanan": {
            "keamanan",
            "security",
            "auth",
            "authentication",
            "middleware",
            "password",
            "session",
        },
        "review": {
            "review",
            "qa",
            "test",
            "testing",
            "bug",
            "security",
            "keamanan",
        },
        "routing": {
            "routing",
            "route",
            "routes",
            "web.php",
            "api.php",
            "controller",
        },


    }

    KEYWORD_ALIASES = {
        "login": {
            "login", "signin", "sign-in", "masuk", "auth",
            "user", "session", "password",
        },
        "autentikasi": {
            "autentikasi", "auth", "authentication", "authenticate",
            "user", "session", "token", "password",
        },
        "api": {"api", "endpoint", "route", "routing", "controller", "rest"},
        "halaman": {"halaman", "page", "view", "blade", "html", "component"},
    }

    FRONTEND_EXTENSIONS = {
        ".blade.php", ".html", ".css", ".js", ".jsx",
        ".ts", ".tsx", ".vue", ".scss", ".sass",
    }

    FRONTEND_PATHS = (
        "resources/views/",
        "resources/css/",
        "resources/js/",
        "public/css/",
        "public/js/",
        "public/build/",
    )

    BACKEND_PATHS = (
        "app/http/controllers/",
        "app/http/middleware/",
        "app/models/",
        "app/services/",
        "app/repositories/",
        "routes/",
        "database/migrations/",
        "database/seeders/",
        "database/factories/",
        "config/",
    )

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

    def _expand_keywords(self, task_keywords: set[str]) -> set[str]:
        expanded = set(task_keywords)

        for keyword in task_keywords:
            expanded.update(self.KEYWORD_ALIASES.get(keyword, set()))

        return expanded

    def _score_file(
        self,
        file_path: str,
        task_keywords: set[str],
        role: str | None = None,
    ) -> int:
        normalized_path = file_path.lower().replace("\\", "/")
        filename = Path(file_path).name.lower()
        suffix = Path(file_path).suffix.lower()

        expanded_keywords = self._expand_keywords(task_keywords)
        score = 0

        # 1. Kecocokan kata kunci pada nama dan lokasi file.
        for keyword in expanded_keywords:
            if keyword in filename:
                score += 5
            elif keyword in normalized_path:
                score += 3

        is_auth_task = bool(
            task_keywords.intersection({
                "login", "autentikasi", "auth", "authentication",
                "password", "credential", "credentials", "session", "token",
            })
        )

        is_api_task = bool(
            task_keywords.intersection({
                "api", "endpoint", "route", "routing", "rest",
            })
        )

        is_frontend_task = bool(
            task_keywords.intersection({
                "frontend", "front-end", "ui", "ux", "blade", "html",
                "css", "javascript", "js", "jsx", "tsx", "vue",
                "component", "view", "halaman", "page", "tampilan",
            })
        )

        # 2. Konteks autentikasi.
        if is_auth_task:
            if "/auth/" in normalized_path:
                score += 8

            if filename in {"auth.php", "user.php", "session.php"}:
                score += 7

            if "authcontroller" in filename:
                score += 10

            if "/controllers/" in normalized_path:
                score += 3

            if "/middleware/" in normalized_path:
                score += 4

            if "/models/" in normalized_path and "user" in filename:
                score += 7

            if "resources/views/" in normalized_path:
                score += 2

        # 3. Konteks API.
        if is_api_task:
            if "/routes/" in normalized_path:
                score += 8

            if filename == "api.php":
                score += 10

            if filename == "web.php":
                score += 4

            if "/controllers/" in normalized_path:
                score += 5

        # 4. Konteks frontend.
        if is_frontend_task:
            if any(path in normalized_path for path in self.FRONTEND_PATHS):
                score += 5

            if filename.endswith(".blade.php"):
                score += 2

            if suffix in {".html", ".css", ".js", ".jsx", ".ts", ".tsx", ".vue"}:
                score += 2

            if is_auth_task and filename in {
                "welcome.blade.php", "index.blade.php",
            }:
                score -= 5

        # 5. Filter dan prioritas sesuai role agent.
        if role == "frontend":
            if any(path in normalized_path for path in self.FRONTEND_PATHS):
                score += 12
            elif filename.endswith(".blade.php"):
                score += 12
            elif suffix in self.FRONTEND_EXTENSIONS:
                score += 8
            elif any(path in normalized_path for path in self.BACKEND_PATHS):
                score -= 8

            if "/providers/" in normalized_path:
                score -= 10

            if "ai-service/" in normalized_path:
                score -= 5

        elif role == "backend":
            if any(path in normalized_path for path in self.BACKEND_PATHS):
                score += 12
            elif suffix == ".php":
                score += 3

            if any(path in normalized_path for path in self.FRONTEND_PATHS):
                score -= 10
            elif filename.endswith(".blade.php"):
                score -= 10

            if "/providers/" in normalized_path:
                score -= 5

            if "ai-service/" in normalized_path:
                score -= 5

        # 6. Hindari file provider AI jika tidak relevan.
        if "/providers/" in normalized_path and role not in {"frontend", "backend"}:
            score -= 5

        
        
        # Prioritas QA berdasarkan konteks task.
        if role == "qa":
            is_auth_task = bool(
                task_keywords.intersection({
                    "login", "auth", "authentication", "autentikasi",
                    "password", "credential", "credentials",
                    "session", "token", "user", "pengguna",
                    "security", "keamanan",
                })
            )

            is_routing_task = bool(
                task_keywords.intersection({
                    "api", "endpoint", "route", "routes",
                    "routing", "rest",
                })
            )

            # Autentikasi: prioritaskan file yang spesifik.
            if is_auth_task:
                if "/middleware/" in normalized_path:
                    score += 12

                if "/controllers/" in normalized_path:
                    if any(
                        keyword in filename
                        for keyword in ("auth", "login", "logout", "session")
                    ):
                        score += 20
                    else:
                        score += 2

                if "/models/" in normalized_path and filename == "user.php":
                    score += 10

                if "/config/" in normalized_path and filename in {
                    "auth.php", "session.php",
                }:
                    score += 10

            # Routing: prioritaskan file definisi route.
            if is_routing_task:
                if "/routes/" in normalized_path:
                    score += 20

                if filename == "web.php":
                    score += 15

                if filename == "api.php":
                    score += 15

                if "/controllers/" in normalized_path:
                    score += 5

                if "/middleware/" in normalized_path:
                    score += 5

            # Kurangi prioritas aset frontend untuk QA backend.
            if filename.endswith((".css", ".scss", ".sass")):
                score -= 15
            elif "/resources/views/" in normalized_path:
                score -= 5




        return max(score, 0)
    

    
    def _matches_role(self, file_path: str, role: str | None) -> bool:
        if role is None or role == "qa":
            return True

        path = file_path.lower().replace("\\", "/")
        filename = Path(file_path).name.lower()

        is_blade = filename.endswith(".blade.php")

        frontend_paths = (
            "resources/views/",
            "resources/css/",
            "resources/js/",
            "public/css/",
            "public/js/",
        )

        backend_paths = (
            "app/http/controllers/",
            "app/http/middleware/",
            "app/models/",
            "app/services/",
            "app/repositories/",
            "routes/",
            "database/migrations/",
            "database/seeders/",
            "database/factories/",
            "config/",
        )

        frontend_extensions = (
            ".html", ".css", ".js", ".jsx", ".ts",
            ".tsx", ".vue", ".scss", ".sass",
        )

        if role == "frontend":
            # Blade hanya diterima dari folder tampilan.
            if is_blade:
                return "resources/views/" in path

            # Aset frontend harus berada di folder aset yang sesuai.
            if any(folder in path for folder in frontend_paths[1:]):
                return filename.endswith(frontend_extensions)

            # HTML diizinkan hanya jika berada di folder tampilan.
            if filename.endswith(".html"):
                return "resources/views/" in path

            return False

        if role == "backend":
            # File backend harus berada di folder backend yang dikenal.
            if any(folder in path for folder in backend_paths):
                return True

            return False

        return False


    def find(
        self,
        task: str,
        limit: int = 10,
        role: str | None = None,
    ) -> list[dict]:
        if role not in {None, "frontend", "backend", "qa"}:
            raise ValueError(
                "Role harus None, 'frontend', 'backend', atau 'qa'."
            )

        task_keywords = self._task_keywords(task)
        scored_files = []

        for file_path in self.files:
            if not self._matches_role(file_path, role):
                continue

            score = self._score_file(
                file_path,
                task_keywords,
                role,
            )

            if score <= 0:
                continue

            scored_files.append({
                "file": file_path,
                "score": score,
            })

        scored_files.sort(
            key=lambda item: (-item["score"], item["file"])
        )

        return scored_files[:limit]
