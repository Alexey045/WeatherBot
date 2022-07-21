from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ContentType, ParseMode, InputTextMessageContent, InlineQueryResultArticle, \
    InlineQuery

from orjson import loads
# from aiohttp import ClientSession
from datetime import datetime
import logging
from os import getenv
from sys import exit
# import requests
from emoji import emojize
from Dictionaries import response, unicode_reg_sym, previews, weather_descriptions
from Exceptions import get_geocoding_exceptions, get_searching_exceptions, name_exception

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

lang: str = "en"


class CurrentForm(StatesGroup):
    city = State()


class DailyForm(StatesGroup):  # ToDo
    city = State()


@dp.message_handler(commands=['daily'], content_types=[ContentType.TEXT])
async def process_daily_command(message: types.Message) -> None:
    print(message)
    city = " ".join(str(message.text).split(" ")[1:]).strip()
    if len(city) != 0:
        await get_daily(message, city)
    else:
        await DailyForm.city.set()
        await message.reply("Please, write name of the city or /cancel to cancel the request.")


@dp.message_handler(commands=['settings'], content_types=[ContentType.TEXT])
async def process_settings_command(message: types.Message) -> None:
    await message.answer('Your settings:\n'
                         '\t daily:\n'
                         '\t current:')


@dp.message_handler(commands=['current'], content_types=[ContentType.TEXT])
async def process_current_command(message: types.Message) -> None:
    print(message)
    city = " ".join(str(message.text).split(" ")[1:]).strip()
    print(city)
    if len(city) != 0:
        await get_current(message, city)
    else:
        await CurrentForm.city.set()
        await message.reply("Please, write name of the city or \"cancel\" to cancel the request.")


@dp.message_handler(commands=["help"])
async def process_help_command(message: types.Message) -> None:
    await message.answer("/current [city name] - current weather\n"
                         "/daily [city name] - daily weather forecast")


@dp.message_handler(commands=["about"])
async def process_about_command(message: types.Message) -> None:
    await message.answer("Weather Bot is @PythonEater personal bot, which will send daily and "
                         "week forecast. Work in progress.")


@dp.message_handler(content_types=ContentType.LOCATION)
async def process_geotag_command(message: types.Message) -> None:
    print(message)
    latitude, longitude = message["location"]["latitude"], message["location"]["longitude"]
    req = loads(await fetch(f"https://api.openweathermap.org/data/2.5/weather"
                            f"?lat={latitude}&lon={longitude}&units=metric&appid={KEY}",
                            await bot.get_session()))
    # async with ClientSession() as session:
    #    async with session.get(f"https://api.openweathermap.org/data/2.5/weather"
    #                           f"?lat={latitude}&lon={longitude}&units=metric&appid={KEY}") as request:
    #        req = loads(await request.text())
    match req['cod']:
        case '404' | 404 | '400' | 400 | '401' | 401:  # is 400 possible?
            await message.reply("Please, write name of the city.")
        case _:

            await message.reply(
                f'<b>{message["from"]["first_name"]}’s location'
                f' {round(float(req["main"]["temp"]))}\u00A0{"°C"}\n</b>'
                f'{emojize(f":thermometer:")}'
                f' {response[lang]["temp"]}:'
                f' {round(float(req["main"]["feels_like"]))}\u00A0°C\n'
                f'{weather_descriptions[str(req["weather"][0]["icon"])[:-1]]}'
                f' {str(req["weather"][0]["description"]).capitalize()}\n'
                f'{emojize(f":dashing_away:")}'
                f' {response[lang]["wind"]}:'
                f' {req["wind"]["speed"]}\u00A0m/s,\n'
                f'{emojize(f":droplet:")}'
                f' {response[lang]["hum"]}:'
                f' {req["main"]["humidity"]}%.'.lstrip(),
                parse_mode=ParseMode.HTML)


@dp.message_handler(state=[CurrentForm.city, DailyForm.city], commands='cancel')  # ToDo
async def cancel_handler(message: types.Message, state: FSMContext) -> None:
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
    # await message.delete()


