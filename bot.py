import telebot
import google.generativeai as genai

BOT_TOKEN = '7462456370:AAEpRNbLqbQt8vRin8CeZCUgNVyyB7tQLsE'
GOOGLE_API_KEY = 'AIzaSyC-V3EfjLTDmJR5CTymMHDnqRp2VlrLX5E'
bot = telebot.TeleBot(BOT_TOKEN)

genai.configure(api_key=GOOGLE_API_KEY)

training_instruction = (
    "Bạn tên là Hydra, được tạo ra bởi Wyn dựa trên API của Gemini AI với phiên bản Pro 1.5, "
    "cố gắng trả lời một cách ngắn gọn, đầy đủ và chính xác nhất có thể, bạn là một người bạn của tất cả mọi người."
)

@bot.message_handler(commands=['start'])
def handle_start(message):
    first_name = message.from_user.first_name
    bot.send_message(message.chat.id, f'Xin chào, {first_name}! Tôi là Hydra, một trợ lý ảo thông minh được tạo ra bởi Wyn. Tôi có thể giúp bạn trả lời nhiều câu hỏi khác nhau, đa lĩnh vực. Hãy hỏi tôi bất cứ điều gì, tôi sẽ cố gắng để trả lời cho bạn')

@bot.message_handler(commands=['ask'])
def handle_ask(message):
    first_name = message.from_user.first_name
    question = message.text[len('/ask '):].strip()
    if not question:
        bot.send_message(message.chat.id, 'Bạn cần nhập câu hỏi sau lệnh /ask.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    formatted_question = f"Tôi là {first_name}, tôi muốn hỏi: {question}"
    full_prompt = f"{training_instruction} {formatted_question}"
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
    response = model.generate_content([full_prompt])
    
    bot.send_message(message.chat.id, response.text)

@bot.message_handler(func=lambda message: message.reply_to_message is not None)
def handle_reply(message):
    first_name = message.from_user.first_name
    question = message.text.strip()
    if not question:
        bot.send_message(message.chat.id, 'Bạn cần nhập câu hỏi.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    formatted_question = f"Tôi là {first_name}, tôi muốn hỏi: {question}"
    full_prompt = f"{training_instruction} {formatted_question}"
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
    response = model.generate_content([full_prompt])
    
    bot.send_message(message.chat.id, response.text)

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
    response = model.generate_content(["What is in this photo?", img])
    
    bot.send_message(message.chat.id, response.text)

@bot.message_handler(func=lambda message: message.chat.type == 'private' and not message.text.startswith('/'))
def handle_private_message(message):
    first_name = message.from_user.first_name
    question = message.text.strip()
    if not question:
        bot.send_message(message.chat.id, 'Bạn cần nhập câu hỏi.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    formatted_question = f"Tôi là {first_name}, tôi muốn hỏi: {question}"
    full_prompt = f"{training_instruction} {formatted_question}"
    model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
    response = model.generate_content([full_prompt])
    
    bot.send_message(message.chat.id, response.text)

bot.polling()
