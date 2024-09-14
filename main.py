from fastapi import FastAPI
from pydantic import BaseModel
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key='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',
)


app = FastAPI()


@app.get("/")
async def root():
    return {"status": 200}


class ParaphraseRequest(BaseModel):
    content: str
    target_tire: str

@app.post("/paraphrase")
async def say_hello(request: ParaphraseRequest):
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a professional Chinese speaker. Your task is going to simplify Chinese sentences."
            },
            {
                "role": "user",
                "content": f"""
                {request.content}
                
                Understand the provided content above. Retell them with the same meaning but only using Chinese Words from the Chinese {request.target_tire} vocabulary set. You can break one sentence into multiple ones composed of Chinese {request.target_tire} vocabulary. Your output should be in Chinese.
                
                **Your response should only contains the paraphrased text.**
                """,
            }
        ],
        model="chatgpt-4o-latest",
    )

    return chat_completion.choices[0].message
