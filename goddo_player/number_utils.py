def convert_to_int(value, round_num=True):
    if round_num:
        return int(round(value))
    else:
        return int(value)