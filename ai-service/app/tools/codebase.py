from pathlib import Path


class CodebaseAnalyzer:
    IGNORED_DIRECTORIES = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "vendor",
        "__pycache__",
        ".idea",
        ".vscode",
        "storage",
    }

    SENSITIVE_FILENAMES = {
        ".env",
        ".env.example",
        ".env.local",
        ".env.production",
        ".env.development",
        "credentials.json",
        "secrets.json",
    }

    SENSITIVE_EXTENSIONS = {
        ".key",
        ".pem",
        ".p12",
        ".pfx",
    }

    MAX_FILE_SIZE = 5 * 1024 * 1024

    def __init__(self, root_path: str):
        self.root = Path(root_path).resolve()

    def _is_ignored(self, file_path: Path) -> bool:
        relative_path = file_path.relative_to(self.root)

        return any(
            part in self.IGNORED_DIRECTORIES
            for part in relative_path.parts
        )

    def _is_sensitive(self, file_path: Path) -> bool:
        filename = file_path.name.lower()

        if filename in {
            name.lower()
            for name in self.SENSITIVE_FILENAMES
        }:
            return True

        if file_path.suffix.lower() in self.SENSITIVE_EXTENSIONS:
            return True

        return False

    def analyze(self) -> dict:
        files = []

        for path in self.root.rglob("*"):
            if not path.is_file():
                continue

            if self._is_ignored(path):
                continue

            if self._is_sensitive(path):
                continue

            try:
                if path.stat().st_size > self.MAX_FILE_SIZE:
                    continue
            except OSError:
                continue

            files.append(str(path.relative_to(self.root)))

        files.sort()

        return {
            "root": str(self.root),
            "total_files": len(files),
            "files": files,
        }