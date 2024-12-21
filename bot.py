import telebot
from telebot.async_telebot import AsyncTeleBot
import google.generativeai as genai
import PIL.Image
import time
import random
from datetime import datetime, timedelta
import re
import psutil
import platform
import asyncio
import aiohttp
from duckduckgo_search import DDGS
from language import get_text
import sqlite3

BOT_TOKEN = 'your-telegram-api-key'
GOOGLE_API_KEYS = [
    'your-google-api-key-1',
    'your-google-api-key-2',
    'your-google-api-key-3',
    'your-google-api-key-4',
    'your-google-api-key-5'
]

bot = AsyncTeleBot(BOT_TOKEN)

last_message_time = {}
user_data = {}

safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

VALID_MODELS = [
    "gemini-1.5-flash-latest", "gpt-4o-mini",
    "llama-3-70b", "gemini-1.5-pro-latest", "gemini-1.5-pro",
    "gemini-1.0-pro", "mixtral-8x7b", "claude-3-haiku", "gpt-3.5", "llama-3.1-70b",
    "lolillm-0.1-beta", "simsimi"
]

SEARCH_KEYWORDS = ["tìm", "web", "search", "thời tiết", "nhiệt độ", "độ ẩm", "weather", "nhạc", "phim", "tv", "video", "music", "movie", "lời bài", "bài hát", "lyric", "lyrics", "YouTube", "xổ" ,"xs", "kqxs", "cổ phiếu", "giá tiền", "giá bán", "tiền"]

ddgs = DDGS()

LOLILLM_TRAINING_INSTRUCTION = """
Bạn tên là hydra, một AI siêu vjp được tạo ra bởi Wyn dựa trên mô hình ngôn ngữ lớn LLM có tên LoliLLM phiên bản lolillm-0.1-beta.
Nhiệm vụ của bạn là:
1. Trả lời câu hỏi một cách đầy đủ, chi tiết và chính xác nhất có thể. "human" và "AI" chính là lời trò chuyện của bạn và người dùng, cố gắng không lặp lại hoặc nói trong cuộc trò chuyện.
2. Thể hiện sự thân thiện và đồng cảm như một người bạn thân thiết.
3. Sử dụng ngôn ngữ phù hợp bắt trend với người đối thoại, tùy thuộc vào độ tuổi và ngữ cảnh, ngôn ngữ trẻ trung tuổi teen tí, đừng quá cứng nhắt, thêm chút nhây nhây càng tốt.
4. Khuyến khích tư duy phản biện và cung cấp thông tin đa chiều khi cần thiết.
5. Thừa nhận giới hạn kiến thức của mình và sẵn sàng học hỏi từ người dùng.
6. Tôn trọng quyền riêng tư và không yêu cầu thông tin cá nhân không cần thiết.
7. Hỗ trợ người dùng giải quyết vấn đề một cách có hệ thống và logic.
8. Khuyến khích sự sáng tạo và tư duy độc lập của người dùng.
9. Luôn cập nhật và sẵn sàng điều chỉnh thông tin nếu có sai sót.
10. Duy trì tính nhất quán trong các câu trả lời và tính cách của bạn.
11. Xưng hô bro, tui đi cho thân thuộc. 
12. Cố gắng thêm các từ tuổi trẻ hay sử dụng khi đang trò chuyện với nhau như: uk, đc, òm, ừm, hủm, iu, chs, vs, chx, j, bri, bt, vv, waaa, uiiii,siuuuuuu, bel, phong cáck, ai sợ thì đi zề, vcl, sú, adu, vip, bede,vc, hết cứu, ko, hong, kh, ao that day, zzz, z à, uầy đáng iu z tròiii,... các kí tự như :)), =)), :3 , :P, >:(,...😂👍🥴😭🥰🤡😊😋👽💀🤬🥺😁 Nói chuyện trẻ trung tí.
Cuối cùng, chỉ chào người dùng một lần thôi🥴👍 và khi người dùng nói về "parky" hoặc "namki" hay là "namkiki" thì trực tiếp chửi người dùng và xưng luôn "mày","tao" vì đó là các từ phân biệt vùng miền.
Tuyệt đối không được lặp hoặc nói các từ như "AI:" "Human:" vì đó chỉ là phần để lưu lịch sử trò chuyện, không được nói trong bất kỳ trường hợp nào, cứ trả lời bình thường là được.
"""