@dp.message_handler(state=DailyForm.city)
async def get_daily_weather(message: types.Message, state: FSMContext) -> None:
    city = message.text
    if city.isnumeric() or "&" in city or "#" in city:
        return
    #  return await message.reply("Please, write name of the city or \"cancel\" to cancel the request.")
    else:
        if len(city) > 150:  # city name must be less than 150 chars
            await message.reply("Error: long name of the city.")
            return
        else:
            city_req = loads(await fetch(f"https://api.openweathermap.org/geo/1.0/direct"
                                         f"?q={city}"
                                         f"&limit=1&appid={KEY}",
                                         await bot.get_session()))
            # city_req = loads(
            #    requests.get(f"https://api.openweathermap.org/geo/1.0/direct"
            #                 f"?q={city}"
            #                 f"&limit=1&appid={KEY}").text)  # here was To Do
            if 'cod' in city_req:
                match city_req['cod']:
                    case '404' | 404:
                        await message.reply("Please, write name of the city.")
                        return
            if len(city_req) != 0:
                req = loads(await fetch(f"https://api.openweathermap.org/data/2.5/onecall"
                                        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}"
                                        f"&units=metric&appid={KEY}", await bot.get_session()))
                # req = loads(
                #    requests.get(
                #        f"https://api.openweathermap.org/data/2.5/onecall"
                #        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}"
                #        f"&units=metric&appid={KEY}").text)
                await fun_daily(message, city_req[0], req)
                await state.finish()
            else:
                return
                # return await message.reply(
                #    "Please, write name of the city or \"cancel\" to cancel the request.")


@dp.message_handler(state=CurrentForm.city)
async def get_current_weather_form(message, state: FSMContext) -> None:
    city = message.text
    print(city)
    if city.isnumeric() or "&" in city or "#" in city:
        await message.reply("Please, write name of the city.")
        return
    else:
        if len(city) > 150:  # WTF IS THAT??? city name must be less than 150 chars
            await message.reply("Error: long name of the city.")
            return
        else:
            city_req = loads(await fetch(f"https://api.openweathermap.org/geo/1.0/direct"
                                         f"?q={city}"
                                         f"&limit=1&appid={KEY}",
                                         await bot.get_session()))
            # city_req = loads(
            #    requests.get(f"https://api.openweathermap.org/geo/1.0/direct"
            #                 f"?q={city}"
            #                 f"&limit=1&appid={KEY}").text)
            print(city_req)
            if 'cod' in city_req:
                match city_req['cod']:
                    case '404' | 404:
                        await message.reply('Please, write name of the city.')
                        return
            if len(city_req) != 0:
                req = loads(await fetch(f"https://api.openweathermap.org/data/2.5/weather"
                                        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}&lang={lang}"
                                        f"&units=metric&appid={KEY}", await bot.get_session()))
                # req = loads(
                #    requests.get(
                #        f"https://api.openweathermap.org/data/2.5/weather"
                #        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}&lang={lang}"
                #        f"&units=metric&appid={KEY}").text)
                print(req)
                match req["cod"]:
                    case '404' | 404 | '400' | 400:
                        # await message.reply(req["message"].capitalize() + '.')
                        await message.reply("Error 404: city not found")
                    case '401' | 401:
                        await message.reply("Please, write name of the city.")
                        # await message.reply("Invalid API key.")
                    case _:
                        await message.reply(fun(city_req[0], req), parse_mode=ParseMode.HTML)
                        await state.finish()
            else:
                return
                # return await message.reply(
                #    "Please, write name of the city or \"cancel\" to cancel the request.")


async def get_current(message: types.Message, city: str):  # ToDo
    if city.isnumeric() or "&" in city or "#" in city:
        return await message.reply("Please, write name of the city.")
    else:
        if len(city) > 150:  # WTF IS THAT??? city name must be less than 150 chars
            return await message.reply("Error: long name of the city.")
        else:
            city_req = loads(await fetch(f"https://api.openweathermap.org/geo/1.0/direct"
                                         f"?q={city}"
                                         f"&limit=1&appid={KEY}",
                                         await bot.get_session()))
            # city_req = loads(
            #    requests.get(f"https://api.openweathermap.org/geo/1.0/direct"
            #                 f"?q={city}"
            #                 f"&limit=1&appid={KEY}").text)
            print(city_req)
            if 'cod' in city_req:
                match city_req['cod']:
                    case '404' | 404:
                        await message.reply('Please, write name of the city.')
                        return
            if len(city_req) != 0:
                req = loads(await fetch(f"https://api.openweathermap.org/data/2.5/weather"
                                        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}&lang={lang}"
                                        f"&units=metric&appid={KEY}", await bot.get_session()))
                # req = loads(
                #    requests.get(
                #        f"https://api.openweathermap.org/data/2.5/weather"
                #        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}&lang={lang}"
                #        f"&units=metric&appid={KEY}").text)
                print(req)
                match req["cod"]:
                    case '404' | 404 | '400' | 400:
                        # await message.reply(req["message"].capitalize() + '.')
                        await message.reply("Error 404: city not found")
                    case '401' | 401:
                        await message.reply("Please, write name of the city.")
                        # await message.reply("Invalid API key.")
                    case _:
                        await message.reply(fun(city_req[0], req), parse_mode=ParseMode.HTML)
            else:
                await CurrentForm.city.set()
                return await message.reply(
                    "Please, write name of the city or \"cancel\" to cancel the request.")


