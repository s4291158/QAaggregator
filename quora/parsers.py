def int_parser(s):
    if type(s) == int:
        return s
    mapping = {
        '+': 0,
        'k': 3,
        'm': 6,
        'b': 9
    }
    s = s.replace(',', '')
    if s[-1] in mapping:
        power = mapping.get(s[-1])
        s = s[:-1]
    else:
        power = 0
    i = int(float(s) * 10 ** power)
    return i
