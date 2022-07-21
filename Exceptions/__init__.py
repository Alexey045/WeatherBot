from logging import info


def get_geocoding_exceptions(request: dict) -> None:
    if len(request) == 0:
        info((request, "Nothing was found."))
    elif "cod" in request:
        match request["cod"]:
            case "400" | "401" | "404" | "429":
                info(f"{request['message']}.")
            case "500" | "502" | "503" | "504":
                info((request, "please contact us for assistance"))
            case _:
                info((request, "Error! Report @PythonEater about this!"))


def catch_error(code: str | int) -> bool:  # ToDo mb delete?
    match code:
        case '404' | 404 | '400' | 400 | '401' | 401:
            return False
        case _:
            return True


def name_exception(request: dict, language: str = "en") -> str:
    try:
        city: str = request["local_names"][language]
    except KeyError:
        city: str = request["name"]
    return city
