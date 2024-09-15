from fastapi import FastAPI
from pydantic import BaseModel
from openai import AsyncOpenAI
import re
import jieba

client = AsyncOpenAI(
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

<<<<<<< Updated upstream
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
=======
def highlight_unknown_words(hsk_vocab, custom_vocab, text):
    """Highlight words in the text that are not in the vocabulary list using jieba for tokenization."""
    words = jieba.cut(text)  # Use jieba to tokenize the Chinese text
    highlighted_text = []
    for word in words:
        if word.strip():  # Ignore empty strings
            if not any(char.isalpha() for char in word):  # If the word contains no alphabetic characters
                highlighted_text.append(word)  # Keep punctuation and numbers as is
            elif word.lower() not in hsk_vocab and word.lower() not in custom_vocab:
                highlighted_text.append(f"**[{word}]**")
            else:
                highlighted_text.append(word)
    return "".join(highlighted_text)  # Join without spaces for Chinese text
>>>>>>> Stashed changes

def get_hsk_vocabulary(level):
    """Extract vocabulary from HSK files up to the given level."""
    vocabulary = set()
    for i in range(1, level + 1):
        try:
<<<<<<< Updated upstream
            with open(f"HSK {i}.txt", 'r', encoding='utf-8') as file:
                vocabulary.extend([line.strip() for line in file])
=======
            with open(f"HSK {i}.txt", "r", encoding="utf-8") as file:
                vocabulary.update(line.strip().lower() for line in file)
>>>>>>> Stashed changes
        except FileNotFoundError:
            print(f"Warning: HSK {i}.txt not found")
    return vocabulary

<<<<<<< Updated upstream
@app.post("/paraphrase")
async def paraphrase(request: ParaphraseRequest):
    level = request.target_tier
    hsk_vocabulary = get_hsk_vocabulary(level)
    
    hsk_vocab_str = ", ".join(hsk_vocabulary)
=======
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


user_custom_dict = set()

@app.post("/paraphrase")
async def paraphrase(request: ParaphraseRequest):
    level = request.target_tier
>>>>>>> Stashed changes

    # First pass: Translate and simplify
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
<<<<<<< Updated upstream
                "content": "You are a professional Chinese translator. Your task is to simplify Chinese sentences or translate and simplify English sentences into Chinese. You will be given the learner's fluency level in their second language, when you translate the content, keep first language words that user likely would not know in their second language, given their fluency level."
=======
                "content": f"""You are a professional Chinese translator. Your task is to simplify Chinese sentences or translate and simplify English sentences into Chinese. You will be given the learner's fluency level in their second language. When you translate the content, keep first language words that the user likely would not know in their second language, given their fluency level.

                Here is an example of an English Sentence in different language fluency levels. 
                Original English text: The study of abiogenesis aims to determine how pre-life chemical reactions gave rise to life under conditions strikingly different from those on Earth today. 
                HSK level adjusted output: 
                
                HSK6: 生命来源的研究学习在与现在的地球环境不同的条件下，非生命的化学反应如何生成了生命。

                HSK5: 生命 originate 的研究想要知道，在和现在不同的地球条件下，非生命的化学反应是怎么变成生命的。

                HSK4: The study of 研究生命如何开始，想了解在不同环境下，化学反应是怎么产生生命的。

                HSK3: Scientists学习生命是怎么开始的，他们想知道在不同条件下，化学reaction如何变成生命。

                HSK2: 人们想知道life是怎么来的，他们想知道chemistry reaction 怎样变成life。

                HSK1: 人想知道life是怎么来的。
                """,
>>>>>>> Stashed changes
            },
            {
                "role": "user",
                "content": f"""
                fluency level: {request.target_tier}
                
                --- CONTENT START
                {request.content}
                
                --- CONTENT END
                
<<<<<<< Updated upstream
                Understand the provided content above. Retell them with the same meaning using Chinese Words from the Chinese HSK {request.target_tier} vocabulary set provided above, and maintaining the first language words that users would likley not know in their second language based on their fluency level. You can break one sentence into multiple ones composed of Chinese HSK {request.target_tier} vocabulary and user's first language words. Your output should be in Chinese words that are in the provided dictionary and other words that remain in English.
=======
                --- HSK {request.target_tier} EXAMPLE SENTENCE:
                
                {text_example[request.target_tier]}
                
                Translate and simplify the provided content above. Retell it with the same meaning using Chinese words appropriate for HSK {request.target_tier} level, and maintain the first language words that users would likely not know in their second language based on their fluency level. You can break one sentence into multiple ones. Your output should be in Chinese words appropriate for the user's level and other words that remain in the user's first language.
>>>>>>> Stashed changes

                Consider the Fluency Level of the user and be intelligent about not showing them words in their second language that they don't know. Keep the Chinese characters within their HSK level.
                
<<<<<<< Updated upstream
                **The response should only contains the paraphrased text.**
                **If the provided content is empty or represent nothing, just response with nothing.**
=======
                **The response should only contain the translated and simplified text.**
                **If the provided content is empty or represents nothing, just respond with nothing.**
                **The response should not contain indicators like "--- CONTENT START".**
>>>>>>> Stashed changes

                KEEP THE GRAMMAR SIMPLE! DO NOT ADD UNNECESSARY COMPLICATED GRAMMARS IN CHINESE.
                """,
            }
        ],
        model="gpt-4o",
    )

