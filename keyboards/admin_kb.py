from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta

b19 = KeyboardButton('Убрать пробы')
b20 = KeyboardButton('Посмотреть загрузку')
b21 = KeyboardButton('Установить макс. загрузку')
b22 = KeyboardButton('Запуск')

kb_admin = ReplyKeyboardMarkup(resize_keyboard=True)

kb_admin.add(b22).add(b19).add(b20)#.add(b21)


b23 = KeyboardButton('Вода')
b24 = KeyboardButton('Почва')
b25 = KeyboardButton('Отмена')

kb_admin_choise = ReplyKeyboardMarkup()
kb_admin_choise.add(b23).add(b24).add(b25)


today = datetime.today()
weekdays = {1:'Пн.', 2:'Вт.', 3:'Ср.', 4:'Чт.',5:'Пт.',6:'Сб.',7:'Вс.'}

b26 = KeyboardButton('{0}{1}'.format(weekdays.get(today.isoweekday()), (today).strftime('(%d.%m)')))
b27 = KeyboardButton('{0}{1}'.format(weekdays.get((today + timedelta(days=1)).isoweekday()), (today + timedelta(days=1)).strftime('(%d.%m)')))
b28 = KeyboardButton('{0}{1}'.format(weekdays.get((today + timedelta(days=2)).isoweekday()), (today + timedelta(days=2)).strftime('(%d.%m)')))
b29 = KeyboardButton('{0}{1}'.format(weekdays.get((today + timedelta(days=3)).isoweekday()), (today + timedelta(days=3)).strftime('(%d.%m)')))
b30 = KeyboardButton('{0}{1}'.format(weekdays.get((today + timedelta(days=4)).isoweekday()), (today + timedelta(days=4)).strftime('(%d.%m)')))
b31 = KeyboardButton('{0}{1}'.format(weekdays.get((today + timedelta(days=5)).isoweekday()), (today + timedelta(days=5)).strftime('(%d.%m)')))
b32 = KeyboardButton('{0}{1}'.format(weekdays.get((today + timedelta(days=6)).isoweekday()), (today + timedelta(days=6)).strftime('(%d.%m)')))


kb_admin_week = ReplyKeyboardMarkup()
kb_admin_week.row(b26).insert(b27).insert(b28).row(b29).insert(b30)
kb_admin_week.row(b31).insert(b32)
kb_admin_week.row(b25)