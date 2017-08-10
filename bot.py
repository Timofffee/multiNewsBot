import libs.requests as requests
import libs.telebot as telebot
import time
import datetime
import re


TOKEN_TG = '' #TOKEN BOT TELEGRAM
TOKEN_VK = '' #ACCESS KEY VK
tg_channel = '@name' #chat in telegram
vk_group = '' #example 'vkapi' (vk.com/vkapi)
sticker_id = ['CAADAgADEgADuYK-DAwZdY5q1ZiJAg', 'CAADAgADEwADuYK-DC9fGK4AAfkdLQI'] #?? Stickers ?? (lol)


tg_bot = telebot.TeleBot(TOKEN_TG)

def send_message(chat, mess, reply_id = -1):
	try:
		im = 'https://api.telegram.org/bot{}/sendMessage'.format(TOKEN_TG)
		if reply_id > 0:
			r = requests.post(im, data = {'chat_id':chat, 'text':mess, 'reply_to_message_id':reply_id})
		else:
			r = requests.post(im, data = {'chat_id':chat, 'text':mess})
	except:
		print('Error getting updates')
		return False	

	if not r.status_code == 200: return False 
	if not r.json()['ok']: return False

def send_photo(chat, url):
	try:
		im = 'https://api.telegram.org/bot{}/sendPhoto'.format(TOKEN_TG)
		r = requests.post(im, data = {'chat_id':chat, 'photo':url})
	except:
		print('Error getting updates')
		return False	

	if not r.status_code == 200: 
		print('Error. Can\'t send photo')
		return False 
	if not r.json()['ok']: return False

def send_video(chat, url):
	try:
		im = 'https://api.telegram.org/bot{}/sendVideo'.format(TOKEN_TG)
		r = requests.post(im, data = {'chat_id':chat, 'video':url})
	except:
		print('Error getting updates')
		return False	

	if not r.status_code == 200: 
		print('Error. Can\'t send video')
		return False 
	if not r.json()['ok']: return False

def send_document(chat, title, url):
	try:
		file = requests.get(url)
	except:
		print('Error getting file')

	try:
		headers = 'Content-Type: multipart/form-data'
		im = 'https://api.telegram.org/bot{}/sendDocument'.format(TOKEN_TG)
		r = requests.post(im, data = {'chat_id':chat}, files = {'document': (title, file.content)})
	except:
		print('Error getting updates')
		return False	

	if not r.status_code == 200: 
		print('Error. Can\'t send doc')
		return False
	if not r.json()['ok']: return False

def send_sticker(chat, file_id):
	try:
		im = 'https://api.telegram.org/bot{}/sendSticker'.format(TOKEN_TG)
		r = requests.post(im, data = {'chat_id':chat, 'sticker':file_id})
	except:
		print('Error getting updates')
		return False	

	if not r.status_code == 200: 
		print('Error. Can\'t send sticker')
		return False 
	if not r.json()['ok']: return False

def get_short_link(link):
	try:
		im = 'https://api.vk.com/method/utils.getShortLink'
		r = requests.post(im, data = {'url':link, 'access_token':TOKEN_VK})
	except:
		print('Error getting updates')
		return False	

	if not r.status_code == 200: 
		print('Error. Can\'t get short link')
		return link
	return r.json()['response']['short_url']


