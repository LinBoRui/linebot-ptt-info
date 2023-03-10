import os

from linebot import LineBotApi
from linebot.models import TextSendMessage, ImageSendMessage, TemplateSendMessage, ButtonsTemplate, CarouselTemplate, MessageAction, URIAction, CarouselColumn


channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
line_bot_api = LineBotApi(channel_access_token)


def send_text_message(reply_token, text):
    line_bot_api.reply_message(reply_token, TextSendMessage(text=text))
    return "OK"


def send_image_message(reply_token, url):
    line_bot_api.reply_message(reply_token, ImageSendMessage(original_content_url=url, preview_image_url=url))
    return "OK"


def send_button_message(reply_token, title, text, buttons):
    actions = []
    for button in buttons:
        actions.append(MessageAction(label=button['label'], text=button['text']))
    line_bot_api.reply_message(reply_token, TemplateSendMessage(alt_text=title, template=ButtonsTemplate(title=title, text=text, actions=actions)))
    return "OK"


def send_button_url_message(reply_token, title, text, buttons):
    actions = []
    print(buttons)
    for button in buttons:
        actions.append(URIAction(label=button['label'], uri=button['url']))
    line_bot_api.reply_message(reply_token, TemplateSendMessage(alt_text=title, template=ButtonsTemplate(title=title, text=text, actions=actions)))
    return "OK"


def send_carousel_message(reply_token, labels):
    actions = []
    columns = []
    page = 1
    for i in range(len(labels)):
        label = labels[i]
        if len(label) > 20:
            label = label[:17] + '...'
        actions.append(MessageAction(label=label, text=str(i+1)))
        if i % 3 == 2:
            columns.append(CarouselColumn(title=f'Page {page}', text='請選擇', actions=actions))
            actions = []
            if page == 10:
                break
            page += 1
    line_bot_api.reply_message(reply_token, TemplateSendMessage(alt_text='請選擇文章', template=CarouselTemplate(columns=columns)))
    return "OK"
