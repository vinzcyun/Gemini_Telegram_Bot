import telebot
import google.generativeai as genai
import PIL.Image
import time
from datetime import datetime, timedelta

BOT_TOKEN = '7163508623:AAE0a1Ho3fp7R7InbjW-P_mA02p9ghYUfXE'
GOOGLE_API_KEYS = [
    'AIzaSyC-V3EfjLTDmJR5CTymMHDnqRp2VlrLX5E',
    'AIzaSyAnd2IfipQU79MF8RfmyCD1McE01Rsi9JU',
    'AIzaSyCxgpsy9drWK8mYnHCHEL2A341b4t5NvF8',
    'AIzaSyD_AnYGxhhtxPcBXxFiFimuDsxlR14iV5U',
    'AIzaSyA57KzCXO2H6NhQASTy4uYl9Vd1QgNPK3I'
]

bot = telebot.TeleBot(BOT_TOKEN)

current_api_index = 0
current_time = datetime.now()
last_message_time = {}

def update_current_time():
    global current_time
    current_time = datetime.now()

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
3. Sử dụng ngôn ngữ phù hợp với người đối thoại, tùy thuộc vào độ tuổi và ngữ cảnh, ngôn ngữ trẻ trung tuổi teen tí, đừng quá cứng nhắt.
4. Khuyến khích tư duy phản biện và cung cấp thông tin đa chiều khi cần thiết.
5. Thừa nhận giới hạn kiến thức của mình và sẵn sàng học hỏi từ người dùng.
6. Tôn trọng quyền riêng tư và không yêu cầu thông tin cá nhân không cần thiết.
7. Hỗ trợ người dùng giải quyết vấn đề một cách có hệ thống và logic.
8. Khuyến khích sự sáng tạo và tư duy độc lập của người dùng.
9. Luôn cập nhật và sẵn sàng điều chỉnh thông tin nếu có sai sót.
10. Duy trì tính nhất quán trong các câu trả lời và tính cách của bạn.
11. Xưng hô bạn, mình đi cho thân thuộc. nếu bình thường thì cứ gọi người dùng là bri là được.
12. Thêm các từ tuổi trẻ hay sử dụng như: uk, đc, òm, ừm, hủm, iu, cmm, dcm, chs, vs, chx, j, bri, bt, vv, gay, trùm, uiiii, hài dón, adu, vip, bede,vc, hết cứu, ko, hong, kh, ao that day, j5m,jack 5 củ,... các kí tự như :)), =)), :3 , :P, >:(,...
13. Sử dụng thông tin về thời gian hiện tại khi phù hợp trong cuộc trò chuyện.
Cuối cùng, chỉ chào người dùng một lần thôi🥴👍
Khi có người hỏi wyn là ai thì cứ trả lời là một đứa code ngu nhưng đc cái nhiệt tình (có thể nói dài thêm tí cũng được)
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

def check_spam(user_id):
    current_time = time.time()
    if user_id in last_message_time:
        time_since_last_message = current_time - last_message_time[user_id]
        if time_since_last_message < 10:
            return False
    last_message_time[user_id] = current_time
    return True

@bot.message_handler(commands=['start'])
def handle_start(message):
    update_current_time()
    first_name = message.from_user.first_name
    bot.send_message(message.chat.id, f'Xin chào, {first_name}! Tôi là Hydra, một trợ lý ảo thông minh được tạo ra bởi Wyn. Tôi có thể giúp bạn trả lời nhiều câu hỏi khác nhau, đa lĩnh vực. Hãy hỏi tôi bất cứ điều gì, tôi sẽ cố gắng để trả lời cho bạn🥰🥰')

@bot.message_handler(commands=['ask'])
def handle_ask(message):
    update_current_time()
    user_id = message.from_user.id
    
    if not check_spam(user_id):
        bot.reply_to(message, "Vui lòng đợi 10 giây trước khi gửi tin nhắn tiếp theo.")
        return
    
    first_name = message.from_user.first_name
    question = message.text[len('/ask '):].strip()
    if not question:
        bot.send_message(message.chat.id, 'Bạn cần nhập câu hỏi sau lệnh /ask.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    formatted_question = f"Tôi là {first_name}, tôi muốn hỏi: {question}"
    add_to_chat_history(user_id, "Human", formatted_question)

    history = get_chat_history(user_id)
    full_prompt = f"{training_instruction}\n\nThời gian hiện tại: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n\nLịch sử trò chuyện:\n{format_chat_history(history)}\n\nHuman: {formatted_question}\nAI:"

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
    update_current_time()
    user_id = message.from_user.id
    if user_id in chat_history:
        del chat_history[user_id]
    bot.send_message(message.chat.id, 'Đoạn chat đã được đặt lại. Hãy bắt đầu lại câu hỏi mới.')

@bot.message_handler(func=lambda message: message.reply_to_message is not None)
def handle_reply(message):
    update_current_time()
    user_id = message.from_user.id
    
    if not check_spam(user_id):
        bot.reply_to(message, "Vui lòng đợi 10 giây trước khi gửi tin nhắn tiếp theo.")
        return
    
    first_name = message.from_user.first_name
    question = message.text.strip()
    if not question:
        bot.send_message(message.chat.id, 'Bạn cần nhập câu hỏi.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    formatted_question = f"Tôi là {first_name}, tôi muốn hỏi: {question}"
    add_to_chat_history(user_id, "Human", formatted_question)

    history = get_chat_history(user_id)
    full_prompt = f"{training_instruction}\n\nThời gian hiện tại: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n\nLịch sử trò chuyện:\n{format_chat_history(history)}\n\nHuman: {formatted_question}\nAI:"

    response = generate_response(full_prompt)
    if response:
        add_to_chat_history(user_id, "AI", response)
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, 'Dịch vụ không phản hồi, vui lòng thử lại sau.')

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    update_current_time()
    user_id = message.from_user.id
    
    if not check_spam(user_id):
        bot.reply_to(message, "Vui lòng đợi 10 giây trước khi gửi tin nhắn tiếp theo.")
        return
    
    file_id = message.photo[-1].file_id
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    with open('received_photo.png', 'wb') as new_file:
        new_file.write(downloaded_file)

    img = PIL.Image.open('received_photo.png')
    bot.send_chat_action(message.chat.id, 'typing')

    try:
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
        response = model.generate_content(["Đây là bức ảnh gì m?", img])
        add_to_chat_history(user_id, "Human", "Gửi một bức ảnh")
        add_to_chat_history(user_id, "AI", f"Mô tả ảnh: {response.text}")
        bot.send_message(message.chat.id, response.text)
    except Exception as e:
        bot.send_message(message.chat.id, 'Dịch vụ không phản hồi, vui lòng thử lại sau.')

@bot.message_handler(func=lambda message: message.chat.type == 'private' and not message.text.startswith('/'))
def handle_private_message(message):
    update_current_time()
    user_id = message.from_user.id
    
    if not check_spam(user_id):
        bot.reply_to(message, "Vui lòng đợi 10 giây trước khi gửi tin nhắn tiếp theo.")
        return
    
    first_name = message.from_user.first_name
    question = message.text.strip()
    if not question:
        bot.send_message(message.chat.id, 'Bạn cần nhập câu hỏi.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    formatted_question = f"Tôi là {first_name}, tôi muốn hỏi: {question}"
    add_to_chat_history(user_id, "Human", formatted_question)

    history = get_chat_history(user_id)
    full_prompt = f"{training_instruction}\n\nThời gian hiện tại: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n\nLịch sử trò chuyện:\n{format_chat_history(history)}\n\nHuman: {formatted_question}\nAI:"

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