import time
import curses
import asyncio
import random
from curses_tools import draw_frame, read_controls, get_frame_size
from space_garbage import fly_garbage

MAX_STAR_COUNT = 200
MAX_STAR_START_DELAY = 20

FRAME_DIR = './animation'
TIC_TIMEOUT = 0.1

coroutines = []

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
    frame1_hight, frame1_width = get_frame_size(frame1)
    rocket_row = maxy - frame1_hight - 1
    rocket_col = (maxx // 2) - (frame1_width // 2)
    border_row = (maxy - frame1_hight)
    border_col = (maxx - frame1_width)

    while True:
        rows_direction, columns_direction, space_pressed = read_controls(canvas)
        rocket_row += rows_direction
        rocket_col += columns_direction

        if not (1 <= rocket_row < border_row):
            rocket_row -= rows_direction
        if not (1 <= rocket_col < border_col):
            rocket_col -= columns_direction
        draw_frame(canvas, rocket_row, rocket_col, frame1)
        await asyncio.sleep(0)
        draw_frame(canvas, rocket_row, rocket_col, frame1, True)
        draw_frame(canvas, rocket_row, rocket_col, frame2)
        await asyncio.sleep(0)
        draw_frame(canvas, rocket_row, rocket_col, frame2, True)


async def blink(canvas, row, column, offset_ticks, symbol='*'):
    await sleep_loop(offset_ticks)
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep_loop(20)

        canvas.addstr(row, column, symbol)
        await sleep_loop(3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep_loop(5)

        canvas.addstr(row, column, symbol)
        await sleep_loop(3)


async def fill_orbit_with_garbage(canvas, garbage, maxx):
    global coroutines
    while True:
        frame = garbage[random.randint(0, len(garbage)-1)]
        col = random.randint(1, maxx - frame[2])
        if len(coroutines) < (MAX_STAR_COUNT + 3 + 10):
            coroutines.append(fly_garbage(canvas, col, frame[0]))
        await sleep_loop(random.randint(0, 30))


def draw(canvas, frame1, frame2, garbage):
    global coroutines
    canvas.border()
    canvas.refresh()
    maxy, maxx = canvas.getmaxyx()
    canvas.nodelay(True)

    coroutines = [fire(canvas, maxy // 2, maxx // 2),
                  animate_spaceship(canvas, maxy, maxx, frame1, frame2),
                  fill_orbit_with_garbage(canvas, garbage, maxx)]

    for i in range(MAX_STAR_COUNT):
        symbol = random.choice('+*.:')
        row = random.randint(1, maxy - 2)
        column = random.randint(1, maxx - 2)
        offset_ticks = random.randint(0, MAX_STAR_START_DELAY)
        coroutines.append(blink(canvas, row, column, offset_ticks, symbol))
    curses.curs_set(False)
    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
            canvas.refresh()
        time.sleep(TIC_TIMEOUT)


def read_frame(fname):
    with open(f'{FRAME_DIR}/{fname}') as hdlr:
        return hdlr.read()


def read_frames():
    frame1 = read_frame('rocket_frame_1.txt')
    frame2 = read_frame('rocket_frame_2.txt')
    return frame1, frame2

def read_garbage_frames():
    garbage_files = ['duck.txt', 'hubble.txt', 'lamp.txt', 'trash_large.txt', 'trash_small.txt', 'trash_xl.txt']
    garbage_frames = []
    for file in garbage_files:
        frame = read_frame(file)
        frame_hight, frame_width = get_frame_size(frame)
        garbage_frames.append([frame, frame_hight, frame_width])
    return garbage_frames


if __name__ == '__main__':
    curses.update_lines_cols()
    frame1, frame2 = read_frames()
    garbage = read_garbage_frames()
    curses.wrapper(draw, frame1, frame2, garbage)

