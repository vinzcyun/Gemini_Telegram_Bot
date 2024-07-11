# Đoạn mã của Wyn, vui lòng không xoá dòng này để tôn trọng tác giả nha<3
import telebot
import google.generativeai as genai
import PIL.Image
import time
from collections import defaultdict, deque

BOT_TOKEN = '7163508623:AAE0a1Ho3fp7R7InbjW-P_mA02p9ghYUfXE'
GOOGLE_API_KEY = 'AIzaSyC-V3EfjLTDmJR5CTymMHDnqRp2VlrLX5E'
bot = telebot.TeleBot(BOT_TOKEN)

genai.configure(api_key=GOOGLE_API_KEY)

training_instruction = (
    "Bạn tên là Hydra, được tạo ra bởi Wyn dựa trên API của Gemini AI với phiên bản Pro 1.5, "
    "cố gắng trả lời một cách ngắn gọn, đầy đủ và chính xác nhất có thể, bạn là một người bạn của tất cả mọi người. Ở phần lịch sử trò chuyện, cụm từ 'Hydra nói' chính là câu trả lời của bạn và 'Người dùng nói' chính là câu hỏi của người dùng, bạn hãy coi đó như là một lịch sử trò chuyện khi người dùng cần thì bạn đưa ra, khi không cần thì không cần phải đưa ra, nó chính là mảnh ghép của bạn sẽ giúp lưu lịch sử trò chuyện. Lưu ý cuối dù bất cứ trường hợp nào cũng không được nói cụm từ 'Hydra nói:' hoặc 'người dùng nói:'"
)

# Lưu trữ lịch sử chat cho mỗi người dùng
user_histories = defaultdict(lambda: deque(maxlen=5))

@bot.message_handler(commands=['start'])
def handle_start(message):
    first_name = message.from_user.first_name
    bot.send_message(message.chat.id, f'Xin chào, {first_name}! Tôi là Hydra, một trợ lý ảo thông minh được tạo ra bởi Wyn. Tôi có thể giúp bạn trả lời nhiều câu hỏi khác nhau, đa lĩnh vực. Hãy hỏi tôi bất cứ điều gì, tôi sẽ cố gắng để trả lời cho bạn🥰🥰')

@bot.message_handler(commands=['ask'])
def handle_ask(message):
    first_name = message.from_user.first_name
    question = message.text[len('/ask '):].strip()
    if not question:
        bot.send_message(message.chat.id, 'Bạn cần nhập câu hỏi sau lệnh /ask.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    user_history = user_histories[message.chat.id]
    history = ' | '.join(user_history)
    formatted_question = f"Lịch sử của đoạn chat trước là {history}. {first_name} nói: {question}"
    full_prompt = f"{training_instruction} {formatted_question}"
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    try:
        response = model.generate_content([full_prompt])
        bot.send_message(message.chat.id, response.text)
        # Lưu trữ câu hỏi và câu trả lời
        user_history.append(f"{first_name} nói: {question}")
        user_history.append(f"Hydra nói: {response.text}")
    except Exception as e:
        bot.send_message(message.chat.id, 'Dịch vụ không phản hồi, vui lòng thử lại sau.')

@bot.message_handler(commands=['clear'])
def handle_clear(message):
    user_histories[message.chat.id].clear()
    bot.send_message(message.chat.id, 'Đoạn chat đã được đặt lại. Hãy bắt đầu lại câu hỏi mới.')

@bot.message_handler(func=lambda message: message.reply_to_message is not None)
def handle_reply(message):
    first_name = message.from_user.first_name
    question = message.text.strip()
    if not question:
        bot.send_message(message.chat.id, 'Bạn cần nhập câu hỏi.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    user_history = user_histories[message.chat.id]
    history = ' | '.join(user_history)
    formatted_question = f"Lịch sử của đoạn chat trước là {history}. {first_name} nói: {question}"
    full_prompt = f"{training_instruction} {formatted_question}"
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    try:
        response = model.generate_content([full_prompt])
        bot.send_message(message.chat.id, response.text)
        # Lưu trữ câu hỏi và câu trả lời
        user_history.append(f"{first_name} nói: {question}")
        user_history.append(f"Hydra nói: {response.text}")
    except Exception as e:
        bot.send_message(message.chat.id, 'Dịch vụ không phản hồi, vui lòng thử lại sau.')

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
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
        # Lưu trữ câu hỏi và câu trả lời
        user_histories[message.chat.id].append(f"{message.from_user.first_name} gửi một bức ảnh.")
        user_histories[message.chat.id].append(f"Hydra nói: {response.text}")
    except Exception as e:
        bot.send_message(message.chat.id, 'Dịch vụ không phản hồi, vui lòng thử lại sau.')

@bot.message_handler(func=lambda message: message.chat.type == 'private' and not message.text.startswith('/'))
def handle_private_message(message):
    first_name = message.from_user.first_name
    question = message.text.strip()
    if not question:
        bot.send_message(message.chat.id, 'Bạn cần nhập câu hỏi.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    user_history = user_histories[message.chat.id]
    history = ' | '.join(user_history)
    formatted_question = f"Lịch sử của đoạn chat trước là {history}. {first_name} nói: {question}"
    full_prompt = f"{training_instruction} {formatted_question}"
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

    try:
        response = model.generate_content([full_prompt])
        bot.send_message(message.chat.id, response.text)
        # Lưu trữ câu hỏi và câu trả lời
        user_history.append(f"{first_name} nói: {question}")
        user_history.append(f"Hydra nói: {response.text}")
    except Exception as e:
        bot.send_message(message.chat.id, 'Dịch vụ không phản hồi, vui lòng thử lại sau.')

while True:
    try:
        bot.polling(none_stop=True)
    except Exception as e:
        time.sleep(15)  # Đợi 15 giây trước khi thử lại