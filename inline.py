from aiogram.types import InlineQuery, \
    InputTextMessageContent, InlineQueryResultArticle
from Dictionaries import unic, previews
from Exceptions import *
from main import *


# id affects both preview and content,
# so it has to be unique for each result
# (Unique identifier for this result, 1-64 Bytes)
# you can set your unique id's
# but for example i'll generate it based on text because I know, that
# only text will be passed in this example
# answer = await get_current(inline_query.query)
# input_content = InputTextMessageContent(answer, parse_mode=ParseMode.HTML)
# result_id: str = hashlib.md5(text.encode()).hexdigest()
# !r for quotes
# answer = fun(city_req, req)  # ToDo разместить все проверки внутри функции, которая возвращает str


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
            answer = fun(city_req[num], req)
            input_content = InputTextMessageContent(answer, parse_mode=ParseMode.HTML)
            if get_searching_exceptions(req) is None:
                result.append(InlineQueryResultArticle(id=f"{num}",
                                                       title=f'{emoji.emojize(":cityscape:")} {name_exception(city_req[num]).upper()} ',
                                                       input_message_content=input_content,
                                                       description=f"{city_req[num]['country']}, "
                                                                   f"{city_req[num]['state'] if 'state' in city_req[num] else city_req[num]['country']}.",
                                                       thumb_url=previews[
                                                           str(req["weather"][0]["icon"])[:-1]], ))
    await inline_query.answer(result, cache_time=1, is_personal=True)


# don't forget to set cache_time=1 for testing (default is 300s or 5m)
# city_req["country"] -> RU, US, etc.
# city_req["state"] -> Moscow, California
# if await get_geocoding_exceptions(city_req) is None:
#   req = json.loads(
#      requests.get(
#         f"https://api.openweathermap.org/data/2.5/weather"
#        f"?lat={city_req[0]['lat']}&lon={city_req[0]['lon']}&lang={lang}"
#       f"&units=metric&appid={KEY}").text)
# if await get_searching_exceptions(req) is None:
#   print(req)
# print(await get_geocoding_exceptions(req))


async def get_current(city: str):
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
                        return fun(city_req, req)
            else:
                return


def fun(city_req, req) -> str:
    city_name = name_exception(city_req)
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
