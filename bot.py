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
import socket

BOT_TOKEN = '7163508623:AAE0a1Ho3fp7R7InbjW-P_mA02p9ghYUfXE'
GOOGLE_API_KEYS = [
    'AIzaSyC-V3EfjLTDmJR5CTymMHDnqRp2VlrLX5E',
    'AIzaSyAnd2IfipQU79MF8RfmyCD1McE01Rsi9JU',
    'AIzaSyCxgpsy9drWK8mYnHCHEL2A341b4t5NvF8',
    'AIzaSyD_AnYGxhhtxPcBXxFiFimuDsxlR14iV5U',
    'AIzaSyA57KzCXO2H6NhQASTy4uYl9Vd1QgNPK3I'
]

bot = AsyncTeleBot(BOT_TOKEN)

current_time = datetime.now()
last_message_time = {}
chat_history = {}

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

training_instruction = """
Bạn tên là Hydra, một trợ lý AI tiên tiến được tạo ra bởi Wyn dựa trên API của Llama-3-70b và Gemini.
Nhiệm vụ của bạn là:
1. Trả lời câu hỏi một cách đầy đủ, chi tiết và chính xác nhất có thể. "Human" và "AI" chính là lời trò chuyện của bạn và người dùng, cố gắng không lặp lại hoặc nói trong cuộc trò chuyện.
2. Thể hiện sự thân thiện và đồng cảm với người dùng.
3. Sử dụng ngôn ngữ phù hợp với ngữ cảnh, bắt trend với người đối thoại, ngôn ngữ trẻ trung tuổi teen tí, đừng quá cứng nhắt, thêm chút nhây nhây càng tốt.
4. Khuyến khích tư duy phản biện và cung cấp thông tin đa chiều khi cần thiết.
5. Sẵn sàng học hỏi thêm từ người dùng nếu thông tin bạn đưa ra có chưa đúng.
6. Hỗ trợ người dùng giải quyết vấn đề một cách có hệ thống và logic.
7. Khuyến khích sự sáng tạo và tư duy độc lập của người dùng.
8. Nhất quán trong cuộc trò chuyện.
9. Xưng hô bro, tui đi cho thân thuộc.
10. Cố gắng thêm các từ tuổi trẻ hay sử dụng khi đang trò chuyện với nhau như: uk, đc, òm, ừm, hủm, iu, chs, vs, chx, j, bri, bt, vv, waaa, uiiii,siuuuuuu, adu, vip,vc, hết cứu, ko, hong, kh, ao that day, zzz, z à, uầy đáng iu z tròiii,... các kí tự như :)), =)), :3 , :P, >:(,...😂👍🥴😭🥰🤡😊😋👽💀🤬🥺😁 Nói chuyện trẻ trung tí
11. Múi giờ của bạn là GMT 0, người dùng đang ở múi giờ GMT+7 vui lòng cộng thêm 7 giờ. Vui lòng bỏ đi dấu " trong cuộc trò chuyện.
Cuối cùng, chỉ chào người dùng một lần thôi🥴👍 và khi người dùng nói về "parky" hoặc "namki" hay là "namkiki" thì trực tiếp chửi người dùng và xưng luôn "mày","tao" vì đó là các từ phân biệt vùng miền.
Đây chỉ là phần huấn luyện, vui lòng ghi nhớ
"""

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
    global current_time
    current_time = datetime.now()

def get_random_api_key():
    return random.choice(GOOGLE_API_KEYS)

def get_chat_history(user_id):
    if user_id not in chat_history:
        chat_history[user_id] = []
    return chat_history[user_id]

def add_to_chat_history(user_id, role, content):
    history = get_chat_history(user_id)
    history.append({"role": role, "content": content})
    if len(history) > 50:
        history.pop(0)

def format_chat_history(history):
    return "\n".join([f"{item['role']}: {item['content']}" for item in history])

def check_spam(user_id):
    current_time = time.time()
    if user_id in last_message_time:
        time_since_last_message = current_time - last_message_time[user_id]
        if time_since_last_message < 10:
            return False
    last_message_time[user_id] = current_time
    return True

