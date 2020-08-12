from telegram_util import matchKey, isInt
from db import subscription, blocklist, popularlist
import weiboo

def shouldApplyFilter(channel_id, key):
	if isInt(key):
		return subscription.filterOnUser(channel_id)
	return subscription.filterOnKey(channel_id)

def passKeyFilter(card):
	if matchKey(str(card), popularlist.items()):
		return weiboo.getCount(card) > 10000
	return weiboo.getCount(card) > 1000

def passMasterFilter(card):
	if matchKey(str(card), blocklist.items()):
		return False
	return weiboo.getCount(card) > 300

def tooOld(card): # will remove may be after 07-20
	created_at = card['mblog']['created_at']
	if len(created_at) != 5:
		return False
	return created_at <= '07-13'

def passFilter(channel, card, key):
	if tooOld(card): # for hash migration
		return False
	channel_id = channel.id
	if (subscription.hasMasterFilter(channel_id) and 
		not passMasterFilter(card)):
		return False
	if (shouldApplyFilter(channel_id, key) and 
		not passKeyFilter(card)):
		return False
	return True