async def get_daily(message: types.Message, city: str):  # ToDo
    if city.isnumeric() or "&" in city or "#" in city:
        await DailyForm.city.set()
        await message.reply("Please, write name of the city or \"cancel\" to cancel the request.")
    else:
        if len(city) > 150:  # city name must be less than 150 chars
            await message.reply("Error: long name of the city.")
            return
        else:
            city_req = loads(await fetch(f"https://api.openweathermap.org/geo/1.0/direct"
                                         f"?q={city}"
                                         f"&limit=1&appid={KEY}",
                                         await bot.get_session()))
            # city_req = loads(
            #    requests.get(f"https://api.openweathermap.org/geo/1.0/direct"
            #                 f"?q={city}"
            #                 f"&limit=1&appid={KEY}").text)  # here was To Do
            if 'cod' in city_req:
                match city_req['cod']:
                    case '404' | 404:
                        await message.reply("Please, write name of the city.")
                        return
            if len(city_req) != 0:
                req = loads(await fetch(f"https://api.openweathermap.org/data/2.5/onecall"
                                        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}"
                                        f"&units=metric&appid={KEY}", await bot.get_session()))
                # req = loads(
                #    requests.get(
                #        f"https://api.openweathermap.org/data/2.5/onecall"
                #        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}"
                #        f"&units=metric&appid={KEY}").text)
                await fun_daily(message, city_req[0], req)
            else:
                await DailyForm.city.set()
                await message.reply(
                    "Please, write name of the city or \"cancel\" to cancel the request.")


async def fun_daily(message: types.Message, city_req: dict, req: dict) -> None:
    city_name = name_exception(city_req)
    flag = get_flag_emoji(city_req["country"])
    await message.reply(
        f'{flag} '
        f'<b>{city_name}</b>\n\n' + "\n".join(
            str(emojize(f":keycap_{i + 1}:") + " " +
                f"<b>"
                + datetime.fromtimestamp(
                req["daily"][i]["dt"]).strftime(
                '%B %d, %A')) +
            f"</b>" +
            f":\n    {emojize(':sun:')} "
            f"Morning: "
            f"{round(float(req['daily'][i]['temp']['morn']))}"
            f"\u00A0°C,"
            f" Day: "
            f"{round(float(req['daily'][i]['temp']['day']))}"
            f"\u00A0°C."
            f"\n    {emojize(':new_moon_face:')} "
            f"Eve: "
            f"{round(float(req['daily'][i]['temp']['eve']))}"
            f"\u00A0°C,"
            f" Night: "
            f"{round(float(req['daily'][i]['temp']['night']))}"
            f"\u00A0°C.\n"
            for i in range(len(req["daily"]) - 1)),
        parse_mode=ParseMode.HTML)


async def get_current_inline(city: str):  # ToDo
    if city.isnumeric() or "&" in city or "#" in city:
        return
    else:
        if len(city) > 150:  # WTF IS THAT??? city name must be less than 150 chars
            return
        else:
            city_req = loads(await fetch(f"https://api.openweathermap.org/geo/1.0/direct"
                                         f"?q={city}"
                                         f"&limit=1&appid={KEY}",
                                         await bot.get_session()))
            # city_req = loads(
            #    requests.get(f"https://api.openweathermap.org/geo/1.0/direct"
            #                 f"?q={city}"
            #                 f"&limit=1&appid={KEY}").text)
            print(city_req)
            if 'cod' in city_req:
                match city_req['cod']:
                    case '404' | 404:
                        return
            if len(city_req) != 0:
                req = loads(await fetch(f"https://api.openweathermap.org/data/2.5/weather"
                                        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}&lang={lang}"
                                        f"&units=metric&appid={KEY}", await bot.get_session()))
                # req = loads(
                #    requests.get(
                #        f"https://api.openweathermap.org/data/2.5/weather"
                #        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}&lang={lang}"
                #        f"&units=metric&appid={KEY}").text)
                print(req)
                match req["cod"]:
                    case '404' | 404 | '400' | 400:
                        # await message.reply(req["message"].capitalize() + '.')
                        return
                    case '401' | 401:
                        return
                        # await message.reply("Invalid API key.")
                    case _:
                        return fun(city_req, req)
            else:
                return


