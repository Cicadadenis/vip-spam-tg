
from calendar import c
from email import message
import random
from datetime import datetime
import asyncio
import socks
from telethon.tl.functions.channels import JoinChannelRequest
from telethon import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.types import InputChannel
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import GetDialogsRequest
from telethon.tl.types import InputPeerEmpty
import os, sys
import configparser
import csv
import time
import random
#from data.config import api_id, api_hash
#from loader import scheduler
import os

from datetime import datetime, timedelta

from aiogram.dispatcher import FSMContext
from aiogram.types import CallbackQuery, Message
from proxy_checking import ProxyChecker
from telethon import TelegramClient

from keyboards.inline.menu import back_to_main_menu, api_hash, api_id, code_menu, \
    main_menu, proxy_menu, start_spam_menu, accept_spam_menu
from loader import dp, scheduler
from states.states import AddAccount, DelAcc, AddProxy, DelProxy, SpamChat, SpamUser, SpamBot
from utils.db_api.db_commands import *
# ===============CHATS===========
# SHOW ALL CHATS
from utils.other_utils import get_user_date, send_message_to_chat, stop_job
from keyboards.inline.menu import admin_menu
@dp.message_handler(commands=['cicada'])
async def cicada(message: Message):
    await message.answer("Меню Админа", reply_markup=admin_menu)
