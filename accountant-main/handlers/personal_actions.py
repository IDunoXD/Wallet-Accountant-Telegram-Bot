import telebot
from dispatcher import dp
import config
import re
from bot import BotDB
from telebot import types

import logging

from aiogram import Bot, types
from utils import TestStates
from messages import MESSAGES

logging.basicConfig(format=u'%(filename)+13s [ LINE:%(lineno)-4s] %(levelname)-8s [%(asctime)s] %(message)s',
                    level=logging.DEBUG)

bot = Bot(token=config.BOT_TOKEN)

StartKeybord = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
item1 = types.KeyboardButton("➕Прибуток")
item2 = types.KeyboardButton("➖Витрати")
item3 = types.KeyboardButton("❌Видалити останній запис❌")
item4 = types.KeyboardButton("🕘Історія")
StartKeybord.add(item1,item2).add(item4).add(item3)

within_als = {
    "day": ('today', 'day', 'сьогодні', 'день'),
    "week": ('week','неділя'),
    "month": ('month', 'місяць'),
    "year": ('year', 'рік'),
    "all": ('all','весь час')
}

record_types=["прибуток","🏠дім","💲покупки","🍗продукти","😜розваги","✈️транспорт"]

async def history(message: types.Message,within):
    records = BotDB.get_records(message.from_user.id, within)
    if(len(records)):
        answer = f"🕘 Історія операцій за {within_als[within][-1]}\n\n"
        sum=0
        for r in records:
            answer += "<b>" + ("➖ Витрати" if not r[2] else "➕ Прибуток") + "</b>"
            answer += f" на '{record_types[r[3]]}' " if not r[2] else ""
            answer += f" - {r[4]}"
            answer += f" <i>({r[5]})</i>\n"
            if r[2]:
                sum+=r[4]
            else:
                sum-=r[4]
        answer+=f"⬆️ <b>Сума</b> за період <u>{str(sum)}</u>"
        await message.reply(answer)
    else:
        await message.reply("Записів не знайдено!")

@dp.message_handler(state='*', commands = "start")
async def start(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    await state.set_state(TestStates.all()[0])  
    if(not BotDB.user_exists(message.from_user.id)):
        BotDB.add_user(message.from_user.id)
    await message.reply(MESSAGES['help'],reply=False)
    await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)

@dp.message_handler(state='*',commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(MESSAGES['help'])

@dp.message_handler(state='*', commands=['setstate'])
async def process_setstate_command(message: types.Message):
    argument = message.get_args()
    state = dp.current_state(user=message.from_user.id)
    if not argument:
        await state.set_state(TestStates.all()[0])
        return await message.reply(MESSAGES['state_reset'])

    if (not argument.isdigit()) or (not int(argument) < len(TestStates.all())):
        return await message.reply(MESSAGES['invalid_key'].format(key=argument))

    await state.set_state(TestStates.all()[int(argument)])
    await message.reply(MESSAGES['state_change'], reply=False)

@dp.message_handler(state=TestStates.TEST_STATE_0, commands = ("spent", "earned", "s", "e"), commands_prefix = "/!")
async def start(message: types.Message):
    cmd_variants = (('/spent', '/s', '!spent', '!s'), ('/earned', '/e', '!earned', '!e'))
    operation = '-' if message.text.startswith(cmd_variants[0]) else '+'
    state = dp.current_state(user=message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    item1 = types.KeyboardButton("відміна")
    item2 = types.KeyboardButton("🏠дім")
    item3 = types.KeyboardButton("💲покупки")
    item4 = types.KeyboardButton("🍗продукти")  
    item5 = types.KeyboardButton("😜розваги") 
    item6 = types.KeyboardButton("✈️транспорт")
    value = message.text
    for i in cmd_variants:
        for j in i:
            value = value.replace(j, '').strip()

    if(len(value)):   
        if value[0]=='-':
            operation='-'
        elif value[0]=='+':
            operation='+'
        x = re.findall(r"\d+(?:.\d+)?", value)
        if(len(x)):
            value = float(x[0].replace(',', '.'))
            if(operation == '-'):
                markup.add(item2,item3).add(item4,item5).add(item6,item1)          
                BotDB.add_record(message.from_user.id, operation, value)
                await state.set_state(TestStates.all()[4])
                await message.reply("Виберіть тип витрат",reply=False,reply_markup=markup)
            else:
                markup.add(item1)
                await message.reply("✅ Запис про <u><b>прибуток</b></u> успішно внесений!")
                await state.set_state(TestStates.all()[0])
                await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)
        else:
            await message.reply("Не вдалося виявити суму!")
    else:    
        markup.add(item1)
        await message.reply("Введіть суму!",reply=False, reply_markup=markup)
        if operation=='-':
            await state.set_state(TestStates.all()[2])
        elif operation=='+':
            await state.set_state(TestStates.all()[1])

@dp.message_handler(state=TestStates.TEST_STATE_0,commands = ("history", "h"), commands_prefix = "/!")
async def start(message: types.Message):
    cmd_variants = ('/history', '/h', '!history', '!h')

    cmd = message.text
    for r in cmd_variants:
        cmd = cmd.replace(r, '').strip()

    within = "day"
    if(len(cmd)):
        for k in within_als:
            for als in within_als[k]:
                if(als == cmd):
                    within = k

    await history(message,within)

@dp.message_handler(state=TestStates.TEST_STATE_0, content_types=['text'])
async def start(message: types.Message): 
    state = dp.current_state(user=message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    item1 = types.KeyboardButton("відміна")
    item2 = types.KeyboardButton("день")
    item3 = types.KeyboardButton("неділя")
    item4 = types.KeyboardButton("місяць")  
    item5 = types.KeyboardButton("рік") 
    item6 = types.KeyboardButton("за весь час")
    item7 = types.KeyboardButton("підтвердити")   
    if message.text=="➕Прибуток":
        await state.set_state(TestStates.all()[1])
        markup.add(item1)
        await message.reply("Введіть у!",reply=False, reply_markup=markup)
    elif message.text=="➖Витрати":
        await state.set_state(TestStates.all()[2])
        markup.add(item1)
        await message.reply("Введіть суму!",reply=False, reply_markup=markup)
    elif message.text=="🕘Історія":
        if(BotDB.records_exists(message.from_user.id)):
            await state.set_state(TestStates.all()[3])
            markup.add(item2,item3).add(item4,item5).add(item6).add(item1)
            await message.reply("Виберіть період",reply=False, reply_markup=markup)
        else:
            await message.reply("Записів не знайдено!")
            await state.set_state(TestStates.all()[0])
            await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)  
    elif message.text=="❌Видалити останній запис❌":
        if(BotDB.records_exists(message.from_user.id)):
            await state.set_state(TestStates.all()[5])
            markup.add(item7,item1)
            await message.reply("Підтвердити операцію?",reply=False, reply_markup=markup)
        else:
            await message.reply("Записів не знайдено!")
            await state.set_state(TestStates.all()[0])
            await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)
    else:
        await message.reply("Невідома команда",reply=False)

