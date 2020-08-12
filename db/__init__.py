import plain_db
from telegram_util import isInt
import yaml
import weiboo

existing = plain_db.loadKeyOnlyDB('existing')
blocklist = plain_db.loadKeyOnlyDB('blocklist')
popularlist = plain_db.loadKeyOnlyDB('popularlist')
weibo_name = plain_db.load('weibo_name', isIntValue=False)

def searchUser(text):
	for key, value in weibo_name.items.items():
		if text in [key, value]:
			return key, value
	result = weiboo.searchUser(text)
	if result:
		weibo_name.update(result[0], result[1])
	return result

def clearText(text):
	text = text.split('?')[0]
	return text.strip('/').split('/')[-1]

def getMatches(text):
	if not text:
		return []
	text = clearText(text)
	user = searchUser(text)
	if user:
		return user
	return [text]

def getDisplay(item):
	display_name = weibo_name.get(item)
	if isInt(item) and not display_name:
		display_name = item
	if display_name:
		return '[%s](https://m.weibo.cn/u/%s)' % (display_name, item)
	return item

class Subscription(object):
	def __init__(self):
		with open('db/subscription') as f:
			self.sub = yaml.load(f, Loader=yaml.FullLoader)

	def add(self, chat_id, text):
		matches = getMatches(text)
		if not matches:
			return
		for text in matches:
			if text not in self.sub.get(chat_id, []):
				self.sub[chat_id] = self.sub.get(chat_id, []) + [text]
				self.save()
				return

	def remove(self, chat_id, text):
		matches = getMatches(text)
		if not matches:
			return
		for text in matches:
			if text in self.sub.get(chat_id, []):
				self.sub[chat_id].remove(text)
				self.save()
				return

	def get(self, chat_id):
		result = [getDisplay(item) for item in self.sub.get(chat_id, [])]
		result.sort()
		return '当前订阅：' + ' '.join(result)

	def subscriptions(self):
		result = set()
		for chat_id in self.sub:
			for item in self.sub.get(chat_id, []):
				if 'filter' not in item.lower():
					result.add(item)
		return result

	def _channels(self, bot, text):
		for chat_id in self.sub:
			if text in self.sub.get(chat_id, []):
				try:
					yield bot.get_chat(chat_id)
				except:
					...

	def channels(self, bot, text):
		return list(self._channels(bot, text))

	# by default, we don't do filter
	def filterOnUser(self, chat_id):
		return 'filterOnUser' in self.sub.get(chat_id, [])

	# by default, we do filter
	def filterOnKey(self, chat_id):
		return 'noFilterOnKey' not in self.sub.get(chat_id, [])

	def hasMasterFilter(self, chat_id):
		return 'hasMasterFilter' in self.sub.get(chat_id, [])

	def save(self):
		with open('db/subscription', 'w') as f:
			f.write(yaml.dump(self.sub, sort_keys=True, indent=2, allow_unicode=True))

subscription = Subscription()