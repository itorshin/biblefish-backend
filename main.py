from fastapi import FastAPI
from pydantic import BaseModel
from openai import AsyncOpenAI
import re

client = AsyncOpenAI(
    api_key='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',
)

app = FastAPI()


@app.get("/")
async def root():
    return {"status": 200}


class ParaphraseRequest(BaseModel):
    content: str
    target_tier: int


def load_vocab_list(vocab_file):
    """Load the custom vocabulary list from a file into a set."""
    with open(vocab_file, 'r', encoding='utf-8') as file:
        vocab = {line.strip().lower() for line in file}
    return vocab


def highlight_unknown_words(vocab, text):
    """Highlight words in the text that are not in the vocabulary list."""
    words = re.findall(r'\b\w+\b', text.lower())  # Extract all words

    highlighted_text = []
    for word in words:
        if word not in vocab:
            highlighted_text.append(f'**[word]**')
        else:
            highlighted_text.append(word)

    highlighted_text = ' '.join(highlighted_text)
    return highlighted_text


@app.post("/paraphrase")
async def paraphrase(request: ParaphraseRequest):
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
                
                Understand the provided content above. Retell them with the same meaning but only using Chinese Words from the Chinese HSK {request.target_tier} vocabulary set. You can break one sentence into multiple ones composed of Chinese HSK {request.target_tier} vocabulary. Your output should be in Chinese.
                
                **Your response should only contains the paraphrased text.**
                """,
            }
        ],
        model="gpt-4o-mini",
    )

    vocab = []

    for i in range(1, request.target_tier + 1):
        vocab += load_vocab_list(f"./HSK {i}.txt")

    marked_content = highlight_unknown_words(vocab, chat_completion.choices[0].message)

    print(marked_content)

    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a professional Chinese speaker. Your task is going to simplify Chinese sentences."
            },
            {
                "role": "user",
                "content": f"""
                {marked_content}
                
                Understand the provided content above. Replace the word in **[]** to HSK {request.target_tier} word. You can break one word into multiple ones composed of Chinese HSK {request.target_tier} vocabulary. Your output should be in Chinese.
                
                **Your response should only contains the fixed text.**
                """,
            }
        ],
        model="gpt-4o-mini",
    )

    return chat_completion.choices[0].message