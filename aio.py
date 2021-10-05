import json
import logging
from aiogram import Bot, Dispatcher, executor, types
from os import getenv
from sys import exit
import requests
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters import Text, state
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentType
import emoji

bot_token = getenv("BOT_TOKEN")
KEY = getenv("OWM_KEY")
if not bot_token:
    exit("Error: no token provided")
if not KEY:
    exit("Error: no API key provided")

bot = Bot(token=bot_token)

logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

buttons = [f"English {emoji.emojize(':United_States:')}",
           f"Русский {emoji.emojize(':Russia:')}"]


class ChooseLanguage(StatesGroup):
    language = State()  # Will be represented in storage as 'Form:name'


@dp.message_handler(commands=['weather'], content_types=[ContentType.TEXT])
async def weather_request(message: types.Message):
    print(message)
    city = str(message["text"]).lstrip("/weather ")
    cities = json.loads(requests.get(f"http://api.openweathermap.org/geo/1.0/direct"
                                     f"?q={city}&limit=3&appid={KEY}").text)  # ToDo
    for cit in cities:
        try:
            print(cit['state'])  # ToDo
        except KeyError:
            pass
        print(cit)
    if len(city) != 0:
        if city.isnumeric():
            await message.reply("Please, write name of the city.")
        else:
            req = json.loads(
                requests.get(
                    f"http://api.openweathermap.org/data/2.5/weather"
                    f"?q={city}&units=metric&appid={KEY}").text)
            print(req)

            match req["cod"]:
                case '404':
                    await message.reply(req["message"])
                case _:
                    await message.reply(
                        f'City: {req["name"]},\nTemperature: {round(float(req["main"]["temp"]))}°C,\n'
                        f'Wind speed: {req["wind"]["speed"]}m/s,\nHumidity: {req["main"]["humidity"]}%.')
    else:
        await message.reply("Please, write name of the city.")


"""
@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await ChooseLanguage.language.set()
    await message.answer(
        "Welcome to Weather Bot!\n\nSend geotag or write '/weather {city_name}' for current weather data.")
"""


@dp.message_handler(commands="start")
async def cmd_start(message: types.Message):
    await ChooseLanguage.language.set()
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text=buttons[0], callback_data="language_en"),
                 types.InlineKeyboardButton(text=buttons[1], callback_data="language_ru"))
    await message.answer("Choose language", reply_markup=keyboard)


@dp.callback_query_handler(Text(startswith="language"), state=ChooseLanguage)
async def process_language(call: types.CallbackQuery, statement: FSMContext):
    print(call)
    print(call.data)
    print(call.data.split('_')[1])  # ru or en
    """async with state.proxy() as data:
        data = call.data.split('_')[1]"""
    data = call.data.split('_')[1]
    await statement.finish()
    await call.message.delete()
    await call.answer()
    if data == "ru":
        await call.message.answer("I know only English now, sorry:)")
    elif data == "en":
        await call.message.answer("Good choice!")
    """async with state.proxy() as data:
        if call.message.text not in buttons:
            await call.message.reply("Please, choose language using buttons.")
            await call.answer()
            return
        data['language'] = call.message.text
    await state.finish()
    print(data['language'])
    await call.message.answer("I know only English now, sorry:)" if data['language'] == buttons[1] 
    else "Good!", reply_markup=types.ReplyKeyboardRemove())
    await call.answer()"""


@dp.message_handler(commands="help")
async def cmd_help(message: types.Message):
    await message.answer("Weather Bot is @PythonEater personal bot, which will send daily and "
                         "week forecast. Work in progress.")


"""
@dp.message_handler(content_types=ContentType.TEXT)
async def answer(message: types.Message):
    print(message)
    print(message.text)
    await message.answer(
        f"Hello, <b>{'@' + message.from_user.username if message.from_user.username is not None else
         message.from_user.first_name}</b>!\n",
        parse_mode=types.ParseMode.HTML)"""


@dp.message_handler(content_types=ContentType.LOCATION)
async def cmd_geotag_message(message: types.Message):
    print(message)
    latitude, longitude = message["location"]["latitude"], message["location"]["longitude"]
    req = json.loads(requests.get(
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?lat={latitude}&lon={longitude}&units=metric&appid={KEY}").text)
    print(req)
    # &lang={message.from_user.language_code}
    match req['cod']:
        case '404':
            await message.reply(req["message"])
            # await message.reply("Неверно введённый город или неправильно построенный запрос")
        case '401':
            await message.reply("Превышен лимит запросов")
        case '429':
            await message.reply(
                "Превышено количество запросов в минуту. Пожалуйста, отправьте ваш запрос позже.")
        case '500' | '502' | '503' | '504':  # ToDo
            await message.reply('Unknown error.')
        case _:
            await message.reply(
                f'{"City: " + req["name"] + "," if req["name"] != "" else ""}\n'
                f'Temperature: {round(float(req["main"]["temp"]))}°C,\n'
                f'Wind speed: {req["wind"]["speed"]}m/s,\n'
                f'Humidity: {req["main"]["humidity"]}%.'.lstrip())
    """
    if req["cod"] in ["400", "404"]:
        await message.reply(req["message"])
    else:
        await message.reply(
            f'{"City: " + req["name"] + "," if req["name"] != "" else ""}\n'
            f'Temperature: {round(float(req["main"]["temp"]))}°C,\nWind speed: {req["wind"]["speed"]}m/s,\n'
            f'Humidity: {req["main"]["humidity"]}%.'.lstrip())"""


"""
@dp.message_handler(content_types=ContentType.ANY)
async def unknown_message(message: types.Message):
    print(message)
    await message.reply("Sorry! Bot understand only geotag and commands /help and /weather.")
"""

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
