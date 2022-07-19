import datetime
import json
import logging
from aiogram import Bot, Dispatcher, executor, types
from os import getenv
from sys import exit
import requests
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import ContentType, ParseMode, InputTextMessageContent, InlineQueryResultArticle, \
    InlineQuery
import emoji
from Dictionaries import response, unic, previews

from aiogram.dispatcher.filters.state import State, StatesGroup

# from aiogram.utils.markdown import *
from Exceptions import get_geocoding_exceptions, get_searching_exceptions

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

lang = "en"


class CurrentForm(StatesGroup):
    city = State()


class DailyForm(StatesGroup):
    city = State()


weather_descriptions = {"01": f"{emoji.emojize(f':sun:')}",
                        "02": f"{emoji.emojize(f':sun_behind_small_cloud:')}",
                        "03": f"{emoji.emojize(f':sun_behind_cloud:')}",
                        "04": f"{emoji.emojize(f':cloud:')}",
                        "09": f"{emoji.emojize(f':cloud_with_rain:')}",
                        "10": f"{emoji.emojize(f':cloud_with_rain:')}",
                        "11": f"{emoji.emojize(f':cloud_with_lightning:')}",
                        "13": f"{emoji.emojize(f':cloud_with_snow:')}",
                        "50": f"{emoji.emojize(f':fog:')}"}


@dp.message_handler(commands=['daily'], content_types=[ContentType.TEXT])
async def process_daily_command(message: types.Message):
    print(message)
    city = " ".join(str(message.text).split(" ")[1:]).strip()
    if len(city) != 0:
        await get_daily(message, city)
    else:
        await DailyForm.city.set()
        await message.reply("Please, write name of the city or \"cancel\" to cancel the request.")


@dp.message_handler(commands=['settings'], content_types=[ContentType.TEXT])
async def process_settings_command(message: types.Message):
    await message.answer('Your settings:\n'
                         '\t daily:\n'
                         '\t current:')


@dp.message_handler(commands=['current'], content_types=[ContentType.TEXT])
async def process_current_command(message: types.Message):
    # print(datetime.datetime.now())
    print(message)
    city = " ".join(str(message.text).split(" ")[1:]).strip()
    print(city)
    if len(city) != 0:
        await get_current(message, city)
    else:
        await CurrentForm.city.set()
        await message.reply("Please, write name of the city or \"cancel\" to cancel the request.")


"""
@dp.message_handler(state=DailyForm.city)
async def process_daily_city(message: types.Message, state: FSMContext):
    await state.update_data(city=str(message.text))
    async with state.proxy() as data:
        await get_daily_weather(message, data["city"])

    # Finish conversation
    await state.finish()
"""


@dp.message_handler(commands=["help"])
async def process_help_command(message: types.Message):
    await message.answer("/current [city name] - current weather\n"
                         "/daily [city name] - daily weather forecast")


@dp.message_handler(commands=["about"])
async def process_about_command(message: types.Message):
    await message.answer("Weather Bot is @PythonEater personal bot, which will send daily and "
                         "week forecast. Work in progress.")


