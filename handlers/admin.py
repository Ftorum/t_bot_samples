from aiogram import Dispatcher, types
from create_bot import bot
from keyboards import kb_admin, kb_admin_week, kb_admin_choise, kb_client_registration
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import ReplyKeyboardRemove
from data_base.sqlite_db import sql_check_person, sql_check_samples_all, sql_remove_samples_admin#, sql_check_max_samples_add_corrections


class FSMadmin(StatesGroup):
    action = State()
    date = State()
    sample = State()
    number = State()
    branch = State()
    

# class FSMcapacity(StatesGroup):
#     capacity = State()


async def commands_admin_start(message: types.Message):
    ID = message.from_user.id  
    person = await sql_check_person(ID)
    if person[0][2] =='ГХиСИ':
        await bot.send_message(message.from_user.id, 'Выберите действие:', reply_markup=kb_admin) 
        await FSMadmin.action.set() 
    else:
        await bot.send_message(message.from_user.id, 'Вам доступ закрыт', reply_markup=ReplyKeyboardRemove())


# async def capasity(message: types.Message, state: FSMContext):
#     ID = message.from_user.id
#     try:
#         async with state.proxy() as data:
#             data['capacity'] = int(message.text)
#             await sql_check_max_samples_add_corrections(data['capacity'])
#         await bot.send_message(message.from_user.id, 'Суппер, данные обновлены', reply_markup=kb_admin)
#     except ValueError:
#         await bot.send_message(message.from_user.id, 'Ошибка!\nВведите пожалуйста число!', reply_markup=kb_admin)
#         await state.finish()

async def commands_second_admin(message: types.Message, state: FSMContext):
    ID = message.from_user.id
    async with state.proxy() as data:
        data['action'] = message.text
    await FSMadmin.date.set()
    await message.reply('Выберите день', reply_markup=kb_admin_week)

async def commands_third_admin(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['date'] = message.text
        current_capasity = await sql_check_samples_all(tuple(data.values())[1])
        if data['action'] == 'Посмотреть загрузку':
            if current_capasity == []:
                await bot.send_message(message.from_user.id, 'На этот день данных нет', reply_markup=kb_admin)
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
                    await bot.send_message(message.from_user.id, 'На {0} {1} запланировали: \nВода: {2} \nПочва: {3}'.format(branch[1],branch[-1],water,soil), reply_markup=kb_admin)
                await bot.send_message(message.from_user.id, 'Итого, запланировано: {0}'.format(total_number_samples), reply_markup=kb_admin)
                await state.finish()
        else:
            await FSMadmin.sample.set()
            await message.reply('Какие пробы хотите удалить?', reply_markup=kb_admin_choise)


async def command_choose_sample(message: types.Message, state: FSMContext):
    ID = message.from_user.id  
    async with state.proxy() as data:
        data['sample'] = message.text
    await FSMadmin.number.set()
    await message.reply('Введите кол-во проб', reply_markup=ReplyKeyboardRemove())


async def command_choose_branch(message: types.Message, state: FSMContext):
    ID = message.from_user.id  
    try:
        async with state.proxy() as data:
            data['number'] = int(message.text)
        await FSMadmin.branch.set()
        await message.reply('Выберите группу/отдел', reply_markup=kb_client_registration)
    except ValueError:
            await bot.send_message(message.from_user.id, 'Ошибка!\nВведите пожалуйста число!', reply_markup=kb_admin)
            await state.finish()


async def command_load_number(message: types.Message, state: FSMContext):
    ID = message.from_user.id  
    async with state.proxy() as data:
        data['branch'] = message.text
        await sql_remove_samples_admin(state,message,tuple(data.values())[-1])
    await state.finish()



async def cancel_handler_admin(message: types.Message, state: FSMContext):
    ID = message.from_user.id  
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.reply('Ok', reply_markup=kb_admin)

def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(commands_admin_start, lambda message: 'запуск' in (message.text).lower(), state=None)
    dp.register_message_handler(cancel_handler_admin, lambda message: 'отмена' in (message.text).lower(), state = '*' )
    dp.register_message_handler(cancel_handler_admin, Text(equals = "отмена", ignore_case=True), state="*")
    dp.register_message_handler(commands_second_admin, state = FSMadmin.action)
    dp.register_message_handler(commands_third_admin, state = FSMadmin.date)
    dp.register_message_handler(command_choose_sample, state = FSMadmin.sample)
    dp.register_message_handler(command_choose_branch, state = FSMadmin.number)
    dp.register_message_handler(command_load_number, state = FSMadmin.branch)
