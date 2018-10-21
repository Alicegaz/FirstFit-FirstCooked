import telebot
from telebot import types
import requests

TOKEN = "584026500:AAGwpFl-1a8GXfIt_2lvBaHU3ZPfjqSwG1o"
bot = telebot.TeleBot(TOKEN)

SPEECH_RECOGNITION_MESSAGE = 'I\'m recognizing your speech, please wait'


def get_help_markup():
    keyboard = types.InlineKeyboardMarkup()
    button_list = [
        types.InlineKeyboardButton("Track your children", callback_data='track_children'),
        types.InlineKeyboardButton("Talk to bank", callback_data='talk_to_bank'),
        types.InlineKeyboardButton("Write developers", callback_data='ask_coders')
    ]

    [keyboard.add(callback_button) for callback_button in button_list]

    return keyboard


@bot.message_handler(commands=['start', 'help', 'about'])
def handle_start(message):
    bot.send_message(chat_id=message.chat.id,
                     text='HELLO',
                     parse_mode='MARKDOWN', reply_markup=get_help_markup())


@bot.message_handler(content_types=['voice'])
def handle_audio(message):
    current_chat_id = message.chat.id

    bot.send_message(chat_id=current_chat_id,
                     text=SPEECH_RECOGNITION_MESSAGE)

    file_info = bot.get_file(message.voice.file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))

    # TODO: Call Google Cloud speech recognition API
    # response = requests.post(
    #     YANDEX_SPEECH_KIT_URL,
    #     data=file.content,
    #     headers={'Content-Type': 'audio/ogg;codecs=opus'})

    # TODO: let the user see what happend with his speech
    # print("voice:", recognized_text)
    # if recognized_text is not None:
    #     text = 'If I\'m right you said: *{}*'.format(recognized_text)
    # else:
    #     text = 'I don\'t understand you, please say more clearly'

    # bot.send_message(chat_id=current_chat_id, text=text,
    #                  parse_mode='MARKDOWN')

    # if recognized_text is not None:
        # TODO: call sentiment analysis model to predict the satisfaction
        # TODO: send something to user
        # bot.send_message(chat_id=current_chat_id,
        #                  text=text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        current_chat_id = call.message.chat.id
        markup = get_help_markup()
        if call.data == "track_children":
            # TODO: return a link to the web service
            send_text = "Put real text here 1"
        elif call.data == "talk_to_bank":
            # TODO: Start voice message dialog
            send_text = "Put real text here 2"

        elif call.data == "ask_coders":
            # TODO: return our contacts
            send_text = "Put real text here 3"
        else:
            send_text = "Unknown callback, sorry"

        if call.data in ['track_children', 'talk_to_bank', 'ask_coders']:
            s = requests.Session()
            s.get('https://api.telegram.org/bot{0}/deletemessage?message_id={1}&chat_id={2}'.format( \
            TOKEN, call.message.message_id, current_chat_id))
        bot.send_message(chat_id=current_chat_id,
            text=send_text, parse_mode='MARKDOWN',
            reply_markup=markup)


bot.polling(none_stop=False, interval=0, timeout=40)
