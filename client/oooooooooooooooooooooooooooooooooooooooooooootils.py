def darken(value):
    value -= 60
    return value if value >= 0 else 0


def lighten(value):
    value += 60
    return value if value <= 255 else 255

