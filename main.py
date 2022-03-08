import datetime
import json
import logging
from aiogram import Bot, Dispatcher, executor, types
from os import getenv
from sys import exit
import requests
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ContentType, ParseMode
import emoji
from aiogram.utils.markdown import bold

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


@dp.message_handler(commands=['daily'], content_types=[ContentType.TEXT])
async def weather_request(message: types.Message):
    print(message)
    city = str(message["text"]).lstrip("/daily ")
    if len(city) != 0:
        if city.isnumeric():
            await message.reply("Please, write name of the city.")
        else:
            if len(city) > 150:
                await message.reply("Error: long name of the city.")  # ToDo
                return
            else:
                city_req = json.loads(
                    requests.get(f"http://api.openweathermap.org/geo/1.0/direct"
                                 f"?q={city}"
                                 f"&limit=1&appid={KEY}").text)  # ToDo
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
                    await message.reply(
                        f'{emoji.emojize(f":cityscape:")} '
                        f'City: {bold(city_req[0]["name"])}\n\n' + "\n".join(
                            str(emoji.emojize(f":keycap_{i + 1}:") + " " +
                                bold(datetime.datetime.fromtimestamp(
                                    req["daily"][i]["dt"]).strftime(
                                    '%B %d, %A'))) + f":\n    {emoji.emojize(':sun:')} "
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
                            for i in range(len(req["daily"]) - 1)), parse_mode=ParseMode.MARKDOWN)
                else:
                    await message.reply("Please, write name of the city.")
    else:
        await message.reply("Please, write name of the city.")


@dp.message_handler(commands=['settings'], content_types=[ContentType.TEXT])
async def settings(message: types.Message):
    await message.answer('Your settings:\n'
                         '\t daily:\n'
                         '\t current:')


@dp.message_handler(commands=['current'], content_types=[ContentType.TEXT])
async def weather_request(message: types.Message):
    print(datetime.datetime.now())
    print(message)
    city = str(message["text"]).lstrip("/current ")
    if len(city) != 0:
        if city.isnumeric():
            await message.reply("Please, write name of the city.")
        else:
            if len(city) > 150:  # WTF IS THAT???
                await message.reply("Error: long name of the city.")  # ToDo
                return
            else:
                city_req = json.loads(
                    requests.get(f"http://api.openweathermap.org/geo/1.0/direct"
                                 f"?q={city}"
                                 f"&limit=1&appid={KEY}").text)
                if 'cod' in city_req:
                    match city_req['cod']:
                        case '404' | 404:
                            await message.reply('Please, write name of the city.')
                            return
                if len(city_req) != 0:
                    req = json.loads(
                        requests.get(
                            f"http://api.openweathermap.org/data/2.5/weather"
                            f"?q={city_req[0]['name']}&units=metric&appid={KEY}").text)
                    match req["cod"]:
                        case '404' | 404 | '400' | 400:
                            await message.reply(req["message"].capitalize() + '.')
                        case '401' | 401:
                            await message.reply("Please, write name of the city.")
                            # await message.reply("Invalid API key.") # ToDo
                        case _:
                            await message.reply(
                                f'{emoji.emojize(f":cityscape:")} '
                                f'City: {req["name"]}d\n'
                                f'{emoji.emojize(f":thermometer:")} '
                                f'Temperature: {round(float(req["main"]["temp"]))}\u00A0°C\n'
                                f'{emoji.emojize(f":dashing_away:")} '
                                f'Wind speed: {req["wind"]["speed"]}\u00A0m/s\n'
                                f'{emoji.emojize(f":droplet:")} '
                                f'Humidity: {req["main"]["humidity"]}%')
                else:
                    await message.reply("Please, write name of the city.")
    else:
        await message.reply("Please, write name of the city.")


@dp.message_handler(commands="help")
async def cmd_help(message: types.Message):
    await message.answer("/current [city name] - current weather\n"
                         "/daily [city name] - daily weather forecast")


@dp.message_handler(commands="about")
async def cmd_about(message: types.Message):
    await message.answer("Weather Bot is @PythonEater personal bot, which will send daily and "
                         "week forecast. Work in progress.")


@dp.message_handler(content_types=ContentType.LOCATION)
async def cmd_geotag_message(message: types.Message):
    latitude, longitude = message["location"]["latitude"], message["location"]["longitude"]
    req = json.loads(requests.get(
        f"http://api.openweathermap.org/data/2.5/weather"
        f"?lat={latitude}&lon={longitude}&units=metric&appid={KEY}").text)
    # &lang={message.from_user.language_code}
    match req['cod']:
        case '404' | 404 | '400' | 400 | '401' | 401:
            await message.reply("Please, write name of the city.")
        case _:
            await message.reply(
                f'{emoji.emojize(f":thermometer:")}'
                f'Temperature: {round(float(req["main"]["temp"]))}\u00A0°C,\n'
                f'{emoji.emojize(f":dashing_away:")}'
                f'Wind speed: {req["wind"]["speed"]}\u00A0m/s,\n'
                f'{emoji.emojize(f":droplet:")}'
                f'Humidity: {req["main"]["humidity"]}%.'.lstrip())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
    """
    loop = asyncio.get_event_loop()
    while True:
        loop.run_until_complete(schedule.run_pending())
    """