def flush_dictionary(dictionary):
    return {k: v for k, v in dictionary.items() if v is not None}


def normalize_timestamp(time, time_to=None, json_format=False, database_format=False):
    import arrow
    time = arrow.get(time,)
    # time = time.to('+03:00')
    # time = time.to('+00:00')
    if time_to is None:
        time_to = '+00:00'

    # print('time_to = [{}]'.format(time_to))
    # print('before: {}'.format(time.isoformat()))
    time = time.to(time_to)
    # print('after: {}'.format(time.isoformat()))

    # if database_format:
        # return time.isoformat(sep=' ')
    if database_format:
        # if time_to:
        #     return '{}{}'.format(time.isoformat(), time_to)
        # else:
        #     return time.isoformat()
        return str(time.isoformat())
        # return '{}{}'.format(time.isoformat(), time_to)
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


class Convert:
    @staticmethod
    def to_int(target):
        if target is None:
            return 0
        else:
            return int(target)