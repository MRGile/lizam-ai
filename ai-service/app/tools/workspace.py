from pathlib import Path


class Workspace:
    IGNORED_DIRECTORIES = {
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "vendor",
        "__pycache__",
        ".idea",
        ".vscode",
    }

    SENSITIVE_FILENAMES = {
        ".env",
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

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

    def __init__(self, root_path: str):
        self.root = Path(root_path).resolve()

    def _resolve_safe_path(self, relative_path: str) -> Path:
        file_path = (self.root / relative_path).resolve()

        if self.root != file_path and self.root not in file_path.parents:
            raise ValueError(
                "Akses file di luar workspace tidak diizinkan."
            )

        return file_path

    def _is_sensitive(self, file_path: Path) -> bool:
        if file_path.name.lower() in {
            name.lower()
            for name in self.SENSITIVE_FILENAMES
        }:
            return True

        if file_path.suffix.lower() in self.SENSITIVE_EXTENSIONS:
            return True

        return False

    def _is_ignored(self, file_path: Path) -> bool:
        relative_path = file_path.relative_to(self.root)

        return any(
            part in self.IGNORED_DIRECTORIES
            for part in relative_path.parts
        )

    def list_files(self) -> list[str]:
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

        return files

    def read_file(self, relative_path: str) -> str:
        file_path = self._resolve_safe_path(relative_path)

        if not file_path.is_file():
            raise FileNotFoundError(
                f"File tidak ditemukan: {relative_path}"
            )

        if self._is_ignored(file_path):
            raise PermissionError(
                "File berada di direktori yang diabaikan."
            )

        if self._is_sensitive(file_path):
            raise PermissionError(
                "Akses ke file sensitif tidak diizinkan."
            )

        if file_path.stat().st_size > self.MAX_FILE_SIZE:
            raise ValueError(
                "Ukuran file melebihi batas 5 MB."
            )

        try:
            return file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(
                "File bukan file teks UTF-8 yang dapat dibaca."
            ) from exc