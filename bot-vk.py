#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fileencoding=utf-8

#основной код

import config1
import vk_api
from urllib.request import urlretrieve #Библиотека для сохранения фото
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
import random
import requests
from bs4 import BeautifulSoup
import time

fraza = [' Что вы, что вы, сеньоры. Гипербола — это преувеличение. К примеру: «Машка в 100 раз больше меня весит!»', 'Всесторонне недоразвитая личность.', 'Ищешь проблему? Я к твоим услугам!', 'Хорошего человека и обидеть приятно.', 'Ты мне напоминаешь меня в двухлетнем возрасте — тоже норовишь всё обоcрать', 'При таком характере ты могла бы быть и покрасивее', 'Я в сотый раз убеждаюсь, что кроме высшего образования нужно иметь хотя бы среднюю сообразительность', 'Хочется верить, что будет хотеться и дальше', 'Скажи, тебе помочь или не мешать?', 'Какая разница, как другие относятся ко мне? Главное — как я отношусь к ним!']

#Авторизация пользователя
vk_session = vk_api.VkApi(config1.log, config1.password)
vk_session.auth()

#Запуск
vkUser = vk_session.get_api()

#Авторизация сообщества
vk_session = vk_api.VkApi(token = config1.token)
vk_session._auth_token()
#Запуск
vk = vk_session.get_api()

#Обращаемся к серверу
session_api =  vk_session.get_api()
longpoll = VkLongPoll(vk_session)

# Группа бота
group_id = ""#Обязательно, иначе выдаст ошибку

# Загрузка данных на сервер и отправка сообщения
def UploadMessage(vk_session,vkUser,peer_id, GroupNameId, photo_ID):
    vk.messages.send(message = "Вот тебе картинка:\nhttps://vk.com/{}?z=photo{}_{}/{}_{}".format(GroupNameId, photo_ID["owner_id"],photo_ID["id"], GroupNameId, photo_ID["album_id"]), peer_id = peer_id, random_id = 0)

#Чек есть ли в сообществе альбомы 
def AlbumCheck(group,vk):
    Check = vk.photos.getAlbums(owner_id = "-{}".format(group))
    if Check['count'] > 0:
        photoAlbum = vk.photos.get(owner_id = "-{}".format(group),album_id = Check['items'][random.randint(0,len(Check['items']) -1)]['id'])
        randomItem = random.randint(0,len(photoAlbum['items'])-1)
        photoImage = photoAlbum['items'][randomItem]
        return photoImage
    else:
        return False

#Проверка открыта ли группа
def CheckGroup(group,vk):
	check =vk.groups.getById(group_id = group)
	if check[0]["is_closed"] == 0 and check[0]['id'] != group_id:
		return True,check[0]['id']
	elif check[0]['id'] == group_id:
		vk.messages.send(peer_id =event.object.message["peer_id"] ,random_id = 0,message = "Оу Бро, это можно использовать только на группах и не на мне")
		return False,0
	else:
		vk.messages.send(peer_id =event.object.message["peer_id"] ,random_id = 0,message = "Оу Бро, Эта группа Закрыта")
		return False,0

#Создаем коавиатуру
def create_keyboard(response):
	keyboard = VkKeyboard(one_time=True)#True чтобы закрывалась, False чтобы не закрывалась
	if response == 'начать':#текст клавиатуры
		keyboard.add_button('фраза', color=VkKeyboardColor.NEGATIVE)
		keyboard.add_button('новости', color=VkKeyboardColor.NEGATIVE)

		keyboard.add_line()#Обозначает добавление новой строки

		keyboard.add_button('погода', color=VkKeyboardColor.POSITIVE)

		keyboard.add_line()

		keyboard.add_button('фото', color=VkKeyboardColor.PRIMARY)#цвет клавиатуры DEFAULT-белый, PRIMARY-синий, NEGATIVE-красный, POSITIVE-зеленый
		keyboard.add_button('чатик', color=VkKeyboardColor.PRIMARY)

		keyboard.add_line()#Обозначает добавление новой строки

		keyboard.add_button('пока', color=VkKeyboardColor.DEFAULT)

	elif response == 'привет' or response == "ку" or response == "hi":
		keyboard.add_button('начать', color=VkKeyboardColor.NEGATIVE)
		keyboard.add_button('пока', color=VkKeyboardColor.PRIMARY)

	elif response == 'пока':
		keyboard.add_button('начать', color=VkKeyboardColor.PRIMARY)

	elif response == 'фраза':
		keyboard.add_button('спасибо', color=VkKeyboardColor.PRIMARY)

	elif response == 'спасибо':
		keyboard.add_button('фраза', color=VkKeyboardColor.NEGATIVE)
		keyboard.add_button('новости', color=VkKeyboardColor.NEGATIVE)

		keyboard.add_line()

		keyboard.add_button('погода', color=VkKeyboardColor.POSITIVE)

		keyboard.add_line()

		keyboard.add_button('фото', color=VkKeyboardColor.PRIMARY)
		keyboard.add_button('чатик', color=VkKeyboardColor.PRIMARY)

		keyboard.add_line()

		keyboard.add_button('пока', color=VkKeyboardColor.DEFAULT)

	elif response == 'чатик':
		keyboard.add_button('спасибо', color=VkKeyboardColor.PRIMARY)

	elif response == 'фото':
		 keyboard.add_button('спасибо', color=VkKeyboardColor.PRIMARY)

	elif response == 'новости':
		keyboard.add_button('спасибо', color=VkKeyboardColor.PRIMARY)

	elif response == 'погода':
		keyboard.add_button('спасибо', color=VkKeyboardColor.PRIMARY)

	keyboard = keyboard.get_keyboard()
	return keyboard

