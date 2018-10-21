from sent_analysis.sentiment import get_sentiment

import telebot
from telebot import types

import base64
import requests
import json

TOKEN = "584026500:AAGwpFl-1a8GXfIt_2lvBaHU3ZPfjqSwG1o"
YANDEX_SPEECH_KIT_URL = 'http://asr.yandex.net/asr_xml?uuid=01ae13cb744628b58fb536d496daa1e7&key=58766f45-93bd-4031' \
                        '-abf7-ded3ba87268c&topic=queries'
API_ENDPOINT = "https://speech.googleapis.com/v1/speech:recognize"
WEBAPP_ADDRESS = 'http://35.231.236.148:8000/'
bot = telebot.TeleBot(TOKEN)

SPEECH_RECOGNITION_MESSAGE = 'I\'m recognizing your speech, please wait...'
CALL_ENDED_SPEECH1 = 'Your call has been ended.'
CALL_ENDED_SPEECH2 = 'The overall sentiment during the call was ranked as {:.1f} positive'
CALL_ENDED_SPEECH3 = '`Your experience is recorded unanimously to influence the positive changes in the strategy of ' \
                     'our company to provide you more profitable offers and make the services better!` '
COMPANY_QUESTIONS = [
    ('Good afternoon, {}. You have been requesting a call from the Sunshine telecom company to learn more about '
     'choosing your voice and internet plans. We can offer you Mint Mobile 3 Month Plan with 4GB of the Internet in '
     'Hungary and 100min of calls to all regions of Hungary for just 21 EUROS per month. Are you interested?',
     './bot/audio/audio11.m4a'),
    ('Actually, for you, we also have a personal promotional offer as you are our regular client. We can suggest you '
     'Sprint Unlimited Plus Plan with 40 GB of the internet, unlimited calls and SMS across Hungary for 23 Euros per '
     'month. Are you interested in it?',
     './bot/audio/audio22.m4a'),
    ('Thank you for your responses! We will come back to you soon!',
     './bot/audio/audio33.m4a')
]

user_states = {}


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
        types.InlineKeyboardButton("Talk to telecom company", callback_data='talk_to_bank'),
        types.InlineKeyboardButton("Just have fun with sentiment analysis", callback_data='sent_analysis'),
        types.InlineKeyboardButton("Write developers", callback_data='ask_coders')
    ]

    [keyboard.add(callback_button) for callback_button in button_list]

    return keyboard


def clear_user_session(user_states, chat_id):
    user_states[chat_id]['mode'] = 'default'
    user_states[chat_id]['dialog_idx'] = 0
    user_states[chat_id]['pos_probas'] = []


def send_user_satisfaction_result(current_chat_id, positive_proba):
    if positive_proba <= 0.5:
        text = '*NEGATIVE*: {:.1f}%'.format((1. - positive_proba) * 100)
        bot.send_message(chat_id=current_chat_id, text=text, parse_mode='MARKDOWN')
        bot.send_sticker(current_chat_id, 'CAADAgADTQQAAmvEygrl-lSot7bymgI')
    else:
        text = '*POSITIVE*: {:.1f}%'.format((positive_proba * 100))
        bot.send_message(chat_id=current_chat_id, text=text, parse_mode='MARKDOWN')
        bot.send_sticker(current_chat_id, 'CAADAgADiQEAAj-VzAqgZEexapUBTQI')


@bot.message_handler(commands=['start', 'help', 'about'])
def handle_start(message):
    current_chat_id = message.chat.id
    if current_chat_id not in user_states:
        user_states[current_chat_id] = {'mode': 'default'}

    bot.send_message(chat_id=current_chat_id,
                     text='Welcome to the Intelligent Voice solutions for the Nokia Mobile Network platform',
                     parse_mode='MARKDOWN', reply_markup=get_help_markup())