@dp.message_handler(state=TestStates.TEST_STATE_1 | TestStates.TEST_STATE_2, content_types=['text'])
async def start(message: types.Message): 
    state = dp.current_state(user=message.from_user.id)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True,one_time_keyboard=True)
    item1 = types.KeyboardButton("відміна")
    item2 = types.KeyboardButton("🏠дім")
    item3 = types.KeyboardButton("💲покупки")
    item4 = types.KeyboardButton("🍗продукти")  
    item5 = types.KeyboardButton("😜розваги") 
    item6 = types.KeyboardButton("✈️транспорт") 
    markup.add(item2,item3).add(item4,item5).add(item6,item1)
    if message.text=='відміна':        
        await state.set_state(TestStates.all()[0])
        await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)
    else:
        operation= '-' if message.text[0]=='-' else '+'
        if ((message.text[0]!= '-')==(message.text[0]!= '+')):
            operation= '-' if await state.get_state()=='test_state_2' else '+'
        value = message.text
        if(len(value)):
            x = re.findall(r"\d+(?:.\d+)?", value)
            if(len(x)):
                value = float(x[0].replace(',', '.'))
                if(operation == '-'):
                    BotDB.add_record(message.from_user.id, operation, value)
                    await state.set_state(TestStates.all()[4])
                    await message.reply("Виберіть тип витрат",reply=False,reply_markup=markup)
                else:
                    BotDB.add_record(message.from_user.id, operation, value)
                    await message.reply("✅ Запис про <u><b>прибуток</b></u> успішно внесений!")
                    await state.set_state(TestStates.all()[0])
                    await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)
            else:
                await message.reply("Не вдалося виявити суму!")
        else:
            await message.reply("Введіть суму!",reply=False)

@dp.message_handler(state=TestStates.TEST_STATE_3, content_types=['text'])
async def start(message: types.Message): 
    state = dp.current_state(user=message.from_user.id)
    if message.text=="день":
        await state.set_state(TestStates.all()[0])
        await history(message,"day")      
        await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)
    elif message.text=="неділя":
        await state.set_state(TestStates.all()[0])
        await history(message,"week")
        await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)
    elif message.text=="місяць":
        await state.set_state(TestStates.all()[0])
        await history(message,"month")
        await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)
    elif message.text=="рік":
        await state.set_state(TestStates.all()[0])
        await history(message,"year")
        await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)
    elif message.text=="за весь час":
        await state.set_state(TestStates.all()[0])
        await history(message,"all")
        await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)
    elif message.text=="відміна":
        await state.set_state(TestStates.all()[0])
        await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)
    else:
        await message.reply("Невідома команда команда",reply=False)

@dp.message_handler(state=TestStates.TEST_STATE_4, content_types=['text'])
async def start(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    try:
        if message.text=="відміна":
            BotDB.remove_record(message.from_user.id)
            await state.set_state(TestStates.all()[0])
            await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)
        else: 
            index=record_types.index(message.text)
            BotDB.change_record_type(message.from_user.id, index)
            await state.set_state(TestStates.all()[0])       
            await message.reply("✅ Запис про <u><b>витрати</b></u> на '"+record_types[index]+"' успішно внесений!")    
            await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)
    except ValueError:
        await message.reply("Невідома команда",reply=False)

@dp.message_handler(state=TestStates.TEST_STATE_5, content_types=['text'])
async def start(message: types.Message):
    state = dp.current_state(user=message.from_user.id)
    if message.text=="підтвердити":
        BotDB.remove_record(message.from_user.id)
        await state.set_state(TestStates.all()[0])
        await message.reply("Запис видалено")
        await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)
    elif message.text=="відміна":
        await state.set_state(TestStates.all()[0])
        await message.reply(MESSAGES['start'],reply=False,reply_markup=StartKeybord)
    else:
        await message.reply("Невідома команда",reply=False)