
def copy_and_add_to_dict(src_dict: dict, key, value):
    new_dict = src_dict.copy()
    new_dict[key] = value
    return new_dict