<<<<<<< Updated upstream
    return chat_completion.choices[0].message.content
=======
    # Process the first pass result
    first_pass_result = chat_completion.choices[0].message.content
    print(first_pass_result)

    # Highlight unknown words
    hsk_vocab = get_hsk_vocabulary(request.target_tier)
    marked_content = highlight_unknown_words(hsk_vocab, user_custom_dict, first_pass_result)
    print(marked_content)

    # Second pass: Further simplification
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a professional Chinese language simplifier. Your task is to further simplify Chinese sentences that contain highlighted words beyond the user's language level.",
            },
            {
                "role": "user",
                "content": f"""
                fluency level: {request.target_tier}
                
                --- CONTENT START
                
                {marked_content}
                
                --- CONTENT END
                
                The content above contains highlighted words (enclosed in **[...]**) that are beyond the user's HSK {request.target_tier} level. Please simplify the text further, replacing these highlighted words with simpler expressions or explanations that match the user's HSK {request.target_tier} level. Maintain the overall meaning of the text while making it more accessible to the user's current language ability. However, please make sure that the English words in the sentence do stay because they were left there on purpose.

                **The response should only contain the further simplified text.**
                **If the provided content is empty or represents nothing, just respond with nothing.**
                **The response should not contain indicators like "--- CONTENT START".**

                KEEP THE GRAMMAR SIMPLE! DO NOT ADD UNNECESSARY COMPLICATED GRAMMARS IN CHINESE.
                """,
            },
        ],
        model="gpt-4o",
    )

    simplified_content = chat_completion.choices[0].message.content
    print(simplified_content)

    # Final pass: Add HTML tags
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a professional HTML tagger. Your task is to add HTML tags from the original raw content to the simplified content, maintaining the structure and attributes of the tags.",
            },
            {
                "role": "user",
                "content": f"""
                    --- CONTENT START

                    {simplified_content}

                    --- CONTENT END
                    
                    --- RAW START
                    
                    {request.raw}

                    --- RAW END

                    The CONTENT provided above has the same meaning as the RAW provided above, but simplified. The RAW has some HTML tags like links or bold. You need to add all the HTML tags from the RAW to the CONTENT. You should keep the same attributes like href.
                    
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

                    **The response should only contain the styled text.**
                    **If the provided content is empty or represents nothing, just respond with nothing (literally nothing).**
                    **The response should not contain indicators like "--- CONTENT START".**
                    """,
            },
        ],
        model="chatgpt-4o-latest",
        temperature=0.4,
    )

    return chat_completion.choices[0].message.content

class FileContentRequest(BaseModel):
    content: str

@app.post("/process_file")
async def process_file(request: FileContentRequest):
    global user_custom_dict
    user_custom_dict = set(word.strip().lower() for word in request.content.split('\n') if word.strip())
    return {"message": "File content received and stored in user_custom_dict"}
>>>>>>> Stashed changes
