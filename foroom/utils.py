def flush_dictionary(dictionary):
    return {k: v for k, v in dictionary.items() if v is not None}


def normalize_timestamp(time, time_to=None, json_format=False, database_format=False):
    import arrow
    time = arrow.get(time,)
    if time_to is None:
        time_to = '+00:00'

    time = time.to(time_to)

    if database_format:
        return str(time.isoformat())
    if json_format:
        return time.for_json()
    return time.isoformat()


def parse_slug_or_id(slug_or_id):
    try:
        _id = int(slug_or_id)
        return None, _id
    except ValueError:
        _slug = slug_or_id
        return _slug, None


def print_debug(*args, symbol='-', count=15):
    print(symbol * count, *args)


def to_int(target, default=0):
    if target is None:
        return default
    else:
        try:
            return int(target)
        except ValueError:
            return default
