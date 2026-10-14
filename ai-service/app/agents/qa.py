import os
import re
from pathlib import Path

from app.tools.test_runner import LaravelTestRunner
from app.providers.openrouter import OpenRouterProvider
from app.tools.relevant_files import RelevantFileFinder
from app.tools.workspace import Workspace

from .base import BaseAgent


class QAAgent(BaseAgent):
    CODE_EXTENSIONS = (
        ".php", ".py", ".js", ".jsx", ".ts",
        ".tsx", ".vue", ".html", ".css", ".blade.php",
    )

    MAX_REVIEW_FILES = 8

    def __init__(self, workspace_path: str | None = None):
        super().__init__(
            name="QA Agent",
            role="Menguji dan melakukan review terhadap perubahan project.",
        )

        root_path = workspace_path or os.getenv(
            "WORKSPACE_PATH",
            os.getcwd(),
        )

        self.root_path = Path(root_path).resolve()
        self.workspace = Workspace(str(self.root_path))
        self.provider = OpenRouterProvider()

    @staticmethod
    def _normalize(path: str) -> str:
        return path.lower().replace("\\", "/").strip("/")

    
    @staticmethod
    def _calculate_route_coverage(
        route_files_available: list[str],
        normalized_selected: set[str],
        routing_task: bool,
    ) -> dict:
        available = sorted({
            QAAgent._normalize(path)
            for path in route_files_available
        })

        reviewed = sorted(
            set(available) & normalized_selected
        )

        missing = sorted(
            set(available) - set(reviewed)
        )

        # Task routing tidak dianggap lengkap jika tidak ada
        # file route yang tersedia atau ada file yang terlewat.
        incomplete = routing_task and (
            not available or bool(missing)
        )

        return {
            "route_files_reviewed": reviewed,
            "route_files_missing": missing,
            "routing_review_incomplete": incomplete,
        }


    @staticmethod
    def _is_auth_task(task: str) -> bool:
        keywords = (
            "auth", "authentication", "autentikasi",
            "login", "logout", "password", "session",
            "token", "credential", "keamanan",
            "security", "middleware",
        )
        task_lower = task.lower()
        return any(keyword in task_lower for keyword in keywords)

    @staticmethod
    def _is_routing_task(task: str) -> bool:
        keywords = (
            "routing", "route", "routes",
            "routing", "endpoint", "api",
        )
        task_lower = task.lower()
        return any(keyword in task_lower for keyword in keywords)

    def _file_priority(
        self,
        file_path: str,
        auth_task: bool,
        routing_task: bool,
    ) -> int:
        path = self._normalize(file_path)
        name = Path(path).name

        score = 0

        # Routing harus diperiksa untuk task yang membahas routing.
        if routing_task and (
            path.startswith("routes/")
            or "/routes/" in path
        ):
            score += 100

        # Prioritaskan middleware dan controller terkait autentikasi.
        if auth_task:
            if "middleware" in path:
                score += 45

            if (
                "auth" in name
                or "login" in name
                or "logout" in name
            ) and "controller" in path:
                score += 60

            if "/models/user.php" in f"/{path}":
                score += 40

            if path.startswith("config/") and name in {
                "auth.php",
                "session.php",
            }:
                score += 35

            if "/controllers/" in path:
                score += 15

        # Aset tampilan bukan prioritas review backend.
        if name.endswith((".css", ".scss", ".sass")):
            score -= 30
        elif path.startswith(("resources/js/", "public/js/")):
            score -= 20
        elif path.startswith("resources/views/"):
            score -= 10

        return score

    async def execute(self, task: str) -> dict:
        try:
            files = sorted(self.workspace.list_files())

            code_files = [
                file_path
                for file_path in files
                if file_path.lower().endswith(self.CODE_EXTENSIONS)
            ]

            if not code_files:
                return {
                    "agent": self.name,
                    "task": task,
                    "status": "failed",
                    "verdict": "REVIEW",
                    "tests_run": False,
                    "message": "Tidak ditemukan file kode untuk direview.",
                }

            auth_task = self._is_auth_task(task)
            routing_task = self._is_routing_task(task)

            finder = RelevantFileFinder(code_files)
            ranked_files = finder.find(
                task,
                limit=len(code_files),
                role="qa",
            )

            score_map = {
                self._normalize(item["file"]): item["score"]
                for item in ranked_files
            }

            # Gabungkan hasil pencarian relevansi dengan file penting
            # yang ditentukan berdasarkan konteks task.
            candidates = set()

            for item in ranked_files:
                candidates.add(item["file"])

            if auth_task or routing_task:
                for file_path in code_files:
                    path = self._normalize(file_path)
                    name = Path(path).name

                    is_route = (
                        path.startswith("routes/")
                        or "/routes/" in path
                    )

                    is_auth_config = (
                        path.startswith("config/")
                        and name in {"auth.php", "session.php"}
                    )

                    is_user_model = (
                        path.endswith("/models/user.php")
                    )

                    is_middleware = "/middleware/" in path

                    is_auth_controller = (
                        "/controllers/" in path
                        and (
                            "auth" in name
                            or "login" in name
                            or "logout" in name
                        )
                    )

                    if (
                        (routing_task and is_route)
                        or (
                            auth_task
                            and (
                                is_auth_config
                                or is_user_model
                                or is_middleware
                                or is_auth_controller
                            )
                        )
                    ):
                        candidates.add(file_path)

            selected = sorted(
                candidates,
                key=lambda file_path: (
                    -self._file_priority(
                        file_path,
                        auth_task,
                        routing_task,
                    ),
                    -score_map.get(self._normalize(file_path), 0),
                    file_path,
                ),
            )[:self.MAX_REVIEW_FILES]

            selected_files = []

            for file_path in selected:
                content = self.workspace.read_file(file_path)

                selected_files.append({
                    "file": file_path,
                    "score": score_map.get(
                        self._normalize(file_path), 0
                    ),
                    "content": content,
                })

            
            normalized_selected = {
                self._normalize(item["file"])
                for item in selected_files
            }

            route_files_available = [
                file_path for file_path in code_files
                if (
                    self._normalize(file_path).startswith("routes/")
                    or "/routes/" in self._normalize(file_path)
                )
            ]

            coverage = self._calculate_route_coverage(
                route_files_available,
                normalized_selected,
                routing_task,
            )

            route_files_selected = coverage["route_files_reviewed"]
            missing_route_files = coverage["route_files_missing"]
            missing_route_review = coverage["routing_review_incomplete"]



            context = "\n\n".join(
                f"FILE: {item['file']}\n"
                f"CONTENT:\n{item['content']}"
                for item in selected_files
            )

            prompt = (
                f"Kamu adalah {self.name} dari LIZAM AI.\n\n"
                "Lakukan code review hanya berdasarkan kode yang diberikan.\n"
                "Jangan mengarang file, konfigurasi, atau hasil pengujian.\n"
                "Bedakan masalah yang terbukti, potensi masalah, "
                "dan rekomendasi opsional.\n"
                "Jangan menyebut konfigurasi default sebagai celah "
                "keamanan tanpa bukti dan konteks yang cukup.\n"
                "Jangan menganggap fitur yang tidak diperlukan sebagai bug.\n\n"
                f"TASK:\n{task}\n\n"
                f"FILE YANG DIREVIEW:\n{context}\n\n"
                "Periksa bug, keamanan, logika, runtime, dan regresi.\n\n"
                "Gunakan format:\n"
                "STATUS: PASS, FAIL, atau REVIEW\n"
                "MASALAH:\n"
                "DAFTAR PERBAIKAN:\n"
                "RISIKO:\n"
                "BATASAN PEMERIKSAAN:\n\n"
                "FAIL: ada masalah penting yang didukung bukti kode.\n"
                "REVIEW: bukti tidak cukup untuk menyimpulkan PASS atau FAIL.\n"
                "PASS: file yang diberikan sudah diperiksa dan tidak "
                "ditemukan masalah penting dalam cakupan pemeriksaan.\n"
                "PASS bukan bukti bahwa seluruh aplikasi aman atau "
                "lulus tes otomatis.\n"
                "Jangan mengaku menjalankan tes otomatis."
            )

            response = await self.provider.generate(prompt)

            match = re.search(
                r"^\s*STATUS\s*:\s*(PASS|FAIL|REVIEW)\b",
                response,
                re.IGNORECASE | re.MULTILINE,
            )

            verdict = match.group(1).upper() if match else "REVIEW"

            # Jangan izinkan PASS jika file routing yang tersedia
            # tidak ikut diperiksa dalam task routing.
            if missing_route_review:
                verdict = "REVIEW"

            
            # Jalankan tes otomatis hanya jika workspace adalah
            # proyek Laravel dengan dependensi yang tersedia.
            test_result = {
                "status": "skipped",
                "tests_run": False,
                "exit_code": None,
                "output": "Workspace bukan proyek Laravel.",
            }

            if (self.root_path / "artisan").is_file():
                try:
                    runner = LaravelTestRunner(str(self.root_path))
                    test_result = runner.run()
                
                except (ValueError, OSError) as exc:
                    test_result = {
                        "status": "error",
                        "tests_run": False,
                        "exit_code": None,
                        "output": str(exc),
                    }


            # Tes gagal berarti QA tidak boleh memberikan PASS.
            if test_result["status"] == "failed":
                verdict = "FAIL"
            elif test_result["status"] in {"timeout", "error"}:
                if verdict != "FAIL":
                    verdict = "REVIEW"


            return {
                "agent": self.name,
                "task": task,
                "status": "completed",
                "verdict": verdict,
                "tests_run": test_result["tests_run"],
                "test_result": test_result,
                "files": [
                    {
                        "file": item["file"],
                        "score": item["score"],
                    }
                    for item in selected_files
                ],
                "message": response,
                
                
                "coverage": {
                    "routing_task": routing_task,
                    "auth_task": auth_task,
                    "route_files_available": route_files_available,
                    "route_files_reviewed": route_files_selected,
                    "route_files_missing": missing_route_files,
                    "routing_review_incomplete": missing_route_review,
                },


                "note": (
                    "Hasil review AI dan tes otomatis tersedia."
                    if test_result["tests_run"]
                    else "Tes otomatis belum berhasil dijalankan."
                ),
            }

        except Exception as exc:
            return {
                "agent": self.name,
                "task": task,
                "status": "failed",
                "verdict": "REVIEW",
                "tests_run": False,
                "message": str(exc),
            }
