def darken(value, amt = 60):
    value -= amt
    return value if value >= 0 else 0


def lighten(value, amt  = 60):
    value += amt
    return value if value <= 255 else 255




x = (29, 10, 100)


print(tuple(map(darken, x, (10 for _ in x))))