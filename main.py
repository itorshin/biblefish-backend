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
    raw: str
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

text_example = {
    1: """
    - 她很高兴。
    - 太好了！
    - 我住在北京。
    - 我会做饭。
    """,
    2: """
    - 你别去游泳了。
    - 他们一起去机场了。
    - 因为下雨，所以他没去踢足球。
    - 学校离我家很近。
    """,
    3: """
    - 这儿的西瓜特别甜。
    - 中国的大城市，我几乎都去过。
    - 请安静，节目马上开始。
    - 这道题其实很容易。
    """,
    4: """
    - 关于这个问题，后面我还会详细说。
    - 把这个字去掉，这个句子就对了。
    - 女儿给我的生活带来很多快乐。
    - 妈妈把刚买的鱼放进了冰箱。
    """,
    5: """
    - 因为马上就要开始上课了，所以快进教室。
    - 他和朋友吵了，所以很不高兴。
    - 我和我妻子有共同的理想和生活目标。
    - 常用的交通工具有汽车、火车、飞机等。
    """,
    6: """
    - 照片要三天才能洗出来。
    - 各位乘客，飞机马上就要起飞了。
    - 妹妹的嘴边有一粒米。
    - 这种植物我们都没见过。
    """,
}


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
                
                                
                --- HSK {request.target_tier} EXAMPLE SENTENCE:
                
                {text_example[request.target_tier]}
                
                Understand the provided content above. Retell them with the same meaning using Chinese Words from the Chinese HSK {request.target_tier} vocabulary set provided above, and maintaining the first language words that users would likley not know in their second language based on their fluency level. You can break one sentence into multiple ones composed of Chinese HSK {request.target_tier} vocabulary and user's first language words. Your output should be in Chinese words that are in the provided dictionary and other words that remain in English.

                The attached dictionary is only a guide - you should consier the Fluency Level of the user and be intelligent about not showing them words in their second language that they don't know. Keep the Chinese characters within their HSK level.
                
                **The response should only contains the paraphrased text.**
                **If the provided content is empty or represent nothing, just response with nothing.**
                **The response should not contains the indicator like "--- CONTENT START".**

                DON'T PUT SUPER COMPLICATED WORDS. IF SOMEONE IS HSK3, DON'T SHOW HSK7 WORDS. ALSO KEEP THE GRAMMAR SIMPLE! DO NOT ADD UNNECESSARY COMPLICATED GRAMMARS IN CHINESE.
                """,
            }
        ],
        model="gpt-4o",
    )

    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a professional Chinese speaker. Your task is going to simplify Chinese sentences or translate and simplify English sentences into Chinese."
            },
            {
                "role": "user",
                "content": f"""
                    --- CONTENT START
                    
                    {request.content}
                    
                    --- CONTENT END
                    
                    --- RAW START
                    
                    {chat_completion.choices[0].message.content}
                    
                    --- RAW END

                    The CONTENT provided above has the same meaning of the RAW provided above. The RAW has some html tags like link or bold. You need to add all the html tags in the RAW to the CONTENT. You should keep the same attributes like href.
                    
                    --- TAKE THE FOLLOWING EXAMPLE:
                    
                    - CONTENT: Valve 是一家美国公司。
                    - RAW: Valve是一间<a href='some url'>美国电子游戏开发商及发行商</a>。
                    - RESPONSE: Valve 是一家<a href='some url'>美国公司</a>。
                    
                    - CONTENT: Valve 是一家美国公司。
                    - RAW: Valve是一间<a href='some url'><span>美国电子游戏开发商及发行商</span></a>。
                    - RESPONSE: Valve 是一家<a href='some url'><span>美国公司</span></a>。
                    
                    - CONTENT: Valve 是一家美国公司。
                    - RAW: Valve的第一款作品是<em>第一人称射击游戏《半衰期》</em>。
                    - RESPONSE: Valve的第一个作品是<em>《半衰期》</em>。

                    **The response should only contains the styled text.**
                    **If the provided content is empty or represent nothing, just response with nothing (nothing is literally nothing).**
                    **The response should not contains the indicator like "--- CONTENT START".**
                    """,
            }
        ],
        model="chatgpt-4o-latest",
        temperature=0.4
    )

    return chat_completion.choices[0].message.content

    return chat_completion.choices[0].message.content