import sqlite3 as sq
from create_bot import bot
from keyboards import kb_client, kb_admin
from config import config

admin = config.ADMIN_ID

def sql_start():
    global base, cur
    global max_number_sample
    max_number_sample = 200
    base = sq.connect('samanta.db')
    cur = base.cursor()
    if base:
        print("Data base connected OK")
    base.execute("CREATE TABLE IF NOT EXISTS personal(id TEXT PRIMARY KEY, name TEXT, brach TEXT)")
    base.commit()
    base.execute("CREATE TABLE IF NOT EXISTS samples(id INTEGER PRIMARY KEY AUTOINCREMENT, day TEXT, water_number INTEGER, soil_number INTEGER, person_id TEXT, branch TEXT, FOREIGN KEY(person_id) REFERENCES personal(id))")
    base.commit()
    base.execute("CREATE TABLE IF NOT EXISTS max_samples(id INTEGER PRIMARY KEY AUTOINCREMENT, amount INTEGER)")
    base.commit()


# async def sql_check_max_samples():
#     return cur.execute("SELECT * FROM max_samples ORDER BY id DESC LIMIT 1").fetchall()

# async def sql_check_max_samples_add_corrections(limit):
#     return cur.execute("INSERT INTO max_samples (amount) VALUES (?)",(limit,)).fetchall()

async def sql_check_person(id):
    return cur.execute("SELECT * FROM personal WHERE id=?", (id,)).fetchall()
    
async def sql_check_people_by_branch(branch):
    return cur.execute("SELECT * FROM personal WHERE brach=?", (branch,)).fetchall()


async def sql_add_person(id, name, branch, message):
    cur.execute("INSERT INTO personal (id, name, brach) VALUES (?, ?, ?)", (id, name, branch,))
    base.commit()
    await bot.send_message(message.from_user.id, "Вы прошли регистрацию", reply_markup=kb_client)
    await bot.send_message(admin, "Прошел регистрацию пользователь:\n{0} {1}".format(name, branch), reply_markup=kb_client)
     

async def sql_check_samples_all(date):
    return cur.execute("SELECT * FROM samples WHERE day=?", (date,)).fetchall()


async def sql_check_samples(date, branch):
    return cur.execute("SELECT * FROM samples WHERE day=? AND branch=?", (date, branch,)).fetchall()


async def sql_remove_samples(state, id, message):
    async with state.proxy() as data:
        person_branch = (await sql_check_person(id))[0][2]
        check_row =(await sql_check_samples(tuple(data.values())[1], person_branch))
        day = tuple(data.values())[1]
        number = tuple(data.values())[-1]
        if check_row != []:
            water_last = check_row[0][2]
            solid_last = check_row[0][3]
            if tuple(data.values())[2]=='Вода':
                if water_last !=None and water_last !=0 and number <= water_last:
                    water_amount_to_update = water_last - number
                    cur.execute("UPDATE samples SET water_number=? WHERE day=? AND branch=?", (water_amount_to_update, day, person_branch,))
                    base.commit()
                    await bot.send_message(message.from_user.id, "Пробы в кол-ве: {0} шт., удалены!\nОсталось: {1} шт.".format(number, water_amount_to_update), reply_markup=kb_client)
                else:
                    await bot.send_message(message.from_user.id, "Вы хотите удалить больше чем есть ({0} шт.), пропробуйте снова".format(water_last), reply_markup=kb_client)
            if tuple(data.values())[2]=='Почва':
                if solid_last !=None and number <= solid_last and solid_last !=0:
                    solid_amount_to_update = solid_last - number
                    cur.execute("UPDATE samples SET soil_number=? WHERE day=? AND branch=?", (solid_amount_to_update, day, person_branch,))
                    base.commit()
                    await bot.send_message(message.from_user.id, "Пробы в кол-ве: {0} шт., удалены!\nОсталось: {1} шт.".format(number, solid_amount_to_update), reply_markup=kb_client)
                else:
                    await bot.send_message(message.from_user.id, "Вы хотите удалить больше чем есть ({0} шт.), пропробуйте снова".format(solid_last), reply_markup=kb_client)       
        else:
            await bot.send_message(message.from_user.id, "У вашей группы/отдела в этот день таких проб не запланировано", reply_markup=kb_client)


