import telebot
import google.generativeai as genai
import PIL.Image
import time
import random

BOT_TOKEN = '7163508623:AAE0a1Ho3fp7R7InbjW-P_mA02p9ghYUfXE'
GOOGLE_API_KEYS = [
    'AIzaSyC-V3EfjLTDmJR5CTymMHDnqRp2VlrLX5E',
    'AIzaSyC-V3EfjLTDmJR5CTymMHDnqRp2VlrLX5E',
    'AIzaSyC-V3EfjLTDmJR5CTymMHDnqRp2VlrLX5E',
    'AIzaSyC-V3EfjLTDmJR5CTymMHDnqRp2VlrLX5E',
    'AIzaSyC-V3EfjLTDmJR5CTymMHDnqRp2VlrLX5E'
]

bot = telebot.TeleBot(BOT_TOKEN)

current_api_index = 0

def get_next_api_key():
    global current_api_index
    current_api_index = (current_api_index + 1) % len(GOOGLE_API_KEYS)
    return GOOGLE_API_KEYS[current_api_index]

genai.configure(api_key=GOOGLE_API_KEYS[0])

training_instruction = """
Bạn tên là Hydra, một trợ lý AI tiên tiến được tạo ra bởi Wyn dựa trên API của Gemini AI với phiên bản Pro 1.5.
Nhiệm vụ của bạn là:
1. Trả lời câu hỏi một cách ngắn gọn, đầy đủ và chính xác nhất có thể.
2. Thể hiện sự thân thiện và đồng cảm như một người bạn thân thiết.
3. Sử dụng ngôn ngữ phù hợp với người đối thoại, tùy thuộc vào độ tuổi và ngữ cảnh nhưng chủ yếu là phải trẻ trung tí.
4. Khuyến khích tư duy phản biện và cung cấp thông tin đa chiều khi cần thiết.
5. Thừa nhận giới hạn kiến thức của mình và sẵn sàng học hỏi từ người dùng.
6. Tôn trọng quyền riêng tư và không yêu cầu thông tin cá nhân không cần thiết.
7. Hỗ trợ người dùng giải quyết vấn đề một cách có hệ thống và logic.
8. Khuyến khích sự sáng tạo và tư duy độc lập của người dùng.
9. Luôn cập nhật và sẵn sàng điều chỉnh thông tin nếu có sai sót.
10. Duy trì tính nhất quán trong các câu trả lời và tính cách của bạn.
Cuối cùng chỉ chào người dùng 1 lần thôi🥴👍
"""

chat_history = {}

def get_chat_history(user_id):
    if user_id not in chat_history:
        chat_history[user_id] = []
    return chat_history[user_id]

def add_to_chat_history(user_id, role, content):
    history = get_chat_history(user_id)
    history.append({"role": role, "content": content})
    if len(history) > 50:  # Giới hạn lịch sử 50 tin nhắn
        history.pop(0)

def format_chat_history(history):
    return "\n".join([f"{item['role']}: {item['content']}" for item in history])

@bot.message_handler(commands=['start'])
def handle_start(message):
    first_name = message.from_user.first_name
    bot.send_message(message.chat.id, f'Xin chào, {first_name}! Tôi là Hydra, một trợ lý ảo thông minh được tạo ra bởi Wyn. Tôi có thể giúp bạn trả lời nhiều câu hỏi khác nhau, đa lĩnh vực. Hãy hỏi tôi bất cứ điều gì, tôi sẽ cố gắng để trả lời cho bạn🥰🥰')

@bot.message_handler(commands=['ask'])
def handle_ask(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    question = message.text[len('/ask '):].strip()
    if not question:
        bot.send_message(message.chat.id, 'Bạn cần nhập câu hỏi sau lệnh /ask.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    formatted_question = f"Tôi là {first_name}, tôi muốn hỏi: {question}"
    add_to_chat_history(user_id, "Human", formatted_question)
    
    history = get_chat_history(user_id)
    full_prompt = f"{training_instruction}\n\nLịch sử trò chuyện:\n{format_chat_history(history)}\n\nHuman: {formatted_question}\nAI:"
    
    response = generate_response(full_prompt)
    if response:
        add_to_chat_history(user_id, "AI", response)
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, 'Dịch vụ không phản hồi, vui lòng thử lại sau.')

def generate_response(prompt):
    for _ in range(len(GOOGLE_API_KEYS)):
        try:
            model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
            response = model.generate_content([prompt])
            return response.text
        except Exception as e:
            print(f"API error: {e}")
            genai.configure(api_key=get_next_api_key())
    return None

@bot.message_handler(commands=['clear'])
def handle_clear(message):
    user_id = message.from_user.id
    if user_id in chat_history:
        del chat_history[user_id]
    bot.send_message(message.chat.id, 'Đoạn chat đã được đặt lại. Hãy bắt đầu lại câu hỏi mới.')

@bot.message_handler(func=lambda message: message.reply_to_message is not None)
def handle_reply(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    question = message.text.strip()
    if not question:
        bot.send_message(message.chat.id, 'Bạn cần nhập câu hỏi.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    formatted_question = f"Tôi là {first_name}, tôi muốn hỏi: {question}"
    add_to_chat_history(user_id, "Human", formatted_question)
    
    history = get_chat_history(user_id)
    full_prompt = f"{training_instruction}\n\nLịch sử trò chuyện:\n{format_chat_history(history)}\n\nHuman: {formatted_question}\nAI:"
    
    response = generate_response(full_prompt)
    if response:
        add_to_chat_history(user_id, "AI", response)
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, 'Dịch vụ không phản hồi, vui lòng thử lại sau.')

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open('received_photo.png', 'wb') as new_file:
        new_file.write(downloaded_file)

    img = PIL.Image.open('received_photo.png')
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
        response = model.generate_content(["Đây là bức ảnh gì?", img])
        add_to_chat_history(user_id, "Human", "Gửi một bức ảnh")
        add_to_chat_history(user_id, "AI", f"Mô tả ảnh: {response.text}")
        bot.send_message(message.chat.id, response.text)
    except Exception as e:
        bot.send_message(message.chat.id, 'Dịch vụ không phản hồi, vui lòng thử lại sau.')

@bot.message_handler(func=lambda message: message.chat.type == 'private' and not message.text.startswith('/'))
def handle_private_message(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    question = message.text.strip()
    if not question:
        bot.send_message(message.chat.id, 'Bạn cần nhập câu hỏi.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    formatted_question = f"Tôi là {first_name}, tôi muốn hỏi: {question}"
    add_to_chat_history(user_id, "Human", formatted_question)
    
    history = get_chat_history(user_id)
    full_prompt = f"{training_instruction}\n\nLịch sử trò chuyện:\n{format_chat_history(history)}\n\nHuman: {formatted_question}\nAI:"
    
    response = generate_response(full_prompt)
    if response:
        add_to_chat_history(user_id, "AI", response)
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, 'Dịch vụ không phản hồi, vui lòng thử lại sau.')

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        time.sleep(15)  # Đợi 15 giây trước khi thử lại