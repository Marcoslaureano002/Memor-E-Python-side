#!/usr/bin/python
# -*- coding:utf-8 -*-
import sys
import os
picdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'pic')
libdir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

import logging
from waveshare_epd import epd7in5_V2
import time
from PIL import Image,ImageDraw,ImageFont
import firebase_admin
import google.cloud
from firebase_admin import credentials, firestore
import time
import traceback
import textwrap


def draw_multiple_line_text(image, text, font, text_color, text_start_height):
 
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    y_text = text_start_height
    lines = textwrap.wrap(text, width=15)
    for line in lines:
        line_width, line_height = font.getsize(line)
        draw.text(((image_width - line_width) / 2, y_text), 
                  line, font=font, fill=text_color)
        y_text += line_height

logging.basicConfig(level=logging.DEBUG)

global displayedMessage
displayedMessage = ""

try:
    logging.info("epd7in5_V2 Demo")
    epd = epd7in5_V2.EPD()
    
    logging.info("init and Clear")
    epd.init()
    epd.Clear()
    print('Initializing Firestore connection...')
    # Credentials and Firebase App initialization. Always required
    firCredentials = credentials.Certificate("serviceAccountKey.json")
    firApp = firebase_admin.initialize_app(firCredentials)

    # Get access to Firestore
    db = firestore.client()
    print('Connection initialized')

    lastMessage = ""
    lastMessageTime = 0


    def on_snapshot(doc_snapshot, changes, read_time):
        global lastMessage, lastMessageTime
        for doc in doc_snapshot:
            doc_dict = doc.to_dict()
            if lastMessage == "":
                lastMessage = doc_dict['message']
                lastMessageTime = doc_dict['time']
                SentBy = doc_dict['sendBy']
            elif (doc_dict['time'] > lastMessageTime) & (doc_dict['message'] != lastMessage):
                lastMessage = doc_dict['message']
                lastMessageTime = doc_dict['time']
                SentBy = doc_dict['sendBy']

        displayedMessage = lastMessage
        stringLength = len(displayedMessage)
        print(stringLength)
        sender = SentBy
        print(sender)
        logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()
        
        logging.info("init and Clear")
        epd.init()
        epd.Clear()
        
        

        # Drawing on the Horizontal image 
        logging.info("1.Drawing on the Horizontal image...")
        
        image = Image.new('1', (epd.width, epd.height), color = 255)
        draw = ImageDraw.Draw(image)
        if 0<stringLength<6:
            fontsize = 275
        elif 5<stringLength<8:
            fontsize = 220
        elif 7<stringLength<10:
            fontsize = 170
        elif 9<stringLength<12:
            fontsize = 150
        elif stringLength == 12:
            fontsize = 125
        elif stringLength == 13:
            fontsize = 120
        elif stringLength == 14:
            fontsize = 120
        else:
            fontsize = 120
        
        print(fontsize)
        #fontsize = 125 #starting font size
        text_color = 0
        text_start_height = 10
        fnt = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), fontsize)
        fnt36 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 36)
        draw_multiple_line_text(image, displayedMessage, fnt, text_color, text_start_height)
        draw.text((epd.width-300, epd.height-45), 'From, ' + sender, font = fnt36, fill = 0)
        epd.display(epd.getbuffer(image))
        time.sleep(2)


    doc_ref = db.collection('chatRoom').document('admin_test').collection('chats')
    doc_watch = doc_ref.on_snapshot(on_snapshot)

    # Keep the app running
    while True:
        time.sleep(1)
   ## print('processing...')
        
    
except IOError as e:
    logging.info(e)
    
except KeyboardInterrupt:    
    logging.info("ctrl + c:")
    epd7in5_V2.epdconfig.module_exit()
    exit()