async def sql_add_samples(state, id, message):
    async with state.proxy() as data:
        person_branch = (await sql_check_person(id))[0][2]
        check_row_all =(await sql_check_samples_all(tuple(data.values())[1]))
        check_row =(await sql_check_samples(tuple(data.values())[1], person_branch)) 
        day = tuple(data.values())[1]
        number = int(tuple(data.values())[-1])
        reply_text= 'Ваши пробы в кол-ве {} шт., приняты'.format(number)
        if check_row == []:
            if number <= max_number_sample:
                if tuple(data.values())[2]=='Вода':
                    cur.execute("INSERT INTO samples (day, water_number, branch) VALUES (?, ?, ?)", (day, number , person_branch,))
                    base.commit()
                    await bot.send_message(message.from_user.id, reply_text, reply_markup=kb_client)
                    for res in cur.execute("SELECT * FROM personal WHERE brach='ГХиСИ' ").fetchall():
                        await bot.send_message(res[0], 'На {0} добавлено {1} проб.\nИтого {2} '.format(day, number, number), reply_markup=kb_client)
                if tuple(data.values())[2]=='Почва':
                    cur.execute("INSERT INTO samples (day, soil_number, branch) VALUES (?, ?, ?)", (day,number, person_branch,))
                    base.commit()
                    await bot.send_message(message.from_user.id, reply_text, reply_markup=kb_client)
                    for res in cur.execute("SELECT * FROM personal WHERE brach='ГХиСИ' ").fetchall():
                        await bot.send_message(res[0], 'На {0} добавлено {1} проб.\nИтого {2} '.format(day, number, number), reply_markup=kb_client)
        else:
            water_amount = 0
            soil_amount = 0
            for i in check_row_all:
                if i[2] != None:
                    water_amount += i[2]
                else:
                    pass
                if i[3] != None:
                    soil_amount += i[3]
                else:
                    pass
            total_summ = water_amount + soil_amount
            able_amount = max_number_sample - total_summ
            max_samples_text = 'Максимальная возможное кол-во проб в этот день: {0}'.format(able_amount)
            if tuple(data.values())[2]=='Вода':
                if check_row[0][2]==None:
                    if number <= able_amount:
                        cur.execute("UPDATE samples SET water_number=? WHERE day=? AND branch=?", (number, day, person_branch,))
                        base.commit()
                        await bot.send_message(message.from_user.id, reply_text, reply_markup=kb_client)
                        for res in cur.execute("SELECT * FROM personal WHERE brach='ГХиСИ' ").fetchall():
                            await bot.send_message(res[0], 'На {0} добавлено {1} проб.\nИтого {2} '.format(day, number, number), reply_markup=kb_client)
                    else:
                        await bot.send_message(message.from_user.id, max_samples_text, reply_markup=kb_client)
                else:
                    if number <= able_amount:
                        summ_water_number = check_row[0][2] + number
                        cur.execute("UPDATE samples SET water_number=? WHERE day=? AND branch=?", (summ_water_number, day, person_branch,))
                        base.commit()
                        await bot.send_message(message.from_user.id, reply_text, reply_markup=kb_client)
                        for res in cur.execute("SELECT * FROM personal WHERE brach='ГХиСИ' ").fetchall():
                            await bot.send_message(res[0], 'На {0} добавлено {1} проб.\nИтого {2} '.format(day, number, total_summ+number), reply_markup=kb_client)
                    else:
                        await bot.send_message(message.from_user.id, max_samples_text, reply_markup=kb_client)
            if tuple(data.values())[2]=='Почва':
                if check_row[0][3] == None:
                    if number <= able_amount:
                        cur.execute("UPDATE samples SET soil_number=? WHERE day=? AND branch=?", (number, day, person_branch,))
                        base.commit()
                        await bot.send_message(message.from_user.id, reply_text, reply_markup=kb_client)
                        for res in cur.execute("SELECT * FROM personal WHERE brach='ГХиСИ' ").fetchall():
                            await bot.send_message(res[0], 'На {0} добавлено {1} проб.\nИтого {2} '.format(day, number, number), reply_markup=kb_client)
                    else:
                        await bot.send_message(message.from_user.id, max_samples_text, reply_markup=kb_client)
                else:
                    if number <= able_amount:
                        summ_soil_number = check_row[0][3]+number
                        cur.execute("UPDATE samples SET soil_number=? WHERE day=? AND branch=?", (summ_soil_number, day, person_branch,))
                        base.commit()
                        await bot.send_message(message.from_user.id, reply_text, reply_markup=kb_client)
                        for res in cur.execute("SELECT * FROM personal WHERE brach='ГХиСИ' ").fetchall():
                            await bot.send_message(res[0], 'На {0} добавлено {1} проб.\nИтого {2} '.format(day, number, total_summ+number), reply_markup=kb_client)
                    else:
                        await bot.send_message(message.from_user.id, max_samples_text, reply_markup=kb_client)
        

