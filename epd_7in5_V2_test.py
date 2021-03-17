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

logging.basicConfig(level=logging.DEBUG)
font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 190)
font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 75)
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
            elif (doc_dict['time'] > lastMessageTime) & (doc_dict['message'] != lastMessage):
                lastMessage = doc_dict['message']
                lastMessageTime = doc_dict['time']

        displayedMessage = lastMessage
        logging.info("epd7in5_V2 Demo")
        epd = epd7in5_V2.EPD()
        
        logging.info("init and Clear")
        epd.init()
        epd.Clear()

        font24 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 190)
        font18 = ImageFont.truetype(os.path.join(picdir, 'Font.ttc'), 75)

        # Drawing on the Horizontal image
        logging.info("1.Drawing on the Horizontal image...")
        Himage = Image.new('1', (epd.width, epd.height), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        draw.text((10, 175), displayedMessage, font = font24, fill = 0)
        epd.display(epd.getbuffer(Himage))
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