@dp.message_handler(content_types=ContentType.LOCATION)
async def process_geotag_command(message: types.Message):
    print(message)
    latitude, longitude = message["location"]["latitude"], message["location"]["longitude"]
    """city_req = json.loads(requests.get(f"https://api.openweathermap.org/geo/1.0/reverse"
                                   f"?lat={latitude}&lon={longitude}&limit=1&appid={KEY}").text)
    city_name = name_exception(city_req)"""
    req = json.loads(requests.get(
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={latitude}&lon={longitude}&units=metric&appid={KEY}").text)
    # &lang={message.from_user.language_code}
    match req['cod']:
        case '404' | 404 | '400' | 400 | '401' | 401:  # is 400 possible?
            await message.reply("Please, write name of the city.")
        case _:

            await message.reply(
                f'<b>{message["from"]["first_name"]}’s location'
                f' {round(float(req["main"]["temp"]))}\u00A0{"°C"}\n</b>'
                f'{emoji.emojize(f":thermometer:")}'
                f' {response[lang]["temp"]}:'
                f' {round(float(req["main"]["feels_like"]))}\u00A0°C\n'
                f'{weather_descriptions[str(req["weather"][0]["icon"])[:-1]]}'
                f' {str(req["weather"][0]["description"]).capitalize()}\n'
                f'{emoji.emojize(f":dashing_away:")}'
                f' {response[lang]["wind"]}:'
                f' {req["wind"]["speed"]}\u00A0m/s,\n'
                f'{emoji.emojize(f":droplet:")}'
                f' {response[lang]["hum"]}:'
                f' {req["main"]["humidity"]}%.'.lstrip(),
                parse_mode=ParseMode.HTML)


@dp.message_handler(state=[CurrentForm.city, DailyForm.city], commands='cancel')
@dp.message_handler(Text(equals='cancel', ignore_case=True), state=[CurrentForm.city, DailyForm.city])
async def cancel_handler(message: types.Message, state: FSMContext):
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info('Cancelling state %r', current_state)
    # Cancel state and inform user about it
    await state.finish()
    # And remove keyboard (just in case)
    await message.reply('Cancelled.')


@dp.message_handler(state=DailyForm.city)
async def get_daily_weather(message: types.Message, state: FSMContext):
    city = message.text
    if city.isnumeric() or "&" in city or "#" in city:
        return await message.reply("Please, write name of the city or \"cancel\" to cancel the request.")
    else:
        if len(city) > 150:  # city name must be less than 150 chars
            return await message.reply("Error: long name of the city.")
        else:
            city_req = json.loads(
                requests.get(f"https://api.openweathermap.org/geo/1.0/direct"
                             f"?q={city}"
                             f"&limit=1&appid={KEY}").text)  # here was To Do
            if 'cod' in city_req:
                match city_req['cod']:
                    case '404' | 404:
                        return await message.reply("Please, write name of the city.")
            if len(city_req) != 0:
                req = json.loads(
                    requests.get(
                        f"https://api.openweathermap.org/data/2.5/onecall"
                        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}"
                        f"&units=metric&appid={KEY}").text)
                await fun_daily(message, city_req, req)
                await state.finish()
            else:
                return await message.reply(
                    "Please, write name of the city or \"cancel\" to cancel the request.")


@dp.message_handler(state=CurrentForm.city)
async def get_current_weather_form(message, state: FSMContext):
    city = message.text
    print(city)
    if city.isnumeric() or "&" in city or "#" in city:
        return await message.reply("Please, write name of the city.")
    else:
        if len(city) > 150:  # WTF IS THAT??? city name must be less than 150 chars
            return await message.reply("Error: long name of the city.")
        else:
            city_req = json.loads(
                requests.get(f"https://api.openweathermap.org/geo/1.0/direct"
                             f"?q={city}"
                             f"&limit=1&appid={KEY}").text)
            print(city_req)
            if 'cod' in city_req:
                match city_req['cod']:
                    case '404' | 404:
                        await message.reply('Please, write name of the city.')
                        return
            if len(city_req) != 0:
                req = json.loads(
                    requests.get(
                        f"https://api.openweathermap.org/data/2.5/weather"
                        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}&lang={lang}"
                        f"&units=metric&appid={KEY}").text)
                print(req)
                match req["cod"]:
                    case '404' | 404 | '400' | 400:
                        # await message.reply(req["message"].capitalize() + '.')
                        await message.reply("Error 404: city not found")
                    case '401' | 401:
                        await message.reply("Please, write name of the city.")
                        # await message.reply("Invalid API key.")
                    case _:
                        await fun(message, city_req, req)
                        await state.finish()
            else:
                return await message.reply(
                    "Please, write name of the city or \"cancel\" to cancel the request.")


async def get_current(message, city: str):
    if city.isnumeric() or "&" in city or "#" in city:
        return await message.reply("Please, write name of the city.")
    else:
        if len(city) > 150:  # WTF IS THAT??? city name must be less than 150 chars
            return await message.reply("Error: long name of the city.")
        else:
            city_req = json.loads(
                requests.get(f"https://api.openweathermap.org/geo/1.0/direct"
                             f"?q={city}"
                             f"&limit=1&appid={KEY}").text)
            print(city_req)
            if 'cod' in city_req:
                match city_req['cod']:
                    case '404' | 404:
                        await message.reply('Please, write name of the city.')
                        return
            if len(city_req) != 0:
                req = json.loads(
                    requests.get(
                        f"https://api.openweathermap.org/data/2.5/weather"
                        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}&lang={lang}"
                        f"&units=metric&appid={KEY}").text)
                print(req)
                match req["cod"]:
                    case '404' | 404 | '400' | 400:
                        # await message.reply(req["message"].capitalize() + '.')
                        await message.reply("Error 404: city not found")
                    case '401' | 401:
                        await message.reply("Please, write name of the city.")
                        # await message.reply("Invalid API key.")
                    case _:
                        await fun(message, city_req, req)
            else:
                await CurrentForm.city.set()
                return await message.reply(
                    "Please, write name of the city or \"cancel\" to cancel the request.")


