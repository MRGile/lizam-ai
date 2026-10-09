import asyncio

from app.agents.backend import BackendAgent


async def main():
    agent = BackendAgent(
        r"C:\Users\Lizam\lizam-ai"
    )

    result = await agent.execute(
        "Perbaiki halaman login dan API autentikasi"
    )

    print(result)


asyncio.run(main())