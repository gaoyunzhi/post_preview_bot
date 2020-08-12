def oneTimeCleanSubscriber():
	for chat_id in list(subscription.sub.keys()):
		try:
			r = tele.bot.send_message(chat_id, 'test')
			r.delete()
		except:
			del subscription.sub[chat_id]
	subscription.save()