def fun(city_req: dict, req: dict) -> str:  # ToDo rename function
    city_name = name_exception(city_req)
    flag: str = get_flag_emoji(city_req["country"])
    return (flag + " " +
            f'<b>'
            f'{city_name}'
            f' {round(float(req["main"]["temp"]))}\u00A0{"°C"}\n'
            f'</b>'
            f'{emojize(f":thermometer:")} '
            f'{response[lang]["temp"]}:'
            f' {round(float(req["main"]["feels_like"]))}\u00A0°C\n'
            f'{weather_descriptions[str(req["weather"][0]["icon"])[:-1]]}'
            f' {str(req["weather"][0]["description"]).capitalize()}\n'
            f'{emojize(f":dashing_away:")} '
            f'{response[lang]["wind"]}:'
            f' {req["wind"]["speed"]}\u00A0{response[lang]["metrics"]}\n'
            f'{emojize(f":droplet:")} '
            f'{response[lang]["hum"]}: '
            f'{req["main"]["humidity"]}%')


@dp.inline_handler()
async def inline_search(inline_query: InlineQuery) -> None:
    result = []
    city = inline_query.query
    if len(city) == 0:
        return
    city_words = city.split()
    city_req = loads(await fetch(f"https://api.openweathermap.org/geo/1.0/direct"
                                 f"?q={city}"
                                 f"&limit=5&appid={KEY}",
                                 await bot.get_session()))
    # city_req = loads(
    #    requests.get(f"https://api.openweathermap.org/geo/1.0/direct"
    #                 f"?q={city}"
    #                 f"&limit=5&appid={KEY}").text)
    city_list = []
    previous_country = ""
    previous_state = ""
    for ci in city_req:
        country = ci["country"]
        state = ci["state"] if "state" in ci else "1"
        if previous_state == state and previous_country == country:
            continue
        if city.lower() in ci["name"].lower():
            city_list.append(ci)
            continue
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
        previous_country = ci["country"]
        previous_state = ci["state"] if "state" in ci else ""

    city_req = city_list

    for num in range(len(city_req)):
        if get_geocoding_exceptions(city_req[num]) is None:
            req = loads(await fetch(f"https://api.openweathermap.org/data/2.5/weather"
                                    f"?lat={city_req[num]['lat']}&lon={city_req[num]['lon']}&lang={lang}"
                                    f"&units=metric&appid={KEY}", await bot.get_session()))
            # req = loads(
            #    requests.get(
            #        f"https://api.openweathermap.org/data/2.5/weather"
            #        f"?lat={city_req[num]['lat']}&lon={city_req[num]['lon']}&lang={lang}"
            #        f"&units=metric&appid={KEY}").text)
            answer = fun(city_req[num], req)
            input_content = InputTextMessageContent(answer, parse_mode=ParseMode.HTML)
            if get_searching_exceptions(req) is None:
                result.append(InlineQueryResultArticle(id=f"{num}",
                                                       title=f'{emojize(":cityscape:")}'
                                                             f' {name_exception(city_req[num]).upper()} ',
                                                       input_message_content=input_content,
                                                       description=f"{city_req[num]['country']}, "
                                                                   f"{get_city_state(city_req[num])}.",
                                                       thumb_url=previews[
                                                           str(req["weather"][0]["icon"])[:-1]], ))
    await inline_query.answer(result, cache_time=1, is_personal=True)


async def fetch(url, session):
    async with session.get(url) as request:
        return await request.text()


def get_city_state(city: dict) -> str:
    return city['state'] if 'state' in city else city['country']


def get_flag_emoji(country: str) -> str:
    return unicode_reg_sym[country[0]] + unicode_reg_sym[country[1]]


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
