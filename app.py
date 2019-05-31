from __future__ import unicode_literals

import random
import time
from datetime import timedelta, datetime
from pymongo import MongoClient

#ref: http://twstock.readthedocs.io/zh_TW/latest/quickstart.html#id2
import twstock

import matplotlib
matplotlib.use('Agg') # ref: https://matplotlib.org/faq/howto_faq.html
import matplotlib.pyplot as plt
import pandas as pd

from imgurpython import ImgurClient

from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

app = Flask(__name__)


channel_secret_8 = '7da2efd742498fe6df95553cce9f5fea'
channel_access_token_8 = 'EkhtS4e2iaJeWO0z3U0XWJKSdYhBX8vA5qudTCqd0JdbWjQxuNvBIFj9UvdDeO66cUkH/0RxF73abRp7cYS0j9CahVtXZ+NTpg4EqJhfm3lPze+iap2iodYg3V52vTydfZbMAfIt1umrv9e2BwTKFgdB04t89/1O/w1cDnyilFU='
line_bot_api_8 = LineBotApi(channel_access_token_8)
parser_8 = WebhookParser(channel_secret_8)

@app.route("/callback_yangbot8", methods=['POST'])
def callback_yangbot8():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser_8.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue

        text=event.message.text
        #userId = event['source']['userId']
        userId = 'U8b3aec5a3147090923fb0cd0a7688143'
        if(text.lower()=='me'):
            content = str(event.source.user_id)

            line_bot_api_8.reply_message(
                event.reply_token,
                TextSendMessage(text=content)
            )
        elif(text.lower() == 'profile'):
            profile = line_bot_api_8.get_profile(event.source.user_id)
            my_status_message = profile.status_message
            if not my_status_message:
                my_status_message = '-'
            line_bot_api_8.reply_message(
                event.reply_token, [
                    TextSendMessage(
                        text='Display name: ' + profile.display_name
                    ),
                    TextSendMessage(
                        text='picture url: ' + profile.picture_url
                    ),
                    TextSendMessage(
                        text='status_message: ' + my_status_message
                    ),
                ]
            )

        elif(text.startswith('#')):
            text = text[1:]
            content = ''

            stock_rt = twstock.realtime.get(text)
            my_datetime = datetime.fromtimestamp(stock_rt['timestamp']+8*60*60)
            my_time = my_datetime.strftime('%H:%M:%S')

            content += '%s (%s) %s\n' %(
                stock_rt['info']['name'],
                stock_rt['info']['code'],
                my_time)
            content += '現價: %s / 開盤: %s\n'%(
                stock_rt['realtime']['latest_trade_price'],
                stock_rt['realtime']['open'])
            content += '最高: %s / 最低: %s\n' %(
                stock_rt['realtime']['high'],
                stock_rt['realtime']['low'])
            content += '量: %s\n' %(stock_rt['realtime']['accumulate_trade_volume'])

            stock = twstock.Stock(text)#twstock.Stock('2330')
            content += '-----\n'
            content += '最近五日價格: \n'
            price5 = stock.price[-5:][::-1]
            date5 = stock.date[-5:][::-1]
            for i in range(len(price5)):
                #content += '[%s] %s\n' %(date5[i].strftime("%Y-%m-%d %H:%M:%S"), price5[i])
                content += '[%s] %s\n' %(date5[i].strftime("%Y-%m-%d"), price5[i])
                
            bfp = twstock.BestFourPoint(stock)
            content += bfp.best_four_point_to_buy()    # 判斷是否為四大買點
            #bfp.best_four_point_to_sell()   # 判斷是否為四大賣點
            #content += bfp.best_four_point()           # 綜合判斷

            line_bot_api_8.reply_message(
                event.reply_token,
                TextSendMessage(text=content)
            )

        elif(text.startswith('/')):
            text = text[1:]
            fn = '%s.png' %(text)
            stock = twstock.Stock(text)
            my_data = {'close':stock.close, 'date':stock.date, 'open':stock.open}
            df1 = pd.DataFrame.from_dict(my_data)

            df1.plot(x='date', y='close')
            plt.title('[%s]' %(stock.sid))
            plt.savefig(fn)
            plt.close()

            # -- upload
            # imgur with account: your.mail@gmail.com
            client_id = '068c8dc4e9828e2'
            client_secret = 'a84369ccc0eee86508b684c6472849a3d55b4c8f'

            client = ImgurClient(client_id, client_secret)
            print("Uploading image... ")
            image = client.upload_from_path(fn, anon=True)
            print("Done")

            url = image['link']
            image_message = ImageSendMessage(
                original_content_url=url,
                preview_image_url=url
            )

            line_bot_api_8.reply_message(
                event.reply_token,
                image_message
                )

        elif(text.startswith('?')):
            text = text[1:]
            content = ''
            sinfo = twstock.codes.codes[text]
            
            content += sinfo.name
            line_bot_api_8.reply_message(
                event.reply_token,
                TextSendMessage(text=content)
            )           
            
    return 'OK'


@app.route("/", methods=['GET'])
def basic_url():
    return 'OK'


if __name__ == "__main__":
    app.run()
    
#===================================================
#   stock bot
#===================================================
#@app.route("/", methods=['GET'])
#def basic_url():
#    return 'OK'
#
#if __name__ == "__main__":
#    app.run()
