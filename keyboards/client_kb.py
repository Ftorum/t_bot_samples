from aiogram.types import ReplyKeyboardMarkup, KeyboardButton #, ReplyKeyboardRemove
from datetime import datetime, timedelta

b0 = KeyboardButton('Привет')
b1 = KeyboardButton('Добавить пробы')
b2 = KeyboardButton('Убрать пробы')
b3 = KeyboardButton('Посмотреть загрузку')

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client.add(b0).add(b1).add(b2).add(b3)



b4 = KeyboardButton('Вода')
b5 = KeyboardButton('Почва')
b6 = KeyboardButton('Отменить')

kb_client_choise = ReplyKeyboardMarkup()
kb_client_choise.add(b4).add(b5).add(b6)


today = datetime.today()
weekdays = {1:'Пн.', 2:'Вт.', 3:'Ср.', 4:'Чт.',5:'Пт.',6:'Сб.',7:'Вс.'}

b7 = KeyboardButton('{0}{1}'.format(weekdays.get(today.isoweekday()), (today).strftime('(%d.%m)')))
b8 = KeyboardButton('{0}{1}'.format(weekdays.get((today + timedelta(days=1)).isoweekday()), (today + timedelta(days=1)).strftime('(%d.%m)')))
b9 = KeyboardButton('{0}{1}'.format(weekdays.get((today + timedelta(days=2)).isoweekday()), (today + timedelta(days=2)).strftime('(%d.%m)')))
b10 = KeyboardButton('{0}{1}'.format(weekdays.get((today + timedelta(days=3)).isoweekday()), (today + timedelta(days=3)).strftime('(%d.%m)')))
b11 = KeyboardButton('{0}{1}'.format(weekdays.get((today + timedelta(days=4)).isoweekday()), (today + timedelta(days=4)).strftime('(%d.%m)')))
b12 = KeyboardButton('{0}{1}'.format(weekdays.get((today + timedelta(days=5)).isoweekday()), (today + timedelta(days=5)).strftime('(%d.%m)')))
b13 = KeyboardButton('{0}{1}'.format(weekdays.get((today + timedelta(days=6)).isoweekday()), (today + timedelta(days=6)).strftime('(%d.%m)')))


kb_client_week = ReplyKeyboardMarkup()
kb_client_week.row(b7).insert(b8).insert(b9).row(b10).insert(b11)
kb_client_week.row(b12).insert(b13)
kb_client_week.row(b6)


b14 = KeyboardButton('ГХиСИ')
b15 = KeyboardButton('ГАГ')
b16 = KeyboardButton('ГПиПВ')
b17 = KeyboardButton('ОХТИ')
b18 = KeyboardButton('ОМВС')

kb_client_registration = ReplyKeyboardMarkup()
kb_client_registration.row(b14).row(b15).row(b16).row(b17).row(b18)

