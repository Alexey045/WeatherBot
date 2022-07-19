def get_geocoding_exceptions(request: dict) -> str:
    if len(request) == 0:
        return "Nothing was found."
    elif "cod" in request:
        match request["cod"]:
            case "400" | "401" | "404" | "429":
                return f"{request['message']}."
            case _:
                print(request)
                return "Error! Report @PythonEater about this!"


def get_searching_exceptions(request: dict) -> str:
    if len(request) == 0:
        return "Nothing was found."
    if "cod" in request:
        match request["cod"]:
            case "400" | "401" | "404" | "429":
                return f"{request['message']}."
            case "500" | "502" | "503" | "504":
                print(request)
                return "Error! Report @PythonEater about this!"


def name_exception(req: dict, lang: str = "en") -> str:
    try:  # ToDo
        city = req["local_names"][lang]
    except KeyError:
        city = req["name"]
    return city
