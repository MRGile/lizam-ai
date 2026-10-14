import subprocess
from pathlib import Path


class LaravelTestRunner:
    """Menjalankan tes Laravel dengan perintah yang dibatasi."""

    TIMEOUT_SECONDS = 120
    MAX_OUTPUT_CHARS = 12000

    def __init__(self, backend_path: str):
        self.backend = Path(backend_path).resolve()

        if not self.backend.is_dir():
            raise ValueError("Folder backend tidak ditemukan.")

        if not (self.backend / "artisan").is_file():
            raise ValueError(
                "File artisan tidak ditemukan. "
                "Pastikan path mengarah ke project Laravel."
            )

        if not (self.backend / "vendor" / "autoload.php").is_file():
            raise ValueError(
                "Dependensi Laravel belum terpasang. "
                "Jalankan composer install terlebih dahulu."
            )

    def run(self) -> dict:
        command = ["php", "artisan", "test"]

        try:
            result = subprocess.run(
                command,
                cwd=str(self.backend),
                capture_output=True,
                text=True,
                timeout=self.TIMEOUT_SECONDS,
                shell=False,
                check=False,
            )

            output = "\n".join(
                part
                for part in (result.stdout, result.stderr)
                if part
            )

            if result.returncode == 0:
                status = "passed"
            else:
                status = "failed"

            return {
                "status": status,
                "tests_run": True,
                "exit_code": result.returncode,
                "output": output[-self.MAX_OUTPUT_CHARS:],
            }

        except subprocess.TimeoutExpired as exc:
            output = ""

            for part in (exc.stdout, exc.stderr):
                if part:
                    if isinstance(part, bytes):
                        part = part.decode("utf-8", errors="replace")
                    output += part + "\n"

            return {
                "status": "timeout",
                "tests_run": True,
                "exit_code": None,
                "output": output[-self.MAX_OUTPUT_CHARS:],
            }

        except OSError as exc:
            return {
                "status": "error",
                "tests_run": False,
                "exit_code": None,
                "output": str(exc),
            }