def get_post(vk_group, offset = 0, count = 1):
	try:
		im = 'https://api.vk.com/method/wall.get'
		r = requests.post(im, data = {'domain':vk_group, 'offset':offset, 'count':count, 'access_token':TOKEN_VK, 'filter':'owner'})
	except:
		print('Error getting updates')
		return False	

	if not r.status_code == 200: 
		print('Error. Can\'t get post')
		return False

	posts = []
	for post in r.json()['response']:
		if not type(post) is int:
			text = post['text']

			text = text.replace('<br>', '\n')
			text = text.replace('&amp', '&')
			text = text.replace('&quot', '"')
			text = text.replace('&apos', "'")
			text = text.replace('&gt', '>')
			text = text.replace('&lt', '<')

			try:
				profile_to_replace = re.findall(r'\[(.*?)\]', text)
				profile_link = re.findall(r'\[(.*?)\|', text)
				profile_name = re.findall(r'\|(.*?)\]', text)
				profiles = []

			# заменаем ссылку на профиль в тексте
			
				for i in range(len(profile_link)):
					profiles.append('{} ({})'.format(profile_name[i], get_short_link('vk.com/' + profile_link[i])))
				
				counter = 0
				for i in profile_to_replace:
					text = text.replace('[' + i + ']', profiles[counter])
					counter += 1
			except:
				pass

			try:
				links = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',text)
				short_links = []
				for l in links:
					short_links.append(get_short_link(l))
				for i in range(len(links)):
					text = text.replace(links[i], short_links[i])
			except:
				pass
			##########=========-------------
			#
			# А потом ещё надо заменять ссылки на короткие через
			# /^(https?:\/\/)?([\w\.]+)\.([a-z]{2,6}\.?)(\/[\w\.]*)*\/?$/
			# Но про это будет потом
			#
			##########=========-------------

			photo = []
			video = []
			doc = []
			gif = []

			if 'attachments' in post:
				for item in post['attachments']:
					if item['type'] == 'photo':
						if 'src_xbig' in item['photo']:
							photo.append(item['photo']['src_xbig'])
						elif 'src_big' in item['photo']:
							photo.append(item['photo']['src_big'])
						else:
							photo.append(item['photo']['src_small'])
					if item['type'] == 'doc':
						if item['doc']['ext'] == 'gif':
							gif.append(item['doc']['url'])
						else:
							doc.append([item['doc']['title'], item['doc']['url']])
					if item['type'] == 'video':
						link_vid = get_short_link('https://vk.com/video{}_{}'.format(item['video']['owner_id'],item['video']['vid']))
						video.append([item['video']['title'], link_vid])
			posts.append([text, photo, gif, doc, video])

	return posts

def checking_posts(vk_group, offset = 0, timestamp = 0, limit = 10):
	try:
		im = 'https://api.vk.com/method/wall.get'
		r = requests.post(im, data = {'domain':vk_group, 'offset':offset, 'count':limit, 'access_token':TOKEN_VK, 'filter':'owner'})
	except:
		print('Error getting updates')
		return False	

	if not r.status_code == 200: 
		print('Error. Can\'t get post')
		return False
	fc = []
	for p in r.json()['response']:
		if not type(p) is int:
			if p['date'] > timestamp:
				fc.append(p['date'])
	return fc


def check_group_wall(vk_group):
	with open('timestamp', 'r') as t:
		timestamp = int(t.read())
	while True:
		print('checking... ' + str(datetime.datetime.now()))

		found_count = checking_posts(vk_group, 1, timestamp)
		if len(found_count) == 0:
			print('New posts not found..')
		elif len(found_count) > 0:
			print('found {} new posts!'.format(len(found_count)))

			timestamp = found_count[0]
			with open('timestamp', 'w') as t:
				t.write(str(timestamp))

			posts = get_post(vk_group, 1, len(found_count))
			posts.reverse()
			for p in posts:
				send_sticker(tg_channel, sticker_id[1])
				send_message(tg_channel, p[0])
				for c in p[1]:
					send_photo (tg_channel, c)
				for c in p[2]:
					send_video (tg_channel, c)
				for c in p[3]:
					send_document (tg_channel, c[0], c[1])
				for c in p[4]:
					send_message (tg_channel, '{}\nLink: {}'.format(c[0],c[1]))
				#send_photo (tg_channel, 'http://laoblogger.com/images/curly-line-clip-art-3.jpg')
		print ('sleep...')
		time.sleep(10*60)

check_group_wall(vk_group)

