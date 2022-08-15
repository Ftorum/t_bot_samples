from aiogram import Dispatcher, types
from create_bot import bot
from keyboards import kb_client, kb_client_choise, kb_client_week, kb_client_registration
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from data_base.sqlite_db import sql_add_samples, sql_check_person, sql_check_samples_all, sql_remove_samples, sql_add_person


class FSMday(StatesGroup):
    date = State()
    action = State()
    sample = State()
    number = State()

class FSMperson(StatesGroup):
    name = State()
    branch = State()


async def commands_hi(message: types.Message):
    ID = message.from_user.id  
    person = await sql_check_person(ID)
    if person ==[]:
        await bot.send_message(message.from_user.id, 'Вам нужно пройти регистрацию.\nВведите свое имя:', reply_markup=ReplyKeyboardRemove())
        await FSMperson.name.set() 
    if person[0][2] == 'ГАГ' or person[0][2] == 'ГПиПВ' or person[0][2] == 'ОХиТИ' or person[0][2] == 'ОМВС':
        await FSMday.action.set() 
        await bot.send_message(message.from_user.id, 'Привет!\nВыберите действие', reply_markup=kb_client)
    else: 
        await bot.send_message(message.from_user.id, 'Вы администратор\nЗапустите свою команду', reply_markup=ReplyKeyboardRemove())


async def enter_name(message: types.Message, state: FSMContext):
    ID = message.from_user.id  
    async with state.proxy() as data:
        data['name'] = message.text
    await FSMperson.branch.set()
    await message.reply('Выберите группу/отдел', reply_markup=kb_client_registration)


async def load_person(message: types.Message, state: FSMContext):
    ID = message.from_user.id  
    async with state.proxy() as data:
        data['branch'] = message.text
    async with state.proxy() as data:
        await sql_add_person(ID, tuple(data.values())[0], tuple(data.values())[1], message)
    await state.finish()


async def type_sample(message: types.Message, state: FSMContext):
    ID = message.from_user.id  
    async with state.proxy() as data:
        data['action'] = message.text
    await FSMday.sample.set()
    await message.reply('Выберите день', reply_markup=kb_client_week)


async def choose_day(message: types.Message, state: FSMContext):
    ID = message.from_user.id  
    async with state.proxy() as data:
        data['date'] = message.text
        current_capasity = await sql_check_samples_all(tuple(data.values())[1])
        if data['action'] == 'Посмотреть загрузку':
            if current_capasity == []:
                await bot.send_message(message.from_user.id, 'На этот день данных нет', reply_markup=kb_client)
                await state.finish()
            else:
                total_number_samples = 0
                for branch in current_capasity:
                    water = branch[2]
                    soil = branch[3]
                    if water != None:
                        total_number_samples += water
                    else:
                        water=0
                    if soil != None:
                        total_number_samples += soil
                    else:
                        soil=0
                    await bot.send_message(message.from_user.id, 'На {0} {1} запланировали: \nВода: {2} \nПочва: {3}'.format(branch[1],branch[-1],water,soil), reply_markup=kb_client)
                await bot.send_message(message.from_user.id, 'Итого, запланировано: {0}'.format(total_number_samples), reply_markup=kb_client)
                await state.finish()
        else:
            await FSMday.date.set()
            await message.reply('Какие пробы хотите добавить/удалить?', reply_markup=kb_client_choise)


async def choose_sample(message: types.Message, state: FSMContext):
    ID = message.from_user.id  
    async with state.proxy() as data:
        data['sample'] = message.text
    await FSMday.number.set()
    await message.reply('Введите кол-во проб', reply_markup=ReplyKeyboardRemove())


async def load_number(message: types.Message, state: FSMContext):
    ID = message.from_user.id  
    try:
        async with state.proxy() as data:
            data['number'] = int(message.text)
        async with state.proxy() as data:
            if tuple(data.values())[0] == 'Добавить пробы':
                person = await sql_check_person(ID)
                await sql_add_samples(state,person[0][0],message)
            if tuple(data.values())[0] == 'Убрать пробы':
                person = await sql_check_person(ID)
                await sql_remove_samples(state,person[0][0],message)
    except ValueError:
        await bot.send_message(message.from_user.id, 'Ошибка!\nВведите пожалуйста число!', reply_markup=kb_client)
        await state.finish()
    await state.finish()


async def cancel_handler(message: types.Message, state: FSMContext):
    ID = message.from_user.id  
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Ok', reply_markup=kb_client)

def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(commands_hi, lambda message: 'привет' in (message.text).lower(), state=None)
    dp.register_message_handler(cancel_handler, lambda message: 'отменить' in (message.text).lower(), state = '*' )
    dp.register_message_handler(cancel_handler, Text(equals = "отменить", ignore_case=True), state="*")
    dp.register_message_handler(type_sample, state = FSMday.action)
    dp.register_message_handler(choose_day, state = FSMday.sample)
    dp.register_message_handler(choose_sample, state = FSMday.date)
    dp.register_message_handler(load_number,  state = FSMday.number)
    dp.register_message_handler(enter_name, state = FSMperson.name)
    dp.register_message_handler(load_person, state = FSMperson.branch)
    
    
