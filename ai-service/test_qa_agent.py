
import asyncio
import json

from app.agents.qa import QAAgent


async def main():
    print("=== TEST QA AGENT ===")

    import os

    project_path = os.path.join(
        os.path.dirname(os.getcwd()),
        "backend",
    )

    agent = QAAgent(workspace_path=project_path)

    print(f"Project yang diperiksa: {project_path}")

    task = (
        "Review keamanan dan potensi bug pada autentikasi "
        "dan routing project Laravel."
    )

    print(f"Task: {task}")
    print("\nMenjalankan QA Agent...\n")

    result = await agent.execute(task)

    print("=== HASIL QA ===")
    print(json.dumps(result, indent=2, ensure_ascii=False))

    print("\n=== RINGKASAN ===")
    print(f"Agent       : {result.get('agent')}")
    print(f"Status      : {result.get('status')}")
    print(f"Verdict     : {result.get('verdict', 'Belum tersedia')}")
    print(f"Tests run   : {result.get('tests_run', False)}")

    if result.get("files"):
        print("\nFile yang direview:")
        for item in result["files"]:
            print(f"- {item['file']} (score: {item['score']})")


if __name__ == "__main__":
    asyncio.run(main())
