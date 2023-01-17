import re


def get_satellite_from_str(string: str):
    satellites_map = {
        "ascat": "ascat",
        "cyg": "cygnss",
        "os2": "oscat",
        "qs": "qscat",
        "rs": "rscat",
    }

    keyword_re = re.search(f"^({'|'.join(satellites_map.keys())})", string.lower())
    if not keyword_re:
        raise Exception(f"Unable to map file name to satellite: {string}")

    return satellites_map[keyword_re.group()]
