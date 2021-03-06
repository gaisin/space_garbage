import asyncio
import curses
import random
import time

import frames.common
from frames.rocket import rocket_frame_1, rocket_frame_2


BACKGROUND_STARS_NUM = 200

TICKS_DELAY = 0.1

SPACESHIP_STEP_SIZE = 1


def set_canvas(canvas, show_cursor=False, show_border=True, non_blocking_input=True):
    '''Sets canvas settings.'''

    curses.curs_set(show_cursor)
    canvas.nodelay(non_blocking_input)
    if show_border:
        canvas.border()


def draw(canvas):
    '''Draws the game on the canvas.'''

    set_canvas(canvas)
    coroutines = []
    window_rows, window_columns = canvas.getmaxyx()  # getmaxyx returns heigh and width of window
    border_size = 1
    for i in range(BACKGROUND_STARS_NUM):
        random_row = random.randint(border_size, window_rows-2*border_size)
        random_column = random.randint(border_size, window_columns-2*border_size)
        random_symbol = random.choice('+*.:')
        coroutines.append(blink(canvas, random_row, random_column, symbol=random_symbol))

    central_row = window_rows // 2
    central_column = window_columns // 2
    coroutines.append(fire(canvas, central_row, central_column))

    coroutines.append(animate_spaceship(canvas, window_rows, window_columns))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                canvas.refresh()
            except StopIteration:
                coroutines.remove(coroutine)
            if not coroutines:
                break
        time.sleep(TICKS_DELAY)
 

async def blink(canvas, row, column, symbol='*'):
    '''Displays animation of a star.'''

    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(random.randint(10, 20)):
          await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(random.randint(3, 6)):
          await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(random.randint(5, 10)):
          await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(random.randint(3, 6)):
          await asyncio.sleep(0)


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    '''Displays animation of gun shot, direction and speed can be specified.'''

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await asyncio.sleep(0)

    canvas.addstr(round(row), round(column), 'O')
    await asyncio.sleep(0)
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()  # getmaxyx returns heigh and width of window
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await asyncio.sleep(0)
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def animate_spaceship(canvas, window_rows, window_columns):
    '''Displays spaceship animation.'''

    frame_rows, frame_columns = frames.common.get_frame_size(rocket_frame_1)
    start_row = (window_rows - frame_rows) // 2
    start_column = (window_columns - frame_columns) // 2
    flame_animation_speed = 2
    border_size = 1

    current_frame = rocket_frame_1
    next_frame = rocket_frame_2

    iteration = 0
    while True:
        frames.common.draw_frame(canvas, start_row, start_column, current_frame)

        iteration += 1
        await asyncio.sleep(0)

        frames.common.draw_frame(canvas, start_row, start_column, current_frame, negative=True)

        rows_direction, columns_direction, _ = frames.common.read_controls(canvas)
        if rows_direction:
            start_row = change_position(start_row, rows_direction, SPACESHIP_STEP_SIZE, window_rows,
                                        border_size, frame_rows)
        if columns_direction:
            start_column = change_position(start_column, columns_direction, SPACESHIP_STEP_SIZE,
                                           window_columns, border_size, frame_columns)

        if iteration % flame_animation_speed == 0:
            current_frame, next_frame = next_frame, current_frame


def change_position(current_position, direction, step_size, window_size, border_size, frame_size):
    '''Changes position according to args.'''

    if (current_position + direction * step_size - border_size >= 0 and 
            border_size + current_position + frame_size + direction * step_size <= window_size):
        new_position = current_position + direction * step_size
    elif direction < 0:
        new_position = current_position - (current_position - border_size)
    elif direction > 0:
        new_position = (current_position + window_size - border_size - 
                        (current_position + frame_size))

    return new_position


if __name__ == '__main__':
  curses.update_lines_cols()
  curses.wrapper(draw)