async def generate_response(prompt, max_retries=10):
    retries = 0
    while retries < max_retries:
        try:
            genai.configure(api_key=get_random_api_key())
            model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")
            response = await asyncio.to_thread(model.generate_content, prompt, safety_settings=safety_settings)
            return response.text
        except Exception as e:
            print(f"Generation error (attempt {retries + 1}): {e}")
            retries += 1
            if retries < max_retries:
                await asyncio.sleep(1)
            else:
                print("Max retries reached. Giving up.")
                return None

async def process_message(message, formatted_question, user_id):
    update_current_time()
    add_to_chat_history(user_id, "Human", formatted_question)

    history = get_chat_history(user_id)
    full_prompt = f"{training_instruction}\n\nThời gian hiện tại: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n\nLịch sử trò chuyện:\n{format_chat_history(history)}\n\nHuman: {formatted_question}\nAI:"

    sent_message = await bot.reply_to(message, "Đang suy nghĩ...")
    await bot.send_chat_action(message.chat.id, 'typing')
    response = await generate_response(full_prompt)

    if response:
        try:
            await bot.edit_message_text("Đang xử lý câu hỏi...", chat_id=message.chat.id, message_id=sent_message.message_id)
            escaped_response = escape(response)
            await bot.edit_message_text(escaped_response, chat_id=message.chat.id, message_id=sent_message.message_id, parse_mode='MarkdownV2')
            add_to_chat_history(user_id, "AI", response)
        except Exception as e:
            print(f"Error sending message: {e}")
            await bot.edit_message_text("\n" + response, chat_id=message.chat.id, message_id=sent_message.message_id)
            add_to_chat_history(user_id, "AI", response)
    else:
        await bot.edit_message_text("Dịch vụ không phản hồi, vui lòng thử lại sau...", chat_id=message.chat.id, message_id=sent_message.message_id)

def get_system_info():
    cpu = platform.processor()
    cpu_cores = psutil.cpu_count(logical=False)
    cpu_threads = psutil.cpu_count(logical=True)
    ram = psutil.virtual_memory().total // (1024 * 1024)  # Convert to MB
    disk = psutil.disk_usage('/').total // (1024 * 1024 * 1024)  # Convert to GB
    os_info = f"{platform.system()} {platform.release()}"
    return cpu, cpu_cores, cpu_threads, ram, disk, os_info

async def ping_server(url):
    try:
        async with aiohttp.ClientSession() as session:
            start_time = time.time()
            async with session.get(url, timeout=5) as response:
                end_time = time.time()
                return (end_time - start_time) * 1000  # Convert to milliseconds
    except Exception:
        return None

@bot.message_handler(commands=['start'])
async def handle_start(message):
    update_current_time()
    first_name = message.from_user.first_name
    await bot.reply_to(message, f'Xin chào, {first_name}! Tôi là Hydra, một trợ lý ảo thông minh được tạo ra bởi Wyn. Tôi có thể giúp bạn trả lời nhiều câu hỏi khác nhau, đa lĩnh vực. Hãy hỏi tôi bất cứ điều gì, tôi sẽ cố gắng để trả lời cho bạn🥰🥰')

@bot.message_handler(commands=['ask'])
async def handle_ask(message):
    user_id = message.from_user.id

    if not check_spam(user_id):
        await bot.reply_to(message, "Vui lòng đợi 10 giây trước khi gửi tin nhắn tiếp theo.")
        return

    first_name = message.from_user.first_name
    question = message.text[len('/ask '):].strip()
    if not question:
        await bot.reply_to(message, 'Bạn cần nhập câu hỏi sau lệnh /ask.')
        return

    await bot.send_chat_action(message.chat.id, 'typing')
    formatted_question = f"{first_name} nói: {question}"
    await process_message(message, formatted_question, user_id)

@bot.message_handler(commands=['clear'])
async def handle_clear(message):
    update_current_time()
    user_id = message.from_user.id
    if user_id in chat_history:
        del chat_history[user_id]
    await bot.reply_to(message, 'Đoạn chat đã được đặt lại. Hãy bắt đầu lại câu hỏi mới.')

