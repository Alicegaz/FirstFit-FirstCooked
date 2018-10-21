from sent_analysis.sentiment import get_sentiment

import telebot
from telebot import types

import base64
import requests
import json

import xml.etree.ElementTree as etree

TOKEN = "584026500:AAGwpFl-1a8GXfIt_2lvBaHU3ZPfjqSwG1o"
YANDEX_SPEECH_KIT_URL = 'http://asr.yandex.net/asr_xml?uuid=01ae13cb744628b58fb536d496daa1e7&key=58766f45-93bd-4031' \
                        '-abf7-ded3ba87268c&topic=queries'
API_ENDPOINT = "https://speech.googleapis.com/v1/speech:recognize"
WEBAPP_ADDRESS = 'http://35.231.236.148:8000/'
bot = telebot.TeleBot(TOKEN)

SPEECH_RECOGNITION_MESSAGE = 'I\'m recognizing your speech, please wait...'


def speech_to_text(audio_content):
    API_KEY = "AIzaSyBwG6k68u2IpEP0rvWAD0Df0fnfEQjaZTY"
    headers = {'Content-type': 'application/json'}
    audio_json = {"config":
                      {"encoding": "OGG_OPUS", "sampleRateHertz": 16000,
                       "languageCode": "en-US", "enableWordTimeOffsets": False},
                  "audio": {"content": base64.b64encode(audio_content).decode('utf-8')}}
    params = {'key': API_KEY}
    rsp = requests.post(API_ENDPOINT, params=params, data=json.dumps(audio_json), headers=headers)

    try:
        rsp = json.loads(rsp.text)
        recognized_text = rsp['results'][0]['alternatives'][0]['transcript']
        return recognized_text
    except Exception:
        return None


def get_help_markup():
    keyboard = types.InlineKeyboardMarkup()
    button_list = [
        types.InlineKeyboardButton("Track your children", callback_data='track_children'),
        types.InlineKeyboardButton("Talk to bank", callback_data='talk_to_bank'),
        types.InlineKeyboardButton("Write developers", callback_data='ask_coders')
    ]

    [keyboard.add(callback_button) for callback_button in button_list]

    return keyboard


def parse_speech_kit_xml(xml_text):
    xml_root = etree.fromstring(xml_text)

    variant = xml_root.find('variant')
    if variant is not None:
        return variant.text

    return None


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

    recognized_text = speech_to_text(file.content)

    print('GOOGLE: {}'.format(recognized_text))
    if recognized_text is not None:
        text = 'If I\'m right you said: *{}*'.format(recognized_text)
    else:
        text = 'I don\'t understand you, please say more clearly'

    bot.send_message(chat_id=current_chat_id, text=text,
                     parse_mode='MARKDOWN')

    if recognized_text is not None:
        positive_proba = get_sentiment(recognized_text)
        if positive_proba <= 0.5:
            text = '*NEGATIVE*: {:.1f}%'.format((1. - positive_proba) * 100)
            bot.send_message(chat_id=current_chat_id, text=text, parse_mode='MARKDOWN')
            bot.send_sticker(current_chat_id, 'CAADAgADTQQAAmvEygrl-lSot7bymgI')
        else:
            text = '*POSITIVE*: {:.1f}%'.format((positive_proba * 100))
            bot.send_message(chat_id=current_chat_id, text=text, parse_mode='MARKDOWN')
            bot.send_sticker(current_chat_id, 'CAADAgADiQEAAj-VzAqgZEexapUBTQI')


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        current_chat_id = call.message.chat.id
        markup = get_help_markup()
        if call.data == "track_children":
            send_text = "Open the link to see the map with location of you child\n{}" \
                .format(WEBAPP_ADDRESS)
        elif call.data == "talk_to_bank":
            # TODO: Start voice message dialog
            send_text = "Put real text here 2"

        elif call.data == "ask_coders":
            send_text = "In case of any questions don\'t hesitate to ask @AliceGazizullina or @vladvin"
        else:
            send_text = "Unknown callback, sorry. You can write developers"

        if call.data in ['track_children', 'talk_to_bank', 'ask_coders']:
            s = requests.Session()
            s.get('https://api.telegram.org/bot{0}/deletemessage?message_id={1}&chat_id={2}'
                  .format(TOKEN, call.message.message_id, current_chat_id))
        bot.send_message(chat_id=current_chat_id,
                         text=send_text, parse_mode='MARKDOWN',
                         reply_markup=markup)


if __name__ == '__main__':
    bot.polling(none_stop=False, interval=0, timeout=40)