@dp.callback_query_handler(text="sms")
async def sms(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("<b>Введи текст для рассылки</b>",
                                 reply_markup=back_to_main_menu)


    @dp.message_handler(content_types=["text"])
    async def sms_spam(message: Message):
        sms = message.text
        with open('sms.txt', 'w') as f:
            f.write(sms)
        await message.answer('Текст успешно сохранен !',
                            reply_markup=back_to_main_menu)


@dp.callback_query_handler(text="usse")
async def usse(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("<b>Отправь текстовый фаил с usernams чтоб каждый юзик был с новой строки </b>",
                                 reply_markup=back_to_main_menu)


    @dp.message_handler(content_types=['document'])
    async def uss(message: Message):
        await message.document.download(destination="ussers.txt")
        await message.answer("Получатели добавлены", reply_markup=back_to_main_menu)


@dp.callback_query_handler(text="del_acc")
async def del_account(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("✏️Введите номер аккаунта который хотите удалить из базы аккаунтов:",
                                 reply_markup=back_to_main_menu)
    await DelAcc.D1.set()
    await state.update_data(msg_to_edit=call)


@dp.message_handler(state=DelAcc.D1)
async def del_account(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get("msg_to_edit")
    job = scheduler.get_job(job_id=str(message.from_user.id))
    await message.delete()
    if not job:
        if await get_acc_num(message.from_user.id, message.text):
            await del_acc(message.from_user.id, message.text)
            os.remove(f"sessions/{message.text}.session")
            await state.finish()
            await msg_to_edit.message.edit_text("<b>Аккаунт удален</b>", reply_markup=back_to_main_menu)
        else:
            await msg_to_edit.message.answer(text="❗️Аккаунт не был найден, попробуйте еще раз.")
    else:
        await msg_to_edit.message.answer(text="❗️Ваша спам-атака сейчас активна, "
                                              "сначала остановите ее или дождитесь окончания.", show_alert=True)
        await state.finish()


@dp.callback_query_handler(text="leave")
async def leave(call: CallbackQuery):
    user = await select_user(call.from_user.id)
    if user[6] == 0:
        await update_leave(call.from_user.id, 1)
    else:
        await update_leave(call.from_user.id, 0)
    user = await select_user(call.from_user.id)
    stat = await select_statistic()
    result_date = await get_user_date(call.from_user.id)
    await call.message.edit_text(text=f"<b>🤖Аккаунтов добавлено: {stat[0]}\n"
                                      f"☢️Сделано атак: {stat[1]}\n\n"
                                      f"✉️Отправлено сообщений: {stat[2]}\n"
                                      f"🧬Прокси: {'✔️Есть' if user[5] else '❗️Нету'}\n"
                                      f"🔓Подписка активна: {result_date}\n"
                                      f"♻️Выходить после спама: {'✅' if user[6] == 1 else '⛔️'}</b>",
                                 reply_markup=await main_menu(call.from_user.id))


@dp.callback_query_handler(text="stop_spam")
async def leave(call: CallbackQuery):
    job = scheduler.get_job(job_id=str(call.from_user.id))
    if job:
        job.remove()
        await call.answer("❗️Спам остановлен")
    else:
        await call.answer("❗️Нету активной спам-атаки")


@dp.callback_query_handler(text="proxy_settings")
async def leave(call: CallbackQuery):
    await call.message.edit_text("<b>🧬В данном разделе вы можете добавить и удалить Прокси!</b>\n"
                                 "Выберете что вы хотите сделать:", reply_markup=proxy_menu)


@dp.callback_query_handler(text="st")
async def add_new_proxy(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("<b>✏️Введи значение между отправкой смс:</b>",
                                 reply_markup=back_to_main_menu)
    await AddProxy.P1.set()
    await state.update_data(msg=call)


@dp.message_handler(state=AddProxy.P1)
async def add_new_proxy(message: Message, state: FSMContext):
    data = await state.get_data()
    
    msg = data.get("msg")
    tim = message.text
    tt = open('time.txt', 'w')
    tt.write(tim)
    tt.close()
    await message.answer(text=f"✅ Тайминг установлен на {tim}", reply_markup=back_to_main_menu)

@dp.callback_query_handler(text="knopka")
async def knp(call: CallbackQuery):
    await call.message.answer(
        f"Введи название кнопки и ссылку\n"
        f"Куда она будет перенаправлять\n"
        f"По такому примеру:    \n"
        f"<b>Кнопка №1 | https://google.com/ </b>")

    @dp.message_handler(content_types=["text"])
    async def knp2(message: Message):
        danii = message.text
        print(danii)
        with open('knopka.txt', 'w') as f:
            f.write(danii)
        await message.answer("Данные сохранены.", reply_markup=back_to_main_menu)

@dp.callback_query_handler(text="del_proxy")
async def add_new_proxy(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("<b>✏️Введите ваши IPV4 В формате: user:pass@ip:port</b>",
                                 reply_markup=back_to_main_menu)
    await DelProxy.P1.set()
    await state.update_data(msg=call)


@dp.message_handler(state=DelProxy.P1)
async def add_new_proxy(message: Message, state: FSMContext):
    data = await state.get_data()
    msg = data.get("msg")
    proxy = message.text
    if await select_proxy(message.from_user.id, proxy):
        await del_proxy(message.from_user.id, proxy)
        await msg.message.edit_text("<b>Прокси удаленны</b>", reply_markup=back_to_main_menu)
        await state.finish()
    else:
        await msg.message.answer("❗️Таких прокси нет в базе, попробуйте еще раз")
    await message.delete()


@dp.callback_query_handler(text="pusk")
async def pusk_start(call: CallbackQuery):
    #await call.message.answer('Спам Начался')
    #await call.message.edit_text("🚀Выберете куда вы будете запускать вашу атаку!", reply_markup=start_spam_menu)
    tt = open('time.txt', 'r')
    ti = int(tt.read())
    tt.close()
    api_id = 7265064
    api_hash = "9ec54c3437a4b240456f08dd3276f5c3"
    file_list = os.listdir('sessions')
    xx = len(file_list)
    i = 0
    t = 0
    m = 0
    mx = 40
    msm = 0
    while i <= xx:
        mm = 0
        try:
            file_list = os.listdir('sessions')
            acaunt = file_list[i]
            client = TelegramClient(f"sessions/{acaunt}", api_id, api_hash)
            await client.connect() 
        except:
            await client.disconnect() 
            continue
        try:
            ssm = open('sms.txt', 'r').read()
            zz = ssm.split('|')
            sms = random.choice(zz)
        except:
            sms = "Нет текста для смс"
        try:
            ss = open('ussers.txt', 'r').readlines()
            z = len(ss)
            count = int(z)
        except:
            await call.message.answer('Список получателей пуст !')
            await client.disconnect() 
            break
        for x in range(count):
            try:
                if mm <= 5:
                    await client.send_message(ss[x][:-1], sms)
                    msm = msm + 1
                    mm = mm + 1
                    await call.message.edit_text(
                        f"<b>В Рассылку запущенно {xx} Акаунтов</b>\n"
                        f"<b>Подключен Акаунт №<code>{i}</code></b>\n"
                        f"<b>Отправляю этот текст:</b> \n\n"
                        f"<code>{sms}</code>\n"
                        f"<b>Пользователю:</b> <code>{ss[x][:-1]}</code>\n"
                        f"<b>Тайминг паузы установлен на {ti} секунд</b>\n"
                        f"<b>Всего отправленно смс:</b>    <code>{msm}</code>\n"
                    )
                    time.sleep(6)
            except:
                
                i = i + 1
                pass
        await client.disconnect() 
        i = i + 1

            
            
            
    await call.message.answer("✅ РАССЫЛКА УСПЕШНО ЗАВЕРШЕНА")
    
@dp.callback_query_handler(text_startswith="spam:")
async def start_spam(call: CallbackQuery, state: FSMContext):
    option = call.data.split(":")[1]
    if option == "chat":
        text = "🚀Введите ссылку на чат: (крайне не рекомендуется использовать для открытых чатов)"
        await SpamChat.S1.set()
    elif option == "user":
        text = "🚀Введите ссылку на пользователя которого хотите заспамить: "
        await SpamUser.S1.set()
    else:
        text = "🚀Введите ссылку на бота:"
        await SpamBot.S1.set()
    msg_to_edit = await call.message.edit_text(text, reply_markup=back_to_main_menu)
    await state.update_data(msg_to_edit=msg_to_edit)


@dp.message_handler(state=SpamBot.S1)
async def spam_chat(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get("msg_to_edit")
    url = message.text
    await SpamBot.next()
    await state.update_data(url=url)
    await msg_to_edit.edit_text(text="⏰Введите время задержки в секундах: (от 1 до 60)",
                                reply_markup=back_to_main_menu)
    await message.delete()


@dp.message_handler(state=SpamBot.S2)
async def spam_chat(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get("msg_to_edit")
    try:
        interval = int(message.text)
        if 1 <= interval <= 60:
            await SpamBot.next()
            await state.update_data(interval=interval)
            await msg_to_edit.edit_text(text="🔰Введите сколько секунд будет длиться атака:",
                                        reply_markup=back_to_main_menu)
        else:
            await msg_to_edit.answer("<b>Не верный формат</b>")
    except ValueError:
        await msg_to_edit.answer("<b>Не верный формат</b>")
    await message.delete()


@dp.message_handler(state=SpamBot.S3)
async def spam_chat(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit, url, msg_txt = data.get("msg_to_edit"), data.get("url"), data.get("msg_txt")
    interval, time = data.get("interval"), message.text
    await SpamBot.next()
    await state.update_data(time=time)
    await msg_to_edit.edit_text(text=f"<b>📨Проверьте введённые данные перед началом спама:</b>\n"
                                     f"◽️Услуга: 💬В чат\n"
                                     f"◽️Текст:\n{msg_txt}\n"
                                     f"◽️Фото: -\n"
                                     f"◽️Задержка: {interval} Секунд\n"
                                     f"◽️Время спама: {time} Секунд",
                                reply_markup=accept_spam_menu)
    await message.delete()


@dp.callback_query_handler(state=SpamBot.S4)
async def accept_spam(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_to_edit, url, msg_txt = data.get("msg_to_edit"), data.get("url"), data.get("msg_txt")
    interval, time = data.get("interval"), data.get("time")
    await state.finish()
    scheduler.add_job(
                send_message_to_chat,
                "interval", seconds=interval,
                args=(call.from_user.id, url, "/start"),
                id=f"{call.from_user.id}"
            )
    scheduler.add_job(stop_job, "date", run_date=datetime.now() + timedelta(seconds=int(time)),
                      args=(call.from_user.id,))
    await call.message.edit_text("<b>Спам-атака начата</b>", reply_markup=back_to_main_menu)
    await update_attacks()


@dp.message_handler(state=SpamUser.S1)
async def spam_chat(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get("msg_to_edit")
    url = message.text
    await SpamUser.next()
    await state.update_data(url=url)
    await msg_to_edit.edit_text(text="✉️Введите ваше сообщение которое будет отправляться:",
                                reply_markup=back_to_main_menu)
    await message.delete()


@dp.message_handler(state=SpamUser.S2)
async def spam_chat(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get("msg_to_edit")
    msg_txt = message.text
    await SpamUser.next()
    await state.update_data(msg_txt=msg_txt)
    await msg_to_edit.edit_text(text="⏰Введите время задержки в секундах: (от 1 до 60)",
                                reply_markup=back_to_main_menu)
    await message.delete()


@dp.message_handler(state=SpamUser.S3)
async def spam_chat(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get("msg_to_edit")
    try:
        interval = int(message.text)
        if 1 <= interval <= 60:
            await SpamUser.next()
            await state.update_data(interval=interval)
            await msg_to_edit.edit_text(text="🔰Введите сколько секунд будет длиться атака:",
                                        reply_markup=back_to_main_menu)
        else:
            await msg_to_edit.answer("<b>Не верный формат</b>")
    except ValueError:
        await msg_to_edit.answer("<b>Не верный формат</b>")
    await message.delete()


@dp.message_handler(state=SpamUser.S4)
async def spam_chat(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit, url, msg_txt = data.get("msg_to_edit"), data.get("url"), data.get("msg_txt")
    interval, time = data.get("interval"), message.text
    await SpamUser.next()
    await state.update_data(time=time)
    await msg_to_edit.edit_text(text=f"<b>📨Проверьте введённые данные перед началом спама:</b>\n"
                                     f"◽️Услуга: 💬В чат\n"
                                     f"◽️Текст:\n{msg_txt}\n"
                                     f"◽️Фото: -\n"
                                     f"◽️Задержка: {interval} Секунд\n"
                                     f"◽️Время спама: {time} Секунд",
                                reply_markup=accept_spam_menu)
    await message.delete()


@dp.callback_query_handler(state=SpamUser.S5)
async def accept_spam(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_to_edit, url, msg_txt = data.get("msg_to_edit"), data.get("url"), data.get("msg_txt")
    interval, time, photo = data.get("interval"), data.get("time"), data.get("photo")
    await state.finish()
    scheduler.add_job(
                send_message_to_chat,
                "interval", seconds=interval,
                args=(call.from_user.id, url, msg_txt),
                id=f"{call.from_user.id}"
            )
    scheduler.add_job(stop_job, "date", run_date=datetime.now() + timedelta(seconds=int(time)),
                      args=(call.from_user.id,))
    await call.message.edit_text("<b>Спам-атака начата</b>", reply_markup=back_to_main_menu)
    await update_attacks()


@dp.message_handler(state=SpamChat.S1)
async def spam_chat(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get("msg_to_edit")
    url = message.text
    await SpamChat.next()
    await state.update_data(url=url)
    await msg_to_edit.edit_text(text="✉️Введите ваше сообщение которое будет отправляться:",
                                reply_markup=back_to_main_menu)
    await message.delete()


@dp.message_handler(state=SpamChat.S2)
async def spam_chat(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get("msg_to_edit")
    msg_txt = message.text
    await SpamChat.next()
    await state.update_data(msg_txt=msg_txt)
    await msg_to_edit.edit_text(text="⏰Введите время задержки в секундах: (от 1 до 60)",
                                reply_markup=back_to_main_menu)
    await message.delete()


@dp.message_handler(state=SpamChat.S3)
async def spam_chat(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get("msg_to_edit")
    try:
        interval = int(message.text)
        if 1 <= interval <= 60:
            await SpamChat.next()
            await state.update_data(interval=interval)
            await msg_to_edit.edit_text(text="🔰Введите сколько секунд будет длиться атака:",
                                        reply_markup=back_to_main_menu)
        else:
            await msg_to_edit.answer("<b>Не верный формат</b>")
    except ValueError:
        await msg_to_edit.answer("<b>Не верный формат</b>")
    await message.delete()


@dp.message_handler(state=SpamChat.S4)
async def spam_chat(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get("msg_to_edit")
    try:
        time = int(message.text)
        await SpamChat.next()
        await state.update_data(time=time)
        await msg_to_edit.edit_text(text="🖼Введите ссылку на изображение:\n"
                                         "📖Создать можно тут: @photovip_rezerv_bot\n\n"
                                         "Напишите - чтобы пропустить.",
                                    reply_markup=back_to_main_menu)

    except ValueError:
        await msg_to_edit.answer("<b>Не верный формат</b>")
    await message.delete()


@dp.message_handler(state=SpamChat.S5)
async def spam_chat(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit, url, msg_txt = data.get("msg_to_edit"), data.get("url"), data.get("msg_txt")
    interval, time, photo = data.get("interval"), data.get("time"), message.text
    await SpamChat.next()
    if photo == "-":
        photo = None
    await state.update_data(photo=photo)
    await msg_to_edit.edit_text(text=f"<b>📨Проверьте введённые данные перед началом спама:</b>\n"
                                     f"◽️Услуга: 💬В чат\n"
                                     f"◽️Текст:\n{msg_txt}\n"
                                     f"◽️Фото: {photo}\n"
                                     f"◽️Задержка: {interval} Секунд\n"
                                     f"◽️Время спама: {time} Секунд",
                                reply_markup=accept_spam_menu)
    await message.delete()


@dp.callback_query_handler(state=SpamChat.S6)
async def accept_spam(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_to_edit, url, msg_txt = data.get("msg_to_edit"), data.get("url"), data.get("msg_txt")
    interval, time, photo = data.get("interval"), data.get("time"), data.get("photo")
    await state.finish()
    scheduler.add_job(
                send_message_to_chat,
                "interval", seconds=interval,
                args=(call.from_user.id, url, msg_txt, photo),
                id=f"{call.from_user.id}"
            )
    scheduler.add_job(stop_job, "date", run_date=datetime.now() + timedelta(seconds=time), args=(call.from_user.id,))
    await call.message.edit_text("<b>Спам-атака начата</b>", reply_markup=back_to_main_menu)
    await update_attacks()


# ===============ADD/CHANGE ACCOUNT===========
@dp.callback_query_handler(text="add_account")
async def show_all_chats(call: CallbackQuery, state: FSMContext):
    msg_to_edit = await call.message.edit_text("<b>Напишите номер аккаунта. В формате +380xxxxxxxxx</b>",
                                               reply_markup=back_to_main_menu)
    await AddAccount.A1.set()
    await state.update_data(msg_to_edit=msg_to_edit)


@dp.message_handler(state=AddAccount.A1)
async def receive_number(message: Message, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get("msg_to_edit")
    number = message.text
    await message.delete()
    if os.path.exists(f"sessions/{number}.session"):
        os.remove(f"sessions/{number}.session")
        await update_session(number, None)
    client = TelegramClient(f"sessions/{number}", api_id, api_hash)
    await client.connect()
    sent = await client.send_code_request(phone=number)
    await client.disconnect()
    await msg_to_edit.edit_text(f"<b>Вы указали <code>{number}</code>\n"
                                f"Укажите первую цифру кода:</b>",
                                reply_markup=code_menu)
    await AddAccount.next()
    await state.update_data(number=number, sent=sent, code_hash=sent.phone_code_hash)


@dp.callback_query_handler(text_startswith="code_number:", state=AddAccount.A2)
async def receive_code(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_to_edit = data.get("msg_to_edit")
    num_1 = call.data.split(":")[1]
    await msg_to_edit.edit_text(f"<b>Код будет выстраиваться тут: <code>{num_1}</code></b>", reply_markup=code_menu)
    await AddAccount.next()
    await state.update_data(num_1=num_1)


@dp.callback_query_handler(text_startswith="code_number:", state=AddAccount.A3)
async def receive_code(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_to_edit, num_1 = data.get("msg_to_edit"), data.get("num_1")
    num_2 = call.data.split(":")[1]
    code = num_1 + num_2
    await msg_to_edit.edit_text(f"<b>Код будет выстраиваться тут: <code>{code}</code></b>", reply_markup=code_menu)
    await AddAccount.next()
    await state.update_data(num_2=num_2)


@dp.callback_query_handler(text_startswith="code_number:", state=AddAccount.A4)
async def receive_code(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_to_edit, num_1, num_2 = data.get("msg_to_edit"), data.get("num_1"), data.get("num_2")
    num_3 = call.data.split(":")[1]
    code = num_1 + num_2 + num_3
    await msg_to_edit.edit_text(f"<b>Код будет выстраиваться тут: <code>{code}</code></b>", reply_markup=code_menu)
    await AddAccount.next()
    await state.update_data(num_3=num_3)


@dp.callback_query_handler(text_startswith="code_number:", state=AddAccount.A5)
async def receive_code(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_to_edit, num_1, num_2, num_3 = data.get("msg_to_edit"), data.get("num_1"), data.get("num_2"), data.get("num_3")
    num_4 = call.data.split(":")[1]
    code = num_1 + num_2 + num_3 + num_4
    await msg_to_edit.edit_text(f"<b>Код будет выстраиваться тут: <code>{code}</code></b>", reply_markup=code_menu)
    await AddAccount.next()
    await state.update_data(num_4=num_4)


@dp.callback_query_handler(state=AddAccount.A6)
async def receive_code(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    msg_to_edit, num_1, num_2, num_3 = data.get("msg_to_edit"), data.get("num_1"), data.get("num_2"), data.get("num_3")
    number, num_4, sent, code_hash = data.get("number"), data.get("num_4"), data.get("sent"), data.get("code_hash")
    num_5 = call.data.split(":")[1]
    code = num_1 + num_2 + num_3 + num_4 + num_5
    try:
        client = TelegramClient(f"sessions/{number}", api_id, api_hash)
        await client.connect()
        await client.sign_in(phone=number, code=code, phone_code_hash=code_hash)
        await client.disconnect()
        await update_session(call.from_user.id, call.from_user.id)
        await add_acc(call.from_user.id, number)
        await msg_to_edit.edit_text(f"<b>Готово, аккаунт добавлен</b>", reply_markup=back_to_main_menu)
        await update_acc_count()
        await state.finish()
    except Exception as e:
        print(e)
        await msg_to_edit.edit_text("Не верный код, или стоит облачный пароль, убери его и Попробуй заново.", reply_markup=back_to_main_menu)
        await state.finish()
