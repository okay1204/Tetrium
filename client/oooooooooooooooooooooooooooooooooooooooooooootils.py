def darken(value, amt = 60):
    return max(value - amt, 0)


def lighten(value, amt  = 60):
    return min(value + amt, 255)

