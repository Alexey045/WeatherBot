from emoji import emojize

response: dict[str, dict[str, str]] = {
    "en": {"temp": "Feels like",
           "wind": "Winds speed", "hum": "Humidity", "metrics": "m/s"},
    "ru": {"temp": "Ощущается как",
           "wind": "Скорость ветра", "hum": "Влажность", "metrics": "м/с"},
    "uk": {"temp": "Відчувається як",
           "wind": "Швидкість вітру", "hum": "Вологість", "metrics": "м/с"}
}

unicode_regional_symbol: dict[str, str] = {"A": "\N{REGIONAL INDICATOR SYMBOL LETTER A}",
                                           "B": "\N{REGIONAL INDICATOR SYMBOL LETTER B}",
                                           "C": "\N{REGIONAL INDICATOR SYMBOL LETTER C}",
                                           "D": "\N{REGIONAL INDICATOR SYMBOL LETTER D}",
                                           "E": "\N{REGIONAL INDICATOR SYMBOL LETTER E}",
                                           "F": "\N{REGIONAL INDICATOR SYMBOL LETTER F}",
                                           "G": "\N{REGIONAL INDICATOR SYMBOL LETTER G}",
                                           "H": "\N{REGIONAL INDICATOR SYMBOL LETTER H}",
                                           "I": "\N{REGIONAL INDICATOR SYMBOL LETTER I}",
                                           "J": "\N{REGIONAL INDICATOR SYMBOL LETTER J}",
                                           "K": "\N{REGIONAL INDICATOR SYMBOL LETTER K}",
                                           "L": "\N{REGIONAL INDICATOR SYMBOL LETTER L}",
                                           "M": "\N{REGIONAL INDICATOR SYMBOL LETTER M}",
                                           "N": "\N{REGIONAL INDICATOR SYMBOL LETTER N}",
                                           "O": "\N{REGIONAL INDICATOR SYMBOL LETTER O}",
                                           "P": "\N{REGIONAL INDICATOR SYMBOL LETTER P}",
                                           "Q": "\N{REGIONAL INDICATOR SYMBOL LETTER Q}",
                                           "R": "\N{REGIONAL INDICATOR SYMBOL LETTER R}",
                                           "S": "\N{REGIONAL INDICATOR SYMBOL LETTER S}",
                                           "T": "\N{REGIONAL INDICATOR SYMBOL LETTER T}",
                                           "U": "\N{REGIONAL INDICATOR SYMBOL LETTER U}",
                                           "V": "\N{REGIONAL INDICATOR SYMBOL LETTER V}",
                                           "W": "\N{REGIONAL INDICATOR SYMBOL LETTER W}",
                                           "X": "\N{REGIONAL INDICATOR SYMBOL LETTER X}",
                                           "Y": "\N{REGIONAL INDICATOR SYMBOL LETTER Y}",
                                           "Z": "\N{REGIONAL INDICATOR SYMBOL LETTER Z}"}

previews: dict[str, str] = {
    "01": f"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com"
          f"/thumbs/120/apple/325/sun_2600-fe0f.png",
    "02": f"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com"
          f"/thumbs/120/apple/325/sun-behind-small-cloud_1f324-fe0f.png",
    "03": f"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com"
          f"/thumbs/120/apple/325/sun-behind-cloud_26c5.png",
    "04": f"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com"
          f"/thumbs/120/apple/325/cloud_2601-fe0f.png",
    "09": f"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com"
          f"/thumbs/120/apple/325/cloud-with-rain_1f327-fe0f.png",
    "10": f"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com"
          f"/thumbs/120/apple/325/cloud-with-rain_1f327-fe0f.png",
    "11": f"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com"
          f"/thumbs/120/apple/325/cloud-with-lightning_1f329-fe0f.png",
    "13": f"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com"
          f"/thumbs/120/apple/325/cloud-with-snow_1f328-fe0f.png",
    "50": f"https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com"
          f"/thumbs/120/apple/325/fog_1f32b-fe0f.png"}

weather_descriptions: dict[str, str] = {"01": str(emojize(f':sun:')),
                                        "02": str(emojize(f':sun_behind_small_cloud:')),
                                        "03": str(emojize(f':sun_behind_cloud:')),
                                        "04": str(emojize(f':cloud:')),
                                        "09": str(emojize(f':cloud_with_rain:')),
                                        "10": str(emojize(f':cloud_with_rain:')),
                                        "11": str(emojize(f':cloud_with_lightning:')),
                                        "13": str(emojize(f':cloud_with_snow:')),
                                        "50": str(emojize(f':fog:'))}