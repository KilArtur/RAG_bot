import asyncio

from services.LLMService import LLMService

async def main():
    llm = LLMService()
    result = await llm.fetch_completion("Почему небо голубое?")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())