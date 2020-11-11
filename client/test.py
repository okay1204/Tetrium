def complimentary_color(color_0: tuple, color_1: tuple):
    

    def compliment(val, num):
        if not num:
            return abs((val + 120) - 360)

        return abs((val + 240) - 360)

    
    