async def get_daily(message: types.Message, city: str):
    if city.isnumeric() or "&" in city or "#" in city:
        await DailyForm.city.set()
        await message.reply("Please, write name of the city or \"cancel\" to cancel the request.")
    else:
        if len(city) > 150:  # city name must be less than 150 chars
            await message.reply("Error: long name of the city.")
            return
        else:
            city_req = json.loads(
                requests.get(f"https://api.openweathermap.org/geo/1.0/direct"
                             f"?q={city}"
                             f"&limit=1&appid={KEY}").text)  # here was To Do
            if 'cod' in city_req:
                match city_req['cod']:
                    case '404' | 404:
                        await message.reply("Please, write name of the city.")
                        return
            if len(city_req) != 0:
                req = json.loads(
                    requests.get(
                        f"https://api.openweathermap.org/data/2.5/onecall"
                        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}"
                        f"&units=metric&appid={KEY}").text)
                await fun_daily(message, city_req, req)
            else:
                await DailyForm.city.set()
                await message.reply(
                    "Please, write name of the city or \"cancel\" to cancel the request.")


def name_exception(req):
    try:  # ToDo
        city = req[0]["local_names"][lang]
    except KeyError:
        city = req[0]["name"]
    return city

def name_exception_inline(req):
    try:  # ToDo
        city = req["local_names"][lang]
    except KeyError:
        city = req["name"]
    return city

def catch_error(code) -> bool:
    match code:
        case '404' | 404 | '400' | 400 | '401' | 401:  # is 400 possible?
            return False
        case _:
            return True


"""
def req(city):
    request = json.loads(
        requests.get(f"https://api.openweathermap.org/data/2.5/weather"
                     f"?q={city}&units=metric&appid={KEY}").text)
    if request["cod"] == "404":
        print('error')
    return req
"""


async def fun(message, city_req, req):
    city_name = name_exception(city_req)
    await message.reply(
        f'{emoji.emojize(f":cityscape:")} '
        f'<b>'
        f'{city_name}'
        f' {round(float(req["main"]["temp"]))}\u00A0{"°C"}\n'
        f'</b>'
        f'{emoji.emojize(f":thermometer:")} '
        f'{response[lang]["temp"]}:'
        f' {round(float(req["main"]["feels_like"]))}\u00A0°C\n'
        f'{weather_descriptions[str(req["weather"][0]["icon"])[:-1]]}'
        f' {str(req["weather"][0]["description"]).capitalize()}\n'
        f'{emoji.emojize(f":dashing_away:")} '
        f'{response[lang]["wind"]}:'
        f' {req["wind"]["speed"]}\u00A0{response[lang]["metrics"]}\n'
        f'{emoji.emojize(f":droplet:")} '
        f'{response[lang]["hum"]}: '
        f'{req["main"]["humidity"]}%',
        parse_mode=ParseMode.HTML)


async def fun_daily(message, city_req, req):
    city_name = name_exception(city_req)
    await message.reply(
        f'{emoji.emojize(f":cityscape:")} '
        f'<b>{city_name}</b>\n\n' + "\n".join(
            str(emoji.emojize(f":keycap_{i + 1}:") + " " +
                f"<b>"
                + datetime.datetime.fromtimestamp(
                req["daily"][i]["dt"]).strftime(
                '%B %d, %A')) +
            f"</b>" +
            f":\n    {emoji.emojize(':sun:')} "
            f"Morning: "
            f"{round(float(req['daily'][i]['temp']['morn']))}"
            f"\u00A0°C,"
            f" Day: "
            f"{round(float(req['daily'][i]['temp']['day']))}"
            f"\u00A0°C."
            f"\n    {emoji.emojize(':new_moon_face:')} "
            f"Eve: "
            f"{round(float(req['daily'][i]['temp']['eve']))}"
            f"\u00A0°C,"
            f" Night: "
            f"{round(float(req['daily'][i]['temp']['night']))}"
            f"\u00A0°C.\n"
            for i in range(len(req["daily"]) - 1)),
        parse_mode=ParseMode.HTML)


