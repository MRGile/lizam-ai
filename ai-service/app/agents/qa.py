import os

from app.providers.openrouter import OpenRouterProvider
from app.tools.workspace import Workspace

from .base import BaseAgent


class QAAgent(BaseAgent):
    CODE_EXTENSIONS = (
        ".php",
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".vue",
        ".html",
        ".css",
        ".blade.php",
    )

    def __init__(self, workspace_path: str | None = None):
        super().__init__(
            name="QA Agent",
            role="Menguji dan melakukan review terhadap perubahan project.",
        )

        root_path = workspace_path or os.getenv(
            "WORKSPACE_PATH",
            os.getcwd(),
        )

        self.workspace = Workspace(root_path)
        self.provider = OpenRouterProvider()

    async def execute(self, task: str) -> dict:
        try:
            files = sorted(self.workspace.list_files())

            code_files = [
                file
                for file in files
                if file.lower().endswith(self.CODE_EXTENSIONS)
            ]

            if not code_files:
                return {
                    "agent": self.name,
                    "task": task,
                    "status": "failed",
                    "message": "Tidak ditemukan file kode untuk direview.",
                }

            selected_file = code_files[0]
            file_content = self.workspace.read_file(selected_file)

            prompt = (
                f"Kamu adalah {self.name} dari LIZAM AI.\n\n"
                "Tugas utama kamu adalah melakukan QA dan code review.\n\n"
                f"Task:\n{task}\n\n"
                f"File yang sedang direview:\n{selected_file}\n\n"
                f"Isi file:\n{file_content}\n\n"
                "Lakukan pemeriksaan terhadap file tersebut.\n\n"
                "Periksa:\n"
                "1. Bug atau potensi bug.\n"
                "2. Kesalahan logika.\n"
                "3. Risiko keamanan yang terlihat.\n"
                "4. Masalah kompatibilitas atau runtime.\n"
                "5. Potensi regresi.\n"
                "6. Masalah kualitas kode yang berpengaruh terhadap fungsi.\n\n"
                "Berikan hasil dalam format:\n"
                "STATUS: PASS atau FAIL\n"
                "MASALAH:\n"
                "DAFTAR PERBAIKAN:\n"
                "RISIKO:\n\n"
                "Jangan mengklaim telah menjalankan test "
                "jika test tersebut tidak benar-benar dijalankan.\n"
                "Jangan mengarang isi file yang tidak diberikan."
            )

            response = await self.provider.generate(prompt)

            status = "completed"

            if "STATUS: FAIL" in response.upper():
                status = "failed"

            return {
                "agent": self.name,
                "task": task,
                "status": status,
                "file": selected_file,
                "message": response,
            }

        except Exception as exc:
            return {
                "agent": self.name,
                "task": task,
                "status": "failed",
                "message": str(exc),
            }