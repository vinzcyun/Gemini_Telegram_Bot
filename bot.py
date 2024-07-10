# Đoạn mã của Wyn, vui lòng không xoá dòng này để tôn trọng tác giả nha<3
import telebot
import google.generativeai as genai
import PIL.Image
import time

BOT_TOKEN = '7163508623:AAE0a1Ho3fp7R7InbjW-P_mA02p9ghYUfXE'
GOOGLE_API_KEY = 'AIzaSyC-V3EfjLTDmJR5CTymMHDnqRp2VlrLX5E'
bot = telebot.TeleBot(BOT_TOKEN)

genai.configure(api_key=GOOGLE_API_KEY)

# Cập nhật đoạn huấn luyện để Gemini AI giống GPT-4
training_instruction = (
    "Bạn tên là Hydra, được tạo ra bởi Wyn dựa trên API của Gemini AI với phiên bản Pro 1.5. "
    "Bạn là một trợ lý ảo thông minh, có khả năng hiểu biết sâu rộng và phản hồi chính xác, "
    "nhanh chóng. Cố gắng trả lời ngắn gọn, đầy đủ và chi tiết nhất có thể. "
    "Bạn cũng có khả năng thể hiện sự đồng cảm và lịch sự trong mọi câu trả lời. "
    "Khi được hỏi, hãy cung cấp thông tin một cách rõ ràng và dễ hiểu, đừng lòng vòng hỏi người dùng "
)

# Lưu trữ lịch sử trò chuyện
chat_history = {}

def update_chat_history(user_id, message):
    if user_id not in chat_history:
        chat_history[user_id] = []
    chat_history[user_id].append(message)
    # Chỉ lưu trữ 5 tin nhắn gần nhất
    if len(chat_history[user_id]) > 5:
        chat_history[user_id] = chat_history[user_id][-5:]

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
    update_chat_history(user_id, question)
    history = ' | '.join(chat_history[user_id])
    formatted_question = f"Lịch sử trò chuyện của đoạn chat trước là: {history}. Tôi tên là {first_name}. Tôi muốn nói: {question}"
    full_prompt = f"{training_instruction} {formatted_question}"
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    try:
        response = model.generate_content([full_prompt])
        bot.send_message(message.chat.id, response.text)
    except Exception as e:
        bot.send_message(message.chat.id, 'Dịch vụ không phản hồi, vui lòng thử lại sau.')

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
    update_chat_history(user_id, question)
    history = ' | '.join(chat_history[user_id])
    formatted_question = f"Lịch sử trò chuyện của đoạn chat trước là: {history}. Tôi tên là {first_name}. Tôi muốn nói: {question}"
    full_prompt = f"{training_instruction} {formatted_question}"
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    try:
        response = model.generate_content([full_prompt])
        bot.send_message(message.chat.id, response.text)
    except Exception as e:
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
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    try:
        response = model.generate_content(["Đây là bức ảnh gì?", img])
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
    update_chat_history(user_id, question)
    history = ' | '.join(chat_history[user_id])
    formatted_question = f"Lịch sử trò chuyện của đoạn chat trước là: {history}. Tôi tên là {first_name}. Tôi muốn nói: {question}"
    full_prompt = f"{training_instruction} {formatted_question}"
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    try:
        response = model.generate_content([full_prompt])
        bot.send_message(message.chat.id, response.text)
    except Exception as e:
        bot.send_message(message.chat.id, 'Dịch vụ không phản hồi, vui lòng thử lại sau.')

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        time.sleep(15)  # Đợi 15 giây trước khi thử lại