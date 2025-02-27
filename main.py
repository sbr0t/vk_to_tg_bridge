import os
import time
import vk_api
import telebot
import requests
from configs import *
from telebot import types
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


vk_session = vk_api.VkApi(token=VK_API_KEY)
longpoll = VkBotLongPoll(vk_session, VK_GROUP_ID)
bot = telebot.TeleBot(TG_BOT_TOKEN)

def download_file(url, filename):
	response = requests.get(url)
	if response.status_code == 200:
		with open(filename, 'wb') as f:
			f.write(response.content)
	else:
		print(f'Ошибка скачивания: {response.status_code}')


for event in longpoll.listen():
	try:
		if event.type == VkBotEventType.MESSAGE_NEW:
			message = event.message

			# Проверяем, есть ли вложения
			attachments = message.attachments if hasattr(message, 'attachments') else []
			if attachments:
				for i, attachment in enumerate(attachments):
					att_type = attachment.get('type')

					if att_type == 'photo':
						# Получаем словарь с данными фото. Обычно в нем есть список разных размеров
						photo = attachment.get('photo', {})
						sizes = photo.get('sizes', [])
						if sizes:
							# Выбираем изображение с максимальным разрешением (по произведению width*height)
							best_photo = max(sizes, key=lambda s: s['width'] * s['height'])
							url = best_photo.get('url')
							if url:
								download_file(url, DOWNLOAD_FOLDER + f'{i}.jpg')
					elif att_type == 'doc':
						# Для документов, URL может быть доступен прямо
						doc = attachment.get('doc', {})
						url = doc.get('url')
						title = doc.get('title', 'document')
						# Попробуйте сохранить с расширением, если оно есть, или просто .doc
						filename = title if '.' in title else title + '.doc'
						if url:
							download_file(url, DOWNLOAD_FOLDER + filename)
					# Можно добавить обработку и для других типов вложений, например, video, audio и т.д.

			files = os.listdir(DOWNLOAD_FOLDER)

			if files:
				photo_count = 0
				for file in files:
					photo_count += 1 if '.jpg' in file else 0

				if photo_count == 1 and len(files) == 1:
					with open(DOWNLOAD_FOLDER + files[0], 'rb') as photo:
						bot.send_photo(TG_CHANEL_ID, photo, caption= message.text)

				elif photo_count == len(files):
					photos = [open(DOWNLOAD_FOLDER + files[0], 'rb')]
					media = [
						types.InputMediaPhoto(photos[0], caption=message.text),
					]

					for i, file in enumerate(files[1:]):
						photos.append(open(DOWNLOAD_FOLDER + file, 'rb'))
						media.append(types.InputMediaPhoto(photos[i+1]))

					bot.send_media_group(TG_CHANEL_ID, media)

					for photo in photos:
						photo.close()

				elif len(files) == 1:
					with open(DOWNLOAD_FOLDER + files[0], 'rb') as doc:
						bot.send_document(TG_CHANEL_ID, doc, caption=message.text)

				else:
					with open(DOWNLOAD_FOLDER + files[0], 'rb') as doc:
						bot.send_document(TG_CHANEL_ID, doc, caption=message.text)
					for file in files[1:]:
						with open(DOWNLOAD_FOLDER + file, 'rb') as doc:
							bot.send_document(TG_CHANEL_ID, doc)

				for file in files:
					os.remove(DOWNLOAD_FOLDER + file)
			else:
				bot.send_message(TG_CHANEL_ID, message.text)
	except Exception as e:
		print(e)