async def sql_remove_samples_admin(state, message, branch):
    async with state.proxy() as data:
        person_branch = branch
        people_in_branch = (await sql_check_people_by_branch(person_branch))
        check_row =(await sql_check_samples(tuple(data.values())[1], person_branch))
        day = tuple(data.values())[1]
        number = tuple(data.values())[-1]
        if check_row != []:
            water_last = check_row[0][2]
            solid_last = check_row[0][3]
            if tuple(data.values())[2]=='Вода':
                if water_last !=None and water_last !=0 and number <= water_last:
                    water_amount_to_update = water_last - number
                    cur.execute("UPDATE samples SET water_number=? WHERE day=? AND branch=?", (water_amount_to_update, day, person_branch,))
                    base.commit()
                    await bot.send_message(message.from_user.id, "Пробы в кол-ве: {0} шт., удалены!\nОсталось: {1} шт.".format(number, water_amount_to_update), reply_markup=kb_admin)
                    for res in people_in_branch:   
                        await bot.send_message(res[0], "Пробы в кол-ве: {0} шт., удалены!\nОсталось: {1} шт.\nОбратитесь в ГХиСИ".format(number, water_amount_to_update))
                else:
                    await bot.send_message(message.from_user.id, "Вы хотите удалить больше чем есть ({0} шт.), пропробуйте снова".format(water_last), reply_markup=kb_admin)
            if tuple(data.values())[2]=='Почва':
                if solid_last !=None and number <= solid_last and solid_last !=0:
                    solid_amount_to_update = solid_last - number
                    cur.execute("UPDATE samples SET soil_number=? WHERE day=? AND branch=?", (solid_amount_to_update, day, person_branch,))
                    base.commit()
                    await bot.send_message(message.from_user.id, "Пробы в кол-ве: {0} шт., удалены!\nОсталось: {1} шт.".format(number, solid_amount_to_update), reply_markup=kb_admin)
                    for res in people_in_branch:   
                        await bot.send_message(res[0], "Пробы в кол-ве: {0} шт., удалены!\nОсталось: {1} шт.\nОбратитесь в ГХиСИ".format(number, solid_amount_to_update))
                else:
                    await bot.send_message(message.from_user.id, "Вы хотите удалить больше чем есть ({0} шт.), пропробуйте снова".format(solid_last), reply_markup=kb_admin)       
        else:
            await bot.send_message(message.from_user.id, "У вашей группы/отдела в этот день таких проб не запланировано", reply_markup=kb_admin)


