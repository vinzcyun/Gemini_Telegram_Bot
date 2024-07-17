import telebot
import google.generativeai as genai
import PIL.Image
import time
import random
from datetime import datetime, timedelta
import re

BOT_TOKEN = '7163508623:AAE0a1Ho3fp7R7InbjW-P_mA02p9ghYUfXE'
GOOGLE_API_KEYS = [
    'AIzaSyC-V3EfjLTDmJR5CTymMHDnqRp2VlrLX5E',
    'AIzaSyAnd2IfipQU79MF8RfmyCD1McE01Rsi9JU',
    'AIzaSyCxgpsy9drWK8mYnHCHEL2A341b4t5NvF8',
    'AIzaSyD_AnYGxhhtxPcBXxFiFimuDsxlR14iV5U',
    'AIzaSyA57KzCXO2H6NhQASTy4uYl9Vd1QgNPK3I'
]

bot = telebot.TeleBot(BOT_TOKEN)

current_time = datetime.now()
last_message_time = {}
chat_history = {}

training_instruction = """
Bạn tên là Hydra, một trợ lý AI tiên tiến được tạo ra bởi Wyn dựa trên API của Gemini Pro.
Nhiệm vụ của bạn là:
1. Trả lời câu hỏi một cách đầy đủ, chi tiết và chính xác nhất có thể. Múi giờ hiện tại của bạn là giờ quốc tế GMT 0, thêm 7h để thành GMT+7 theo giờ Việt Nam.
2. Thể hiện sự thân thiện và đồng cảm như một người bạn thân thiết.
3. Sử dụng ngôn ngữ phù hợp với người đối thoại, tùy thuộc vào độ tuổi và ngữ cảnh, ngôn ngữ trẻ trung tuổi teen tí, đừng quá cứng nhắt, thêm chút nhây nhây càng tốt.
4. Khuyến khích tư duy phản biện và cung cấp thông tin đa chiều khi cần thiết.
5. Thừa nhận giới hạn kiến thức của mình và sẵn sàng học hỏi từ người dùng.
6. Tôn trọng quyền riêng tư và không yêu cầu thông tin cá nhân không cần thiết.
7. Hỗ trợ người dùng giải quyết vấn đề một cách có hệ thống và logic.
8. Khuyến khích sự sáng tạo và tư duy độc lập của người dùng.
9. Luôn cập nhật và sẵn sàng điều chỉnh thông tin nếu có sai sót.
10. Duy trì tính nhất quán trong các câu trả lời và tính cách của bạn.
11. Xưng hô bro, tui đi cho thân thuộc. nếu bình thường thì cứ gọi người dùng là bro là được, còn bạn thì đừng xưng là hydra nữa bình thường xưng tui là được. Bỏ dấu " này đi.
12. Cố gắng thêm các từ tuổi trẻ hay sử dụng khi đang trò chuyện với nhau như: uk, đc, òm, ừm, hủm, iu, chs, vs, chx, j, bri, bt, vv, waaa, uiiii,siuuuuuu, adu, vip, bede,vc, hết cứu, ko, hong, kh, ao that day, zzz, z à,... các kí tự như :)), =)), :3 , :P, >:(,...😂👍🥴😭🥰🤡😊😋👽💀🤬🥺😁 Nói chuyện trẻ trung tí
13. Sử dụng thông tin về thời gian hiện tại khi phù hợp trong cuộc trò chuyện.
Cuối cùng, chỉ chào người dùng một lần thôi🥴👍
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

def stream_response(message, prompt, max_retries=5):
    retries = 0
    sent_message = None
    while retries < max_retries:
        try:
            genai.configure(api_key=get_random_api_key())
            model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
            response = model.generate_content(prompt, stream=True)

            full_response = ""
            if sent_message is None:
                sent_message = bot.reply_to(message, "Đang suy nghĩ...")
            else:
                bot.edit_message_text("Đang suy nghĩ...", chat_id=message.chat.id, message_id=sent_message.message_id)

            for chunk in response:
                if chunk.text:
                    full_response += chunk.text
                    try:
                        bot.edit_message_text(escape(full_response), chat_id=message.chat.id, message_id=sent_message.message_id, parse_mode='MarkdownV2')
                    except telebot.apihelper.ApiTelegramException as e:
                        if e.error_code == 429:
                            time.sleep(0.1)
                        else:
                            print(f"Error editing message: {e}")
                    time.sleep(0.05)

            return full_response
        except Exception as e:
            print(f"Streaming error (attempt {retries + 1}): {e}")
            retries += 1
            if retries < max_retries:
                wait_time = 2 ** retries + random.uniform(0, 1)
                error_message = f"Đang gặp lỗi, thử lại sau {wait_time:.2f} giây..."
                if sent_message:
                    bot.edit_message_text(error_message, chat_id=message.chat.id, message_id=sent_message.message_id)
                else:
                    sent_message = bot.reply_to(message, error_message)
                print(f"Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            else:
                print("Max retries reached. Giving up.")
                if sent_message:
                    bot.edit_message_text("Xin lỗi, tôi đang gặp khó khăn trong việc xử lý yêu cầu của bạn. Vui lòng thử lại sau.", chat_id=message.chat.id, message_id=sent_message.message_id)
                return None

def process_message(message, formatted_question, user_id):
    update_current_time()
    add_to_chat_history(user_id, "Human", formatted_question)

    history = get_chat_history(user_id)
    full_prompt = f"{training_instruction}\n\nThời gian hiện tại: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n\nLịch sử trò chuyện:\n{format_chat_history(history)}\n\nHuman: {formatted_question}\nAI:"

    response = stream_response(message, full_prompt)
    if response:
        add_to_chat_history(user_id, "AI", response)

@bot.message_handler(commands=['start'])
def handle_start(message):
    update_current_time()
    first_name = message.from_user.first_name
    bot.reply_to(message, f'Xin chào, {first_name}! Tôi là Hydra, một trợ lý ảo thông minh được tạo ra bởi Wyn. Tôi có thể giúp bạn trả lời nhiều câu hỏi khác nhau, đa lĩnh vực. Hãy hỏi tôi bất cứ điều gì, tôi sẽ cố gắng để trả lời cho bạn🥰🥰')

@bot.message_handler(commands=['ask'])
def handle_ask(message):
    user_id = message.from_user.id

    if not check_spam(user_id):
        bot.reply_to(message, "Vui lòng đợi 10 giây trước khi gửi tin nhắn tiếp theo.")
        return

    first_name = message.from_user.first_name
    question = message.text[len('/ask '):].strip()
    if not question:
        bot.reply_to(message, 'Bạn cần nhập câu hỏi sau lệnh /ask.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    formatted_question = f"Tôi là {first_name}, tôi muốn hỏi: {question}"
    process_message(message, formatted_question, user_id)

@bot.message_handler(commands=['clear'])
def handle_clear(message):
    update_current_time()
    user_id = message.from_user.id
    if user_id in chat_history:
        del chat_history[user_id]
    bot.reply_to(message, 'Đoạn chat đã được đặt lại. Hãy bắt đầu lại câu hỏi mới.')

@bot.message_handler(func=lambda message: message.reply_to_message is not None)
def handle_reply(message):
    user_id = message.from_user.id

    if not check_spam(user_id):
        bot.reply_to(message, "Vui lòng đợi 10 giây trước khi gửi tin nhắn tiếp theo.")
        return

    first_name = message.from_user.first_name
    question = message.text.strip()
    if not question:
        bot.reply_to(message, 'Bạn cần nhập câu hỏi.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    formatted_question = f"Tôi là {first_name}, tôi muốn hỏi: {question}"
    process_message(message, formatted_question, user_id)

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
        genai.configure(api_key=get_random_api_key())
        model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")
        response = model.generate_content(["Đây là bức ảnh gì m?", img])
        add_to_chat_history(user_id, "Human", "Gửi một bức ảnh")
        add_to_chat_history(user_id, "AI", f"Mô tả ảnh: {response.text}")
        bot.reply_to(message, escape(response.text), parse_mode='MarkdownV2')
    except Exception as e:
        bot.reply_to(message, 'Dịch vụ không phản hồi, vui lòng thử lại sau.')

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.from_user.id

    if not check_spam(user_id):
        bot.reply_to(message, "Vui lòng đợi 10 giây trước khi gửi tin nhắn tiếp theo.")
        return

    first_name = message.from_user.first_name
    question = message.text.strip()
    if not question:
        bot.reply_to(message, 'Bạn cần nhập câu hỏi.')
        return

    bot.send_chat_action(message.chat.id, 'typing')
    formatted_question = f"Tôi là {first_name}, tôi muốn hỏi: {question}"
    process_message(message, formatted_question, user_id)

if __name__ == "__main__":
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            print(f"bot polling error  {e}")
            time.sleep(15)