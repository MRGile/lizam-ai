import os

from app.providers.gemini import GeminiProvider
from app.tools.relevant_files import RelevantFileFinder
from app.tools.workspace import Workspace

from .base import BaseAgent


class FrontendAgent(BaseAgent):
    def __init__(self, workspace_path: str | None = None):
        super().__init__(
            name="Frontend Agent",
            role="Menganalisis dan mengembangkan bagian frontend.",
        )

        root_path = workspace_path or os.getenv(
            "WORKSPACE_PATH",
            os.getcwd(),
        )

        self.workspace = Workspace(root_path)
        self.provider = GeminiProvider()

    async def execute(self, task: str) -> dict:
        try:
            files = sorted(self.workspace.list_files())

            finder = RelevantFileFinder(files)

            relevant_files = finder.find(
                task,
                limit=5,
                role="frontend",
            )

            if not relevant_files:
                return {
                    "agent": self.name,
                    "task": task,
                    "status": "failed",
                    "message": "Tidak ditemukan file frontend yang relevan.",
                }

            selected_files = []

            for item in relevant_files:
                file_path = item["file"]

                content = self.workspace.read_file(
                    file_path
                )

                selected_files.append({
                    "file": file_path,
                    "score": item["score"],
                    "content": content,
                })

            context = "\n\n".join(
                [
                    (
                        f"FILE: {item['file']}\n"
                        f"SCORE: {item['score']}\n"
                        f"CONTENT:\n{item['content']}"
                    )
                    for item in selected_files
                ]
            )

            prompt = (
                f"Kamu adalah {self.name} dari LIZAM AI.\n\n"
                "Kamu bertugas menganalisis bagian frontend "
                "dari sebuah project.\n\n"
                f"Task:\n{task}\n\n"
                "Berikut file yang dipilih oleh "
                "Relevant File Finder:\n\n"
                f"{context}\n\n"
                "Analisis file-file tersebut berdasarkan task.\n\n"
                "Berikan:\n"
                "1. File yang paling relevan.\n"
                "2. Masalah yang ditemukan.\n"
                "3. Penyebab yang paling mungkin.\n"
                "4. Perubahan yang diperlukan.\n"
                "5. File yang perlu diubah.\n\n"
                "Jangan mengarang isi file.\n"
                "Jangan mengklaim file sudah diubah.\n"
                "Agent ini hanya melakukan analisis."
            )

            response = await self.provider.generate(prompt)

            return {
                "agent": self.name,
                "task": task,
                "status": "completed",
                "files": [
                    {
                        "file": item["file"],
                        "score": item["score"],
                    }
                    for item in selected_files
                ],
                "message": response,
            }

        except Exception as exc:
            return {
                "agent": self.name,
                "task": task,
                "status": "failed",
                "message": str(exc),
            }