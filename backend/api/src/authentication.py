import src.config as config


def is_access_key_valid(access_key: str) -> bool:
    return access_key in config.ACCESS_KEYS