async def sql_add_samples_admin(state, message, branch):
    async with state.proxy() as data:
        person_branch = branch
        check_row_all =(await sql_check_samples_all(tuple(data.values())[1]))
        check_row =(await sql_check_samples(tuple(data.values())[1], person_branch)) 
        day = tuple(data.values())[1]
        number = int(tuple(data.values())[-1])
        reply_text= 'Ваши пробы в кол-ве {} шт., приняты'.format(number)
        if check_row == []:
            if number <= max_number_sample:
                if tuple(data.values())[2]=='Вода':
                    cur.execute("INSERT INTO samples (day, water_number, branch) VALUES (?, ?, ?)", (day, number , person_branch,))
                    base.commit()
                    await bot.send_message(message.from_user.id, reply_text, reply_markup=kb_admin)
                    for res in cur.execute("SELECT * FROM personal WHERE brach='ГХиСИ' ").fetchall():
                        await bot.send_message(res[0], 'На {0} добавлено {1} проб.\nИтого {2} '.format(day, number, number), reply_markup=kb_admin)
                if tuple(data.values())[2]=='Почва':
                    cur.execute("INSERT INTO samples (day, soil_number, branch) VALUES (?, ?, ?)", (day,number, person_branch,))
                    base.commit()
                    await bot.send_message(message.from_user.id, reply_text, reply_markup=kb_admin)
                    for res in cur.execute("SELECT * FROM personal WHERE brach='ГХиСИ' ").fetchall():
                        await bot.send_message(res[0], 'На {0} добавлено {1} проб.\nИтого {2} '.format(day, number, number), reply_markup=kb_admin)
        else:
            water_amount = 0
            soil_amount = 0
            for i in check_row_all:
                if i[2] != None:
                    water_amount += i[2]
                else:
                    pass
                if i[3] != None:
                    soil_amount += i[3]
                else:
                    pass
            total_summ = water_amount + soil_amount
            able_amount = max_number_sample - total_summ
            max_samples_text = 'Максимальная возможное кол-во проб в этот день: {0}'.format(able_amount)
            if tuple(data.values())[2]=='Вода':
                if check_row[0][2]==None:
                    if number <= able_amount:
                        cur.execute("UPDATE samples SET water_number=? WHERE day=? AND branch=?", (number, day, person_branch,))
                        base.commit()
                        await bot.send_message(message.from_user.id, reply_text, reply_markup=kb_admin)
                        for res in cur.execute("SELECT * FROM personal WHERE brach='ГХиСИ' ").fetchall():
                            await bot.send_message(res[0], 'На {0} добавлено {1} проб.\nИтого {2} '.format(day, number, number), reply_markup=kb_admin)
                    else:
                        await bot.send_message(message.from_user.id, max_samples_text, reply_markup=kb_admin)
                else:
                    if number <= able_amount:
                        summ_water_number = check_row[0][2] + number
                        cur.execute("UPDATE samples SET water_number=? WHERE day=? AND branch=?", (summ_water_number, day, person_branch,))
                        base.commit()
                        await bot.send_message(message.from_user.id, reply_text, reply_markup=kb_admin)
                        for res in cur.execute("SELECT * FROM personal WHERE brach='ГХиСИ' ").fetchall():
                            await bot.send_message(res[0], 'На {0} добавлено {1} проб.\nИтого {2} '.format(day, number, total_summ+number), reply_markup=kb_admin)
                    else:
                        await bot.send_message(message.from_user.id, max_samples_text, reply_markup=kb_admin)
            if tuple(data.values())[2]=='Почва':
                if check_row[0][3] == None:
                    if number <= able_amount:
                        cur.execute("UPDATE samples SET soil_number=? WHERE day=? AND branch=?", (number, day, person_branch,))
                        base.commit()
                        await bot.send_message(message.from_user.id, reply_text, reply_markup=kb_admin)
                        for res in cur.execute("SELECT * FROM personal WHERE brach='ГХиСИ' ").fetchall():
                            await bot.send_message(res[0], 'На {0} добавлено {1} проб.\nИтого {2} '.format(day, number, number), reply_markup=kb_admin)
                    else:
                        await bot.send_message(message.from_user.id, max_samples_text, reply_markup=kb_admin)
                else:
                    if number <= able_amount:
                        summ_soil_number = check_row[0][3]+number
                        cur.execute("UPDATE samples SET soil_number=? WHERE day=? AND branch=?", (summ_soil_number, day, person_branch,))
                        base.commit()
                        await bot.send_message(message.from_user.id, reply_text, reply_markup=kb_admin)
                        for res in cur.execute("SELECT * FROM personal WHERE brach='ГХиСИ' ").fetchall():
                            await bot.send_message(res[0], 'На {0} добавлено {1} проб.\nИтого {2} '.format(day, number, total_summ+number), reply_markup=kb_admin)
                    else:
                        await bot.send_message(message.from_user.id, max_samples_text, reply_markup=kb_admin)
