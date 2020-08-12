#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telegram_util import log_on_fail, removeOldFiles, getLogStr, isInt
import album_sender
from db import subscription, existing, weibo_name
import threading
import weibo_2_album
from command import setupCommand
from common import debug_group, tele
import weiboo
import random
from filter import passFilter
import time

processed_channels = set()

def shouldProcess(channel, card, key):
	if channel.id in processed_channels:
		return False
	if not passFilter(channel, card, key):
		return False
	whash = weiboo.getHash(card) + str(channel.id)
	if not existing.add(whash):
		return False
	processed_channels.add(channel.id)
	return True

# a hack, we can fetch the single item again, but weibo will 
# be unhappy about the frequent calls
def removeSeeMore(result): 
	pivot = '[全文](/status/'
	result.cap = result.cap.split(pivot)[0]

def process(key):
	channels = subscription.channels(tele.bot, key)
	search_result = weiboo.search(key, force_cache=True)
	if isInt(key): # backfill, can remove this part after 7/17
		result = weiboo.searchUser(key)
		if result:
			weibo_name.update(result[0], result[1])
	if not search_result:
		print('no search result', key)
	for url, card in search_result:
		result = None
		for channel in channels:
			if not shouldProcess(channel, card, key):
				continue
			print(url, channel.id, channel.username)
			if not result:
				time.sleep(60)
				result = weibo_2_album.get(url, card['mblog'])
				removeSeeMore(result)
			try:
				album_sender.send_v2(channel, result)
			except Exception as e:
				debug_group.send_message(getLogStr(channel.username, channel.id, url, e))
				raise e

@log_on_fail(debug_group)
def loopImp():
	removeOldFiles('tmp', day=0.1) # video could be very large
	global processed_channels 
	processed_channels = set()
	for key in subscription.subscriptions():
		if random.random() > 0.05:
			continue
		process(key)

def loop():
	loopImp()
	threading.Timer(60 * 10, loop).start() 

if __name__ == '__main__':
	threading.Timer(1, loop).start() 
	setupCommand(tele.dispatcher)
	tele.start_polling()
	tele.idle()