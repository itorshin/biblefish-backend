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
            highlighted_text.append(f'**[{word}]**')
        else:
            highlighted_text.append(word)

    highlighted_text = ' '.join(highlighted_text)
    return highlighted_text

def get_hsk_vocabulary(level):
    """Extract vocabulary from HSK files up to the given level."""
    vocabulary = []
    for i in range(1, level + 1):
        try:
            with open(f"HSK {i}.txt", 'r', encoding='utf-8') as file:
                vocabulary.extend([line.strip() for line in file])
        except FileNotFoundError:
            print(f"Warning: HSK {i}.txt not found")
    return vocabulary

@app.post("/paraphrase")
async def paraphrase(request: ParaphraseRequest):
    level = request.target_tier
    hsk_vocabulary = get_hsk_vocabulary(level)
    
    hsk_vocab_str = ", ".join(hsk_vocabulary)

    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a professional Chinese translator. Your task is to simplify Chinese sentences or translate and simplify English sentences into Chinese. You will be given the learner's fluency level in their second language, when you translate the content, keep first language words that user likely would not know in their second language, given their fluency level."
            },
            {
                "role": "user",
                "content": f"""
                fluency level: {request.target_tier}
                Here are the HSK vocabulary list for the fluency level:
                {hsk_vocab_str}

                --- CONTENT START
                {request.content}
                
                --- CONTENT END
                
                Understand the provided content above. Retell them with the same meaning using Chinese Words from the Chinese HSK {request.target_tier} vocabulary set provided above, and maintaining the first language words that users would likley not know in their second language based on their fluency level. You can break one sentence into multiple ones composed of Chinese HSK {request.target_tier} vocabulary and user's first language words. Your output should be in Chinese words that are in the provided dictionary and other words that remain in English.

                The attached dictionary is only a guide - you should consier the Fluency Level of the user and be intelligent about not showing them words in their second language that they don't know. Keep the Chinese characters within their HSK level.
                
                **The response should only contains the paraphrased text.**
                **If the provided content is empty or represent nothing, just response with nothing.**

                DON'T PUT SUPER COMPLICATED WORDS. IF SOMEONE IS HSK3, DON'T SHOW HSK7 WORDS. ALSO KEEP THE GRAMMAR SIMPLE! DO NOT ADD UNNECESSARY COMPLICATED GRAMMARS IN CHINESE.
                """,
            }
        ],
        model="gpt-4o",
    )

    return chat_completion.choices[0].message.content