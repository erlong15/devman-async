import time
import curses
import asyncio
import random
from curses_tools import draw_frame, read_controls

MAX_STAR_COUNT = 200


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    """Display animation of gun shot. Direction and speed can be specified."""

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()
    max_row, max_column = rows - 2, columns - 2

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def sleep_loop(ticks):
    for i in range(ticks):
        await asyncio.sleep(0)


async def animate_spaceship(canvas, maxy, maxx, frame1, frame2):
    frame_lines = frame1.split('\n')
    frame1_high = len(frame_lines)
    frame1_width = len(frame_lines[0])
    rocket_row = maxy - frame1_high - 1
    rocket_col = (maxx // 2) - (frame1_width // 2)

    while True:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        rocket_row += rows_direction
        rocket_col += columns_direction
        if rocket_row < 2 or rocket_col < 2 \
            or rocket_row > (maxy - frame1_high - 1) \
            or rocket_col > (maxx - frame1_width - 3):
                rocket_row -= rows_direction
                rocket_col -= columns_direction

        await asyncio.sleep(0)
        draw_frame(canvas, rocket_row, rocket_col, frame1)
        await asyncio.sleep(0)
        draw_frame(canvas, rocket_row, rocket_col, frame1, True)
        draw_frame(canvas, rocket_row, rocket_col, frame2)
        await asyncio.sleep(0)
        draw_frame(canvas, rocket_row, rocket_col, frame2, True)





async def blink(canvas, row, column, symbol='*'):
    await sleep_loop(random.randint(0, 20))
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep_loop(20)

        canvas.addstr(row, column, symbol)
        await sleep_loop(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep_loop(5)

        canvas.addstr(row, column, symbol)
        await sleep_loop(3)


# coroutine = curses.wrapper(blink, 5, 20)

def draw(canvas, frame1, frame2):
    TIC_TIMEOUT = 0.1
    canvas.border()
    canvas.refresh()
    (maxy, maxx) = canvas.getmaxyx()
    canvas.nodelay(True)

    coroutines = [fire(canvas, maxy // 2, maxx // 2),
                  animate_spaceship(canvas, maxy, maxx, frame1, frame2)]
    for i in range(MAX_STAR_COUNT):
        symbol = random.choice('+*.:')
        row = random.randint(1, maxy - 2)
        column = random.randint(1, maxx - 2)
        coroutines.append(blink(canvas, row, column, symbol))
    curses.curs_set(False)
    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                del coroutines[0]
            canvas.refresh()
        time.sleep(TIC_TIMEOUT)


def read_frame(fname):
    with open(fname) as hdlr:
        return hdlr.read()


def read_frames():
    frame1 = read_frame('./rocket_frame_1.txt')
    frame2 = read_frame('./rocket_frame_2.txt')
    return frame1, frame2


if __name__ == '__main__':
    curses.update_lines_cols()
    frame1, frame2 = read_frames()
    curses.wrapper(draw, frame1, frame2)

