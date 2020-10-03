piece_colors = {
    'T': 'purple',
    'L': 'orange',
    'BL': 'blue',
    'S': 'green',
    'BS': 'red',
    'I': 'teal',
    'O': 'yellow'
}


def get_piece(x, y, piece):

    if piece == 'T':

        color = piece_colors[piece]

        return [
            (x, y, color),
            (x+1, y, color),
            (x-1, y, color),
            (x, y-1, color)
        ]

    if piece == 'L':

        color = piece_colors[piece]

        return [
            (x, y+1, color),
            (x-1, y-1, color),
            (x-1, y, color),
            (x-1, y+1, color)
        ]
    
    elif piece == 'BL':

        color = piece_colors[piece]

        return [
            (x, y+1, color),
            (x+1, y-1, color),
            (x+1, y, color),
            (x+1, y+1, color)
        ]

    elif piece == 'S':

        color = piece_colors[piece]

        return [
            (x, y, color),
            (x+1, y, color),
            (x, y+1, color),
            (x-1, y+1, color)
        ]

    elif piece == 'BS':

        color = piece_colors[piece]

        return [
            (x, y, color),
            (x-1, y, color),
            (x, y+1, color),
            (x+1, y+1, color)
        ]

    elif piece == 'I':

        color = piece_colors[piece]

        return [
            (x, y-1, color),
            (x, y, color),
            (x, y+1, color),
            (x, y+2, color)
        ]

    elif piece == 'O':
        
        color = piece_colors[piece]

        return [
            (x, y, color),
            (x+1, y, color),
            (x+1, y+1, color),
            (x, y+1, color)
        ]