@bot.message_handler(func=lambda message: True)
def handle_text(message):
    current_chat_id = message.chat.id

    if current_chat_id in user_states:
        if user_states[current_chat_id]['mode'] == 'talk':
            bot.send_message(chat_id=message.chat.id,
                             text='I see you are tired of my quizzes. You can go to another section',
                             parse_mode='MARKDOWN', reply_markup=get_help_markup())
            user_states[current_chat_id]['mode'] = 'default'
        else:
            bot.send_message(chat_id=message.chat.id,
                             text='You can go to one of the sections from buttons',
                             parse_mode='MARKDOWN', reply_markup=get_help_markup())
    else:
        user_states[current_chat_id] = {'mode': 'default'}
        bot.send_message(chat_id=message.chat.id,
                         text='You can go to one of the sections from buttons',
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

    if user_states[current_chat_id]['mode'] == 'talk':
        if recognized_text is not None:
            user_states[current_chat_id]['dialog_idx'] += 1
            positive_proba = get_sentiment(recognized_text)
            user_states[current_chat_id]['pos_probas'].append(positive_proba)
            if positive_proba <= 0.5:
                text = '*NEGATIVE*: {:.1f}%'.format((1. - positive_proba) * 100)
                bot.send_message(chat_id=current_chat_id, text=text, parse_mode='MARKDOWN')
            else:
                text = '*POSITIVE*: {:.1f}%'.format((positive_proba * 100))
                bot.send_message(chat_id=current_chat_id, text=text, parse_mode='MARKDOWN')

            # End of the talk
            if user_states[current_chat_id]['dialog_idx'] >= len(COMPANY_QUESTIONS) - 1:
                avg_sent = sum(user_states[current_chat_id]['pos_probas']) /\
                           len(user_states[current_chat_id]['pos_probas'])
                bot.send_message(chat_id=current_chat_id, text=CALL_ENDED_SPEECH1, parse_mode='MARKDOWN')
                audio = open(COMPANY_QUESTIONS[-1][1], 'rb')
                bot.send_audio(current_chat_id, audio)
                bot.send_message(chat_id=current_chat_id, text=CALL_ENDED_SPEECH2.format(avg_sent),
                                 parse_mode='MARKDOWN')
                bot.send_message(chat_id=current_chat_id, text=CALL_ENDED_SPEECH3,
                                 parse_mode='MARKDOWN', reply_markup=get_help_markup())

                send_user_satisfaction_result(current_chat_id, avg_sent)
                clear_user_session(user_states, current_chat_id)
            # The talk continues
            else:
                bot.send_message(chat_id=current_chat_id,
                                 text=COMPANY_QUESTIONS[user_states[current_chat_id]['dialog_idx']][0],
                                 parse_mode='MARKDOWN')
                audio = open(COMPANY_QUESTIONS[user_states[current_chat_id]['dialog_idx']][1], 'rb')
                bot.send_audio(current_chat_id, audio)
    else:
        if recognized_text is not None:
            positive_proba = get_sentiment(recognized_text)
            send_user_satisfaction_result(current_chat_id, positive_proba)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        current_chat_id = call.message.chat.id
        username = call.message.from_user.first_name

        markup = get_help_markup()
        if call.data == "track_children":
            send_text = "Open the link to see the map with location of you child\n{}" \
                .format(WEBAPP_ADDRESS)
            bot.send_message(chat_id=current_chat_id,
                             text=send_text, parse_mode='MARKDOWN',
                             reply_markup=markup)
        elif call.data == "talk_to_bank":
            send_text = "In the next few dialog sections I will show you speeches from some telecom company and you " \
                        "should answer on them by voice, so I can recognize you and make some sensitivity analysis. " \
                        "Wait fot the last message to see the result."
            user_states[current_chat_id]['mode'] = 'talk'
            user_states[current_chat_id]['dialog_idx'] = 0
            user_states[current_chat_id]['pos_probas'] = []
            bot.send_message(chat_id=current_chat_id,
                             text=send_text, parse_mode='MARKDOWN')
            bot.send_message(chat_id=current_chat_id,
                             text=COMPANY_QUESTIONS[0][0].format(username), parse_mode='MARKDOWN')
            audio = open(COMPANY_QUESTIONS[0][1], 'rb')
            bot.send_audio(current_chat_id, audio)

        elif call.data == "ask_coders":
            clear_user_session(user_states, current_chat_id)
            send_text = "In case of any questions don\'t hesitate to ask @AliceGazizullina or @vladvin"
            bot.send_message(chat_id=current_chat_id,
                             text=send_text, parse_mode='MARKDOWN',
                             reply_markup=markup)
        elif call.data == 'sent_analysis':
            clear_user_session(user_states, current_chat_id)
            send_text = "You switched to the default mode where you can send voice messages in order to get your " \
                        "sentiment analysis results"
            bot.send_message(chat_id=current_chat_id,
                             text=send_text, parse_mode='MARKDOWN',
                             reply_markup=markup)
        else:
            clear_user_session(user_states, current_chat_id)
            send_text = "Unknown callback, sorry. You can write developers"
            bot.send_message(chat_id=current_chat_id,
                             text=send_text, parse_mode='MARKDOWN',
                             reply_markup=markup)

        if call.data in ['track_children', 'talk_to_bank', 'ask_coders']:
            s = requests.Session()
            s.get('https://api.telegram.org/bot{0}/deletemessage?message_id={1}&chat_id={2}'
                  .format(TOKEN, call.message.message_id, current_chat_id))


if __name__ == '__main__':
    bot.polling(none_stop=False, interval=0, timeout=40)
