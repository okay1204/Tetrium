def darken(value, amt = 60):
    value -= amt
    return value if value >= 0 else 0


def lighten(value, amt  = 60):
    value += amt
    return value if value <= 255 else 255