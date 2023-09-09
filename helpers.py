import logging


def safe_int_parse(text) -> int:
    try:
        return int(text)
    except ValueError:
        logging.debug(f"Could not parse '{text}' as an integer.")
        return None


def safe_float_parse(text) -> float:
    try:
        return float(text)
    except ValueError:
        logging.debug(f"Could not parse '{text}' as an float.")
        return None


def find_by_name(target_name, obj_list):
    for obj in obj_list:
        if obj.name == target_name:
            return obj
    return None
