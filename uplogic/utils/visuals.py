from bge import render

def draw_line(start, end, color=[1, 1, 1, 1]):
    render.drawLine(
        start,
        end,
        color
    )

def draw_cube(origin, width, color=[1, 1, 1, 1]):
    draw_box(origin, width, width, width, color)


def draw_box(origin, length, width, height, color=[1, 1, 1, 1]):
    c1 = origin.copy()
    c2 = origin.copy()
    c3 = origin.copy()
    c4 = origin.copy()
    c5 = origin.copy()
    c6 = origin.copy()
    c7 = origin.copy()

    c1[0] += width

    c2[0] += width
    c2[1] += length

    c3[1] += length

    c4[2] += height

    c5[0] += width
    c5[2] += height

    c6[0] += width
    c6[1] += length
    c6[2] += height

    c7[1] += length
    c7[2] += height

    draw_line(origin, c1, color)
    draw_line(c1, c2, color)
    draw_line(c2, c3, color)
    draw_line(c3, origin, color)

    draw_line(origin, c4, color)
    draw_line(c1, c5, color)
    draw_line(c2, c6, color)
    draw_line(c3, c7, color)

    draw_line(c4, c5, color)
    draw_line(c5, c6, color)
    draw_line(c6, c7, color)
    draw_line(c7, c4, color)
