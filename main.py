import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import requests
from configs import *

vk_session = vk_api.VkApi(token=VK_API_KEY)
longpoll = VkBotLongPoll(vk_session, '229561055')


def download_file(url, filename):
	response = requests.get(url)
	if response.status_code == 200:
		with open(filename, 'wb') as f:
			f.write(response.content)
		print(f'Файл сохранён как {filename}')
	else:
		print(f'Ошибка скачивания: {response.status_code}')


for event in longpoll.listen():
	if event.type == VkBotEventType.MESSAGE_NEW:
		message = event.message
		print('Текст:', message.text)

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
		else:
			print("Нет вложений в сообщении.")
