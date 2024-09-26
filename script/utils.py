def to_hex_map(the_map):
    new_map = {}
    for key, value in the_map.items():
        new_map[hex(key)] = value
    return new_map