async def get_current_inline(city: str):
    if city.isnumeric() or "&" in city or "#" in city:
        return
    else:
        if len(city) > 150:  # WTF IS THAT??? city name must be less than 150 chars
            return
        else:
            city_req = json.loads(
                requests.get(f"https://api.openweathermap.org/geo/1.0/direct"
                             f"?q={city}"
                             f"&limit=1&appid={KEY}").text)
            print(city_req)
            if 'cod' in city_req:
                match city_req['cod']:
                    case '404' | 404:
                        return
            if len(city_req) != 0:
                req = json.loads(
                    requests.get(
                        f"https://api.openweathermap.org/data/2.5/weather"
                        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}&lang={lang}"
                        f"&units=metric&appid={KEY}").text)
                print(req)
                match req["cod"]:
                    case '404' | 404 | '400' | 400:
                        # await message.reply(req["message"].capitalize() + '.')
                        return
                    case '401' | 401:
                        return
                        # await message.reply("Invalid API key.")
                    case _:
                        return fun_inline(city_req, req)
            else:
                return


def fun_inline(city_req, req) -> str:
    city_name = name_exception_inline(city_req)
    flag = unic[city_req["country"][0]] + unic[city_req["country"][1]]
    print(flag)
    return (flag + " " +
            f'<b>'
            f'{city_name}'
            f' {round(float(req["main"]["temp"]))}\u00A0{"°C"}\n'
            f'</b>'
            f'{emoji.emojize(f":thermometer:")} '
            f'{response[lang]["temp"]}:'
            f' {round(float(req["main"]["feels_like"]))}\u00A0°C\n'
            f'{weather_descriptions[str(req["weather"][0]["icon"])[:-1]]}'
            f' {str(req["weather"][0]["description"]).capitalize()}\n'
            f'{emoji.emojize(f":dashing_away:")} '
            f'{response[lang]["wind"]}:'
            f' {req["wind"]["speed"]}\u00A0{response[lang]["metrics"]}\n'
            f'{emoji.emojize(f":droplet:")} '
            f'{response[lang]["hum"]}: '
            f'{req["main"]["humidity"]}%')


@dp.inline_handler()
async def inline_echo(inline_query: InlineQuery) -> None:
    result = []
    city = inline_query.query
    city_words = city.split()
    city_req = json.loads(
        requests.get(f"https://api.openweathermap.org/geo/1.0/direct"
                     f"?q={city}"
                     f"&limit=5&appid={KEY}").text)
    city_list = []
    print(city_req)
    for ci in city_req:
        if "local_names" in ci:
            for c in city_words:
                flag = False
                for name in ci["local_names"].values():
                    if c.lower() in name.lower():
                        flag = True
                        city_list.append(ci)
                        break
                if flag:
                    break

    city_req = city_list
    print(city_req)

    for num in range(len(city_req)):
        # if city not in city_req[num]["local_names"]:
        #    continue
        if get_geocoding_exceptions(city_req[num]) is None:
            req = json.loads(
                requests.get(
                    f"https://api.openweathermap.org/data/2.5/weather"
                    f"?lat={city_req[num]['lat']}&lon={city_req[num]['lon']}&lang={lang}"
                    f"&units=metric&appid={KEY}").text)
            answer = fun_inline(city_req[num], req)
            input_content = InputTextMessageContent(answer, parse_mode=ParseMode.HTML)
            if get_searching_exceptions(req) is None:
                result.append(InlineQueryResultArticle(id=f"{num}",
                                                       title=f'{emoji.emojize(":cityscape:")} {name_exception_inline(city_req[num]).upper()} ',
                                                       input_message_content=input_content,
                                                       description=f"{city_req[num]['country']}, "
                                                                   f"{city_req[num]['state'] if 'state' in city_req[num] else city_req[num]['country']}.",
                                                       thumb_url=previews[
                                                           str(req["weather"][0]["icon"])[:-1]], ))
    await inline_query.answer(result, cache_time=1, is_personal=True)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
