piece_colors = {
    'T': 'purple',
    'L': 'orange',
    'BL': 'blue',
    'S': 'green',
    'BS': 'red',
    'I': 'teal',
    'O': 'yellow'
}

def preview_piece(x, y, piece):

    # 15 px is one block here

    color = piece_colors[piece]
    
    if piece == 'T':

        return [
            (color, x-22, y+5, 45, 15),
            (color, x-7, y-10, 15, 15)
        ]

    elif piece == "L":

        return [
            (color, x-15, y-30, 15, 45),
            (color, x-15, y+10, 30, 15)
        ]

    elif piece == "BL":

        return [
            (color, x, y-30, 15, 45),
            (color, x-15, y+10, 30, 15)
        ]

    elif piece == "S":

        return [
            (color, x-7, y-15, 30, 15),
            (color, x-22, y, 30, 15)
        ]

    elif piece == "BS":

        return [
            (color, x-22, y-15, 30, 15),
            (color, x-7, y, 30, 15)
        ]
    
    elif piece == "I":

        return [
            (color, x-8, y-30, 15, 60)
        ]

    elif piece == "O":

        return [
            (color, x-15, y-15, 30, 30)
        ]


def get_piece(x, y, piece):

    color = piece_colors[piece]

    if piece == 'T':


        return [
            (x, y, color),
            (x+1, y, color),
            (x-1, y, color),
            (x, y-1, color)
        ]

    if piece == 'L':

        

        return [
            (x, y+1, color),
            (x-1, y-1, color),
            (x-1, y, color),
            (x-1, y+1, color)
        ]
    
    elif piece == 'BL':

        

        return [
            (x, y+1, color),
            (x+1, y-1, color),
            (x+1, y, color),
            (x+1, y+1, color)
        ]

    elif piece == 'S':

        

        return [
            (x, y, color),
            (x+1, y, color),
            (x, y+1, color),
            (x-1, y+1, color)
        ]

    elif piece == 'BS':

        

        return [
            (x, y, color),
            (x-1, y, color),
            (x, y+1, color),
            (x+1, y+1, color)
        ]

    elif piece == 'I':

        

        return [
            (x, y-1, color),
            (x, y, color),
            (x, y+1, color),
            (x, y+2, color)
        ]

    elif piece == 'O':
        
        

        return [
            (x, y, color),
            (x+1, y, color),
            (x+1, y+1, color),
            (x, y+1, color)
        ]


if __name__ == "__main__":
    import main