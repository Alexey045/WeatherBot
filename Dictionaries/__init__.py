from emoji import emojize

response: dict = {
    "en": {"temp": "Feels like",
           "wind": "Winds speed", "hum": "Humidity", "metrics": "m/s"},
    "ru": {"temp": "Ощущается как",
           "wind": "Скорость ветра", "hum": "Влажность", "metrics": "м/с"},
    "uk": {"temp": "Відчувається як",
           "wind": "Швидкість вітру", "hum": "Вологість", "metrics": "м/с"}
}

previews: dict = {
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

weather_descriptions: dict = {"01": emojize(f':sun:'),
                              "02": emojize(f':sun_behind_small_cloud:'),
                              "03": emojize(f':sun_behind_cloud:'),
                              "04": emojize(f':cloud:'),
                              "09": emojize(f':cloud_with_rain:'),
                              "10": emojize(f':cloud_with_rain:'),
                              "11": emojize(f':cloud_with_lightning:'),
                              "13": emojize(f':cloud_with_snow:'),
                              "50": emojize(f':fog:')}
