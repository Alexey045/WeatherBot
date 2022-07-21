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


def catch_error(code) -> bool:  # ToDo
    match code:
        case '404' | 404 | '400' | 400 | '401' | 401:  # is 400 possible?
            return False
        case _:
            return True


def name_exception(request: dict, language: str = "en") -> str:
    try:  # ToDo
        city = request["local_names"][language]
    except KeyError:
        city = request["name"]
    return city
