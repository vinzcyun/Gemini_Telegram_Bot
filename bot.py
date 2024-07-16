import telebot
import google.generativeai as genai
import PIL.Image
import json
import os
from collections import deque

BOT_TOKEN = '7163508623:AAE0a1Ho3fp7R7InbjW-P_mA02p9ghYUfXE'
GOOGLE_API_KEY = 'AIzaSyC-V3EfjLTDmJR5CTymMHDnqRp2VlrLX5E'
bot = telebot.TeleBot(BOT_TOKEN)

genai.configure(api_key=GOOGLE_API_KEY)

MAX_HISTORY = 100
CONTEXT_LENGTH = 10  # Số tin nhắn gần nhất sử dụng cho context

training_instruction = (
    "Bạn tên là Hydra, được tạo ra bởi Wyn dựa trên API của Gemini AI với phiên bản Pro 1.5, "
    "cố gắng trả lời một cách ngắn gọn, đầy đủ và chính xác nhất có thể, bạn là một người bạn của tất cả mọi người."
)

chat_history = {}

def save_chat_history(user_id, message):
    if user_id not in chat_history:
        chat_history[user_id] = deque(maxlen=MAX_HISTORY)
    
    chat_history[user_id].append(message)
    
    with open(f'chat_history_{user_id}.json', 'w', encoding='utf-8') as f:
        json.dump(list(chat_history[user_id]), f, ensure_ascii=False, indent=4)

def load_chat_history(user_id):
    if user_id in chat_history:
        return list(chat_history[user_id])
    try:
        with open(f'chat_history_{user_id}.json', 'r', encoding='utf-8') as f:
            history = json.load(f)
            chat_history[user_id] = deque(history, maxlen=MAX_HISTORY)
            return list(chat_history[user_id])
    except FileNotFoundError:
        chat_history[user_id] = deque(maxlen=MAX_HISTORY)
        return []

def clear_chat_history(user_id):
    if user_id in chat_history:
        chat_history[user_id].clear()
    try:
        os.remove(f'chat_history_{user_id}.json')
    except FileNotFoundError:
        pass

def generate_response(user_id, first_name, question):
    history = load_chat_history(user_id)
    
    conversation = [
        {"role": "system", "content": training_instruction},
        *history[-CONTEXT_LENGTH:],  # Sử dụng 10 tin nhắn gần nhất
        {"role": "user", "content": f"Tôi là {first_name}, tôi muốn hỏi: {question}"}
    ]
    
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
    
    try:
        response = model.generate_content(conversation)
        return response.text
    except Exception as e:
        return 'Dịch vụ không phản hồi, vui lòng thử lại sau.'

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    response = f'Xin chào, {first_name}! Tôi là Hydra, một trợ lý ảo thông minh được tạo ra bởi Wyn. Tôi có thể giúp bạn trả lời nhiều câu hỏi khác nhau, đa lĩnh vực. Hãy hỏi tôi bất cứ điều gì, tôi sẽ cố gắng để trả lời cho bạn🥰🥰'
    bot.send_message(message.chat.id, response)
    save_chat_history(user_id, {"role": "assistant", "content": response})

@bot.message_handler(commands=['ask'])
def handle_ask(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    question = message.text[len('/ask '):].strip()
    if not question:
        bot.send_message(message.chat.id, 'Bạn cần nhập câu hỏi sau lệnh /ask.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    response = generate_response(user_id, first_name, question)
    bot.send_message(message.chat.id, response)
    save_chat_history(user_id, {"role": "user", "content": question})
    save_chat_history(user_id, {"role": "assistant", "content": response})

@bot.message_handler(commands=['clear'])
def handle_clear(message):
    user_id = message.from_user.id
    clear_chat_history(user_id)
    bot.send_message(message.chat.id, 'Đoạn chat đã được đặt lại. Hãy bắt đầu lại câu hỏi mới.')

@bot.message_handler(func=lambda message: message.chat.type == 'private' and not message.text.startswith('/'))
def handle_private_message(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    question = message.text.strip()
    if not question:
        bot.send_message(message.chat.id, 'Bạn cần nhập câu hỏi.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    response = generate_response(user_id, first_name, question)
    bot.send_message(message.chat.id, response)
    save_chat_history(user_id, {"role": "user", "content": question})
    save_chat_history(user_id, {"role": "assistant", "content": response})

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        time.sleep(15)  # Đợi 15 giây trước khi thử lại