import asyncio

from app.agents.frontend import FrontendAgent


async def main():
    agent = FrontendAgent(
        r"C:\Users\Lizam\lizam-ai"
    )

    result = await agent.execute(
        "Perbaiki halaman login dan API autentikasi"
    )

    print(result)


asyncio.run(main())