STATUS = False#переменная состаяния

#Форма отправки сообщения
def send_message(vk_session, id_type, id, message=None, attachment=None, keyboard=None):
    vk_session.method('messages.send',{id_type: id, 'message': message, 'random_id': random.randint(-2147483648, +2147483648), "attachment": attachment, 'keyboard': keyboard})


for event in longpoll.listen():#слушаем сервер
	if event.type == VkEventType.MESSAGE_NEW:#находим новое сообщение
		print(event.text)#текст сообщения
		print(event.user_id)#id пользователя

		response = event.text.lower()#приравниваем сообщение к нижнему регистру
		keyboard = create_keyboard(response)#создаем клавиатуру

		if event.from_user and not (event.from_me):#если сообщение от пользователя и не от меня
			if response == "привет" or response == "ку" or response == "hi":
				 send_message(vk_session, 'user_id', event.user_id, message='Привет, друг!',keyboard=keyboard)
				 print('-'*10)
			elif response == "пока":
				send_message(vk_session, 'user_id', event.user_id, message='Пока(((',keyboard=keyboard)
				print('-'*10)
			elif response == "начать":
				send_message(vk_session, 'user_id', event.user_id, message='Давай начнем. Что делаем?',keyboard=keyboard)
				print('-'*10)
			elif response == "фраза":
				send_message(vk_session, 'user_id', event.user_id, message=str(fraza[random.randint(0,9)]), keyboard=keyboard)
				print('-'*10)
			elif response == "спасибо":
				send_message(vk_session, 'user_id', event.user_id, message='Пожалуйста, что делаем дальше?',keyboard=keyboard)
				print('-'*10)
			elif response == "чатик":
				send_message(vk_session, 'user_id', event.user_id, message=str(config1.chat),keyboard=keyboard)
				print('-'*10)
			elif response == "фото":
				send_message(vk_session, 'user_id', event.user_id, message='Для получения фотографии отправь мне ссылку на группу откуда хочешь фото.',keyboard=keyboard)
				print('-'*10)

			elif "https://vk.com/" in response:
				GroupNameId = response.replace("https://vk.com/","")
				vk.messages.send(peer_id = event.peer_id,random_id = 0,message = "Вау, отлично, Бро, сейчас отправлю!")
				print('-'*10)
				check = CheckGroup(GroupNameId,vk)
				if check[0]:
					photo_ID = AlbumCheck(check[1],vkUser)
					if photo_ID != False:
						UploadMessage(vk_session,vkUser,event.peer_id, GroupNameId, photo_ID)
					else:
						vk.messages.send(peer_id = event.peer_id,random_id = 0,message = "Эй Бро! В этой группе нет альбомов с фото")
						print('-'*10)

			elif response == "новости":
				url = 'https://yandex.ru/news/'
				page = requests.get(url)
				bs = BeautifulSoup(page.text, 'html.parser')

				selector = '.link_theme_black'
				result = [i.text for i in bs.select(selector)]
				result = result[-1]

				send_message(vk_session, 'user_id', event.user_id, message=str(result),keyboard=keyboard)
				print('-'* 10)

			elif response == "погода":
				send_message(vk_session, 'user_id', event.user_id, message="Ввиди название города")
				STATUS = True

			elif STATUS:

				s_city = event.text
				city_id = 0

				res = requests.get("http://api.openweathermap.org/data/2.5/find", params={'q': s_city, 'type': 'like', 'units': 'metric', 'APPID': config1.apikey})
				data = res.json()

				cities = ["{} ({})".format(d['name'], d['sys']['country'])for d in data['list']]
				city_id = data['list'][0]['id']

				RES = requests.get("http://api.openweathermap.org/data/2.5/weather", params={'id': city_id, 'units': 'metric', 'lang': 'ru', 'APPID': config1.apikey})
				DATA = RES.json()

				keyB=VkKeyboard(one_time=True)
				keyB.add_button('спасибо', color=VkKeyboardColor.PRIMARY)
				keyB = keyB.get_keyboard()

				send_message(vk_session, 'user_id', event.user_id, message="Погодные условия: " + str(DATA['weather'][0]['description']))

				send_message(vk_session, 'user_id', event.user_id, message="Температура: " + str(DATA['main']['temp']),keyboard=keyB)

				STATUS = False

			else:
				vk_session.method('messages.send', {'user_id': event.user_id, 'message': 'Я не знаю что ответить(', 'random_id': 0})