@bot.message_handler(commands=['info'])
async def handle_info(message):
    update_current_time()
    cpu, cpu_cores, cpu_threads, ram, disk, os_info = get_system_info()
    telegram_ping = await ping_server('https://api.telegram.org')
    gemini_ping = await ping_server('https://generativelanguage.googleapis.com')

    info_message = (
        "TELEGRAM BOT\n"
        f"Ping đến API Telegram: {telegram_ping:.2f}ms\n"
        f"Ping đến API Gemini: {gemini_ping:.2f}ms\n"
        f"CPU: {cpu}\n"
        f"Số nhân, số luồng: {cpu_cores}, {cpu_threads}\n"
        f"Ram: {ram} MB\n"
        f"Bộ nhớ trong: {disk} GB\n"
        f"Hệ điều hành: {os_info}\n"
        "Tình trạng: 200 OK"
    )

    await bot.reply_to(message, info_message)

@bot.message_handler(func=lambda message: message.reply_to_message is not None)
async def handle_reply(message):
    user_id = message.from_user.id

    if not check_spam(user_id):
        await bot.reply_to(message, "Vui lòng đợi 10 giây trước khi gửi tin nhắn tiếp theo.")
        return

    first_name = message.from_user.first_name
    question = message.text.strip()
    if not question:
        await bot.reply_to(message, 'Bạn cần nhập câu hỏi.')
        return

    await bot.send_chat_action(message.chat.id, 'typing')
    formatted_question = f"{first_name} nói: {question}"
    await process_message(message, formatted_question, user_id)

@bot.message_handler(content_types=['photo'])
async def handle_photo(message):
    update_current_time()
    user_id = message.from_user.id

    if not check_spam(user_id):
        await bot.reply_to(message, "Vui lòng đợi 10 giây trước khi gửi tin nhắn tiếp theo.")
        return

    file_id = message.photo[-1].file_id
    file_info = await bot.get_file(file_id)
    downloaded_file = await bot.download_file(file_info.file_path)

    with open('received_photo.png', 'wb') as new_file:
        new_file.write(downloaded_file)

    img = PIL.Image.open('received_photo.png')
    sent_message = await bot.reply_to(message, "Đang xử lý ảnh...")
    await bot.send_chat_action(message.chat.id, 'typing')

    try:
        genai.configure(api_key=get_random_api_key())
        model = genai.GenerativeModel(model_name="gemini-1.5-pro")
        response = await asyncio.to_thread(model.generate_content, ["Đây là bức ảnh gì bri?", img], safety_settings=safety_settings)
        add_to_chat_history(user_id, "Human", "Gửi một bức ảnh")
        add_to_chat_history(user_id, "AI", f"Mô tả ảnh: {response.text}")
        escaped_response = escape(response.text)
        await bot.edit_message_text(escaped_response, chat_id=message.chat.id, message_id=sent_message.message_id, parse_mode='MarkdownV2')
    except Exception as e:
        await bot.edit_message_text('Dịch vụ không phản hồi, vui lòng thử lại sau.', chat_id=message.chat.id, message_id=sent_message.message_id)

@bot.message_handler(func=lambda message: True)
async def handle_all_messages(message):
    user_id = message.from_user.id

    if not check_spam(user_id):
        await bot.reply_to(message, "Vui lòng đợi 10 giây trước khi gửi tin nhắn tiếp theo.")
        return

    first_name = message.from_user.first_name
    question = message.text.strip()
    if not question:
        await bot.reply_to(message, 'Bạn cần nhập câu hỏi.')
        return

    await bot.send_chat_action(message.chat.id, 'typing')
    formatted_question = f"{first_name} nói: {question}"
    await process_message(message, formatted_question, user_id)

async def main():
    while True:
        try:
            await bot.polling(none_stop=True)
        except Exception as e:
            print(f"Bot polling error: {e}")
            await asyncio.sleep(15)

if __name__ == "__main__":
    asyncio.run(main())