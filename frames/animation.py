'''Async funcs for frames animation.'''

import asyncio
import curses
import random

import frames.common
from frames.rocket import rocket_frame_1, rocket_frame_2


async def animate_spaceship(canvas, window_rows, window_columns, step_size):
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
            start_row = frames.common.change_frame_position(start_row, rows_direction,
                step_size, window_rows, border_size, frame_rows)
        if columns_direction:
            start_column = frames.common.change_frame_position(start_column, columns_direction,
                step_size, window_columns, border_size, frame_columns)

        if iteration % flame_animation_speed == 0:
            current_frame, next_frame = next_frame, current_frame


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

