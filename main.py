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
    content: list[str]
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


@app.post("/paraphrase")
async def paraphrase(request: ParaphraseRequest):
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a professional Chinese speaker. Your task is going to simplify Chinese sentences or translate and simplify English sentences into Chinese."
            },
            {
                "role": "user",
                "content": f"""
                {request.content}
                
                Understand the provided content above. Retell them with the same meaning but only using Chinese Words from the Chinese HSK {request.target_tier} vocabulary set. You can break one sentence into multiple ones composed of Chinese HSK {request.target_tier} vocabulary. Your output should be in Chinese.
                
                **Your response should be a plain JSON object with 1 key called 'content'. The value of 'content' should be a list of simplified sentences, corresponding to the input sentences. No code block, no markdown, no HTML tags, no special characters. The order of the output sentences should be the same as the input sentences.**
                """,
            }
        ],
        model="gpt-4o",
    )
    return chat_completion.choices[0].message.content



# "{\"content\": [\"在全球化中，跨文化交际很重要。不但对个人发展有好处，也能帮助国际合作和理解。\", \"人工智能技术发展很快。我们要思考怎样提高生产效率，还要保障人类的就业。\", \"环境保护和经济发展有矛盾。怎样在追求GDP增长同时，实现可持续发展是一个挑战。\", \"在信息爆炸的时代，提高媒体素养和批判性思维能力，辨别虚假信息很重要。\", \"现代社会工作和生活平衡越来越难。怎样在事业和个人幸福之间找到平衡，是许多人的困境。\"]}"