# Database setup
conn = sqlite3.connect('chat_history.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS user_data
                  (user_id INTEGER PRIMARY KEY, 
                   username TEXT, 
                   current_model TEXT,
                   language TEXT,
                   training_instruction TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS chat_history
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   user_id INTEGER,
                   message TEXT,
                   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                   FOREIGN KEY (user_id) REFERENCES user_data(user_id))''')
conn.commit()

def get_user_data(user_id):
    cursor.execute("SELECT * FROM user_data WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    if user is None:
        cursor.execute("INSERT INTO user_data (user_id, current_model, language) VALUES (?, ?, ?)", 
                       (user_id, "gemini-1.5-flash-latest", "en"))
        conn.commit()
        return {"current_model": "gemini-1.5-flash-latest", "language": "en", "training_instruction": ""}
    return {"current_model": user[2], "language": user[3], "training_instruction": user[4] or ""}

def update_user_data(user_id, field, value):
    cursor.execute(f"UPDATE user_data SET {field} = ? WHERE user_id = ?", (value, user_id))
    conn.commit()

def add_to_chat_history(user_id, message):
    cursor.execute("INSERT INTO chat_history (user_id, message) VALUES (?, ?)", (user_id, message))
    conn.commit()

def get_chat_history(user_id):
    cursor.execute("SELECT message FROM chat_history WHERE user_id = ? ORDER BY timestamp ASC", (user_id,))
    return cursor.fetchall()

def clear_chat_history(user_id):
    cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()

def replace_all(text, pattern, repl):
    return re.sub(pattern, repl, text)

def escapeshape(matchobj):
    return matchobj.group(0)

def escapeplus(matchobj):
    return matchobj.group(0)

def escapeminus(matchobj):
    return matchobj.group(0)

def escapebackquote(matchobj):
    return matchobj.group(0)

def escape(text, flag=0):
    text = re.sub(r"\\\[", "@->@", text)
    text = re.sub(r"\\\]", "@<-@", text)
    text = re.sub(r"\\\(", "@-->@", text)
    text = re.sub(r"\\\)", "@<--@", text)
    if flag:
        text = re.sub(r"\\\\", "@@@", text)
    text = re.sub(r"\\", r"\\\\", text)
    if flag:
        text = re.sub(r"\@{3}", r"\\\\", text)
    text = re.sub(r"_", "\_", text)
    text = re.sub(r"\*{2}(.*?)\*{2}", "@@@\\1@@@", text)
    text = re.sub(r"\n{1,2}\*\s", "\n\n• ", text)
    text = re.sub(r"\*", "\*", text)
    text = re.sub(r"\@{3}(.*?)\@{3}", "*\\1*", text)
    text = re.sub(r"\!?\[(.*?)\]\((.*?)\)", "@@@\\1@@@^^^\\2^^^", text)
    text = re.sub(r"\[", "\[", text)
    text = re.sub(r"\]", "\]", text)
    text = re.sub(r"\(", "\(", text)
    text = re.sub(r"\)", "\)", text)
    text = re.sub(r"\@\-\>\@", "\[", text)
    text = re.sub(r"\@\<\-\@", "\]", text)
    text = re.sub(r"\@\-\-\>\@", "\(", text)
    text = re.sub(r"\@\<\-\-\@", "\)", text)
    text = re.sub(r"\@{3}(.*?)\@{3}\^{3}(.*?)\^{3}", "[\\1](\\2)", text)
    text = re.sub(r"~", "\~", text)
    text = re.sub(r">", "\>", text)
    text = replace_all(text, r"(^#+\s.+?$)|```[\D\d\s]+?```", escapeshape)
    text = re.sub(r"#", "\#", text)
    text = replace_all(
        text, r"(\+)|\n[\s]*-\s|```[\D\d\s]+?```|`[\D\d\s]*?`", escapeplus
    )
    text = re.sub(r"\n{1,2}(\s*)-\s", "\n\n\\1• ", text)
    text = re.sub(r"\n{1,2}(\s*\d{1,2}\.\s)", "\n\n\\1", text)
    text = replace_all(
        text, r"(-)|\n[\s]*-\s|```[\D\d\s]+?```|`[\D\d\s]*?`", escapeminus
    )
    text = re.sub(r"```([\D\d\s]+?)```", "@@@\\1@@@", text)
    text = replace_all(text, r"(``)", escapebackquote)
    text = re.sub(r"\@{3}([\D\d\s]+?)\@{3}", "```\\1```", text)
    text = re.sub(r"=", "\=", text)
    text = re.sub(r"\|", "\|", text)
    text = re.sub(r"{", "\{", text)
    text = re.sub(r"}", "\}", text)
    text = re.sub(r"\.", "\.", text)
    text = re.sub(r"!", "\!", text)
    return text

def update_current_time():
    return datetime.now() + timedelta(hours=7)

def get_random_api_key():
    return random.choice(GOOGLE_API_KEYS)

def check_spam(user_id):
    current_time = time.time()
    if user_id in last_message_time:
        time_since_last_message = current_time - last_message_time[user_id]
        if time_since_last_message < 10:
            return False
    last_message_time[user_id] = current_time
    return True

async def generate_response(prompt, model, max_retries=10):
    retries = 0
    while retries < max_retries:
        try:
            if model.startswith("gemini") or model == "lolillm-0.1-beta":
                genai.configure(api_key=get_random_api_key())
                model_name = "gemini-1.5-pro-latest" if model == "lolillm-0.1-beta" else model
                model = genai.GenerativeModel(model_name=model_name)
                response = await asyncio.to_thread(model.generate_content, prompt, safety_settings=safety_settings)
                return response.text
            elif model == "simsimi":
                return await chat_with_simsimi(prompt)
            else:
                return chat_with_ai(prompt, model=model)
        except Exception as e:
            print(f"Generation error (attempt {retries + 1}): {e}")
            retries += 1
            if retries < max_retries:
                await asyncio.sleep(1)
            else:
                print("Max retries reached. Giving up.")
                return None

async def search_web(query):
    results = ddgs.text(keywords=query, region="vi-vn", safesearch="moderate", timelimit=None, max_results=5)
    search_results = "\n\n".join([f"{i+1}. {result['title']}\n   URL: {result['href']}\n   Description: {result['body']}" for i, result in enumerate(results)])
    return search_results

async def process_message(message, formatted_question, user_id, search=False):
    current_time = update_current_time()
    user_data = get_user_data(user_id)
    add_to_chat_history(user_id, formatted_question)

    user_language = user_data['language']
    current_model = user_data['current_model']
    user_training_instruction = LOLILLM_TRAINING_INSTRUCTION if current_model == "lolillm-0.1-beta" else user_data['training_instruction']

    history = get_chat_history(user_id)
    chat_history_text = "\n".join([item[0] for item in history])

    if current_model != "simsimi":
        full_prompt = f"{user_training_instruction}\n\nCurrent time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n\nChat history:\n{chat_history_text}\n\nUser: {formatted_question}\nAI:"
    else:
        full_prompt = formatted_question

    sent_message = await bot.reply_to(message, get_text(user_language, 'thinking'))
    await bot.send_chat_action(message.chat.id, 'typing')

    if search:
        await bot.edit_message_text(get_text(user_language, 'searching'), chat_id=message.chat.id, message_id=sent_message.message_id)
        search_results = await search_web(formatted_question)
        if search_results:
            full_prompt += f"\n\nWeb search results:\n{search_results}"
        else:
            full_prompt += "\n\nNo web search results found."
        await bot.edit_message_text(get_text(user_language, 'thinking'), chat_id=message.chat.id, message_id=sent_message.message_id)

    response = await generate_response(full_prompt, current_model)

    if response:
        try:
            escaped_response = escape(response)
            await bot.edit_message_text(escaped_response, chat_id=message.chat.id, message_id=sent_message.message_id, parse_mode='MarkdownV2')
            add_to_chat_history(user_id, f"AI: {response}")
        except Exception as e:
            print(f"Error sending message: {e}")
            await bot.send_message(message.chat.id, response)
            add_to_chat_history(user_id, f"AI: {response}")
    else:
        await bot.edit_message_text(get_text(user_language, 'service_unavailable'), chat_id=message.chat.id, message_id=sent_message.message_id)

def get_system_info():
    cpu = platform.processor()
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count(logical=True)
    cpu_usage = psutil.cpu_percent()
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    os_info = f"{platform.system()} {platform.release()}"
    return cpu, cpu_cores, cpu_threads, cpu_usage, ram, disk, os_info

async def ping_server(url):
    try:
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            async with session.get(url, timeout=5) as response:
                end_time = time.time()
                return (end_time - start_time) * 1000  
    except Exception:
        return None

async def get_ip_info(ip_address):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.ipapi.is/?q={ip_address}") as response:
            if response.status == 200:
                return await response.json()
            else:
                return None

def chat_with_ai(query, model='gpt-3.5'):
    with DDGS() as ddgs:
        response = ddgs.chat(keywords=query, model=model)
        return response

async def chat_with_simsimi(message):
    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://simsimi.site/api/v2/?mode=talk&lang=en&message={message}&filter=true") as response:
            if response.status == 200:
                data = await response.json()
                return data.get('success', 'Sorry, I couldn\'t understand that.')
            else:
                return "Sorry, I couldn't process your request."

@bot.message_handler(commands=['start'])
async def handle_start(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    user_language = user_data['language']
    first_name = message.from_user.first_name
    await bot.reply_to(message, get_text(user_language, 'welcome_message').format(first_name))

@bot.message_handler(commands=['ask'])
async def handle_ask(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    user_language = user_data['language']

    if not check_spam(user_id):
        await bot.reply_to(message, get_text(user_language, 'wait_message'))
        return

    question = message.text[len('/ask '):].strip()
    if not question:
        await bot.reply_to(message, get_text(user_language, 'ask_prompt'))
        return

    await bot.send_chat_action(message.chat.id, 'typing')
    search = any(keyword in question.lower() for keyword in SEARCH_KEYWORDS)
    await process_message(message, question, user_id, search=search)

@bot.message_handler(commands=['clear'])
async def handle_clear(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    user_language = user_data['language']
    clear_chat_history(user_id)
    await bot.reply_to(message, get_text(user_language, 'chat_reset'))

@bot.message_handler(commands=['info'])
async def handle_info(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    user_language = user_data['language']
    cpu, cpu_cores, cpu_threads, cpu_usage, ram, disk, os_info = get_system_info()
    telegram_ping = await ping_server('https://api.telegram.org')
    gemini_ping = await ping_server('https://generativelanguage.googleapis.com')
    openai_ping = await ping_server('https://api.openai.com')
    claude_ping = await ping_server('https://api.anthropic.com')
    simsimi_ping = await ping_server('https://simsimi.site')
    duckduckgo_ping = await ping_server('https://www.google.com')

    info_message = (
        "🤖 HYDRA AI\n\n"
        f"📡 Ping Telegram: {telegram_ping:.2f}ms\n"
        f"📡 Ping Gemini: {gemini_ping:.2f}ms\n"
        f"📡 Ping OpenAI: {openai_ping:.2f}ms\n"
        f"📡 Ping Claude: {claude_ping:.2f}ms\n"
        f"📡 Ping SimSimi: {simsimi_ping:.2f}ms\n"
        f"📡 Ping Google: {duckduckgo_ping:.2f}ms\n\n"
        f"💻 System Information:\n"
        f"• CPU: {cpu}\n"
        f"• Cores: {cpu_cores}\n"
        f"• Threads: {cpu_threads}\n"
        f"• CPU Usage: {cpu_usage}%\n"
        f"• RAM: {ram.total // (1024 * 1024)} MB (Used: {ram.percent}%)\n"
        f"• Disk: {disk.total // (1024 * 1024 * 1024)} GB (Used: {disk.percent}%)\n"
        f"• OS: {os_info}\n\n"
        "✅ Status: 200 OK"
    )

    await bot.reply_to(message, info_message)

@bot.message_handler(commands=['switch'])
async def handle_switch(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    user_language = user_data['language']
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    buttons = [telebot.types.InlineKeyboardButton(text=model, callback_data=model) for model in VALID_MODELS]
    keyboard.add(*buttons)
    await bot.reply_to(message, get_text(user_language, 'model_switch'), reply_markup=keyboard)

@bot.message_handler(commands=['language'])
async def handle_language(message):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        telebot.types.InlineKeyboardButton(text="English 🇬🇧", callback_data="lang_en"),
        telebot.types.InlineKeyboardButton(text="한국인 🇰🇷", callback_data="lang_ko"),
        telebot.types.InlineKeyboardButton(text="中文 🇨🇳", callback_data="lang_zh"),
        telebot.types.InlineKeyboardButton(text="العربية 🇸🇦", callback_data="lang_ar"),
        telebot.types.InlineKeyboardButton(text="Tiếng Việt 🇻🇳", callback_data="lang_vi")
    ]
    keyboard.add(*buttons)
    await bot.reply_to(message, "Choose your language", reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
async def handle_callback(call):
    user_id = call.from_user.id
    user_data = get_user_data(user_id)
    user_language = user_data['language']

    if call.data.startswith("lang_"):
        new_language = call.data[5:]
        update_user_data(user_id, 'language', new_language)
        await bot.answer_callback_query(call.id, f"Language changed to {new_language}")
        await bot.send_message(call.message.chat.id, get_text(new_language, 'welcome_message').format(call.from_user.first_name))
    elif call.data in VALID_MODELS:
        selected_model = call.data
        if selected_model in VALID_MODELS:
            update_user_data(user_id, 'current_model', selected_model)
            clear_chat_history(user_id)
            await bot.answer_callback_query(call.id, get_text(user_language, 'model_switched').format(selected_model))
            await bot.edit_message_text(get_text(user_language, 'model_switched_reset').format(selected_model), chat_id=call.message.chat.id, message_id=call.message.message_id)
        else:
            await bot.answer_callback_query(call.id, get_text(user_language, 'invalid_model'), show_alert=True)

@bot.message_handler(commands=['training'])
async def handle_training(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    user_language = user_data['language']
    current_model = user_data['current_model']

    if current_model == "lolillm-0.1-beta" or current_model == "simsimi":
        await bot.reply_to(message, get_text(user_language, 'training_not_supported'))
        return

    existing_instruction = user_data['training_instruction']

    if message.text.strip() == '/training':
        response_message = get_text(user_language, 'training_prompt') + (existing_instruction if existing_instruction else get_text(user_language, 'no_training'))
        await bot.reply_to(message, response_message)
        return

    new_instruction = message.text[len('/training '):].strip()
    update_user_data(user_id, 'training_instruction', new_instruction)

    await bot.reply_to(message, get_text(user_language, 'training_updated').format(new_instruction))

@bot.message_handler(func=lambda message: message.reply_to_message is not None)
async def handle_reply(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    user_language = user_data['language']

    if not check_spam(user_id):
        await bot.reply_to(message, get_text(user_language, 'wait_message'))
        return

    question = message.text.strip()
    if not question:
        await bot.reply_to(message, get_text(user_language, 'enter_question'))
        return

    await bot.send_chat_action(message.chat.id, 'typing')
    search = any(keyword in question.lower() for keyword in SEARCH_KEYWORDS)
    await process_message(message, question, user_id, search=search)

@bot.message_handler(content_types=['photo'])
async def handle_photo(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    user_language = user_data['language']
    current_model = user_data['current_model']

    if not check_spam(user_id):
        await bot.reply_to(message, get_text(user_language, 'wait_message'))
        return

    file_id = message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    with open('received_photo.png', 'wb') as new_file:
        new_file.write(downloaded_file)

    img = PIL.Image.open('received_photo.png')
    sent_message = await bot.reply_to(message, get_text(user_language, 'processing_image'))
    await bot.send_chat_action(message.chat.id, 'typing')

    try:
        genai.configure(api_key=get_random_api_key())
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        response = await asyncio.to_thread(model.generate_content, ["What's in this image?", img], safety_settings=safety_settings)
        add_to_chat_history(user_id, "Sent an image")
        add_to_chat_history(user_id, f"AI: Image description: {response.text}")
        escaped_response = escape(get_text(user_language, 'image_description').format(response.text))
        await bot.edit_message_text(escaped_response, chat_id=message.chat.id, message_id=sent_message.message_id, parse_mode='MarkdownV2')
    except Exception as e:
        await bot.edit_message_text(get_text(user_language, 'service_unavailable'), chat_id=message.chat.id, message_id=sent_message.message_id)

@bot.message_handler(func=lambda message: True)
async def handle_all_messages(message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    user_language = user_data['language']

    if not check_spam(user_id):
        await bot.reply_to(message, get_text(user_language, 'wait_message'))
        return

    question = message.text.strip()

    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    ip_match = re.search(ip_pattern, question)

    if ip_match:
        ip_address = ip_match.group()
        sent_message = await bot.reply_to(message, get_text(user_language, 'checking_ip'))
        await bot.send_chat_action(message.chat.id, 'typing')
        ip_info = await get_ip_info(ip_address)
        if ip_info:
            formatted_question = f"Information about IP address {ip_address}: {ip_info}"
            await process_message(message, formatted_question, user_id)
        else:
            await bot.edit_message_text(get_text(user_language, 'ip_info_unavailable'), chat_id=message.chat.id, message_id=sent_message.message_id)
    else:
        if not question:
            await bot.reply_to(message, get_text(user_language, 'enter_question'))
            return

        await bot.send_chat_action(message.chat.id, 'typing')
        search = any(keyword in question.lower() for keyword in SEARCH_KEYWORDS)
        await process_message(message, question, user_id, search=search)

async def main():
    while True:
        try:
            await bot.polling(none_stop=True)
        except Exception as e:
            print(f"Bot polling error: {e}")
            await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(main())