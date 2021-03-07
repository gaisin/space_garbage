'''Async funcs for frames animation.'''

import asyncio
import curses
import random

import frames.common
from frames.garbage import duck, hubble, lamp, trash_small, trash_medium, trash_large
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
        await sleep()

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
        await sleep(random.randint(10, 20))

        canvas.addstr(row, column, symbol)
        await sleep(random.randint(3, 6))

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(random.randint(5, 10))

        canvas.addstr(row, column, symbol)
        await sleep(random.randint(3, 6))


async def fire(canvas, start_row, start_column, rows_speed=-0.3, columns_speed=0):
    '''Displays animation of gun shot, direction and speed can be specified.'''

    row, column = start_row, start_column

    canvas.addstr(round(row), round(column), '*')
    await sleep()

    canvas.addstr(round(row), round(column), 'O')
    await sleep()
    canvas.addstr(round(row), round(column), ' ')

    row += rows_speed
    column += columns_speed

    symbol = '-' if columns_speed else '|'

    rows, columns = canvas.getmaxyx()  # getmaxyx returns heigh and width of window
    max_row, max_column = rows - 1, columns - 1

    curses.beep()

    while 0 < row < max_row and 0 < column < max_column:
        canvas.addstr(round(row), round(column), symbol)
        await sleep()
        canvas.addstr(round(row), round(column), ' ')
        row += rows_speed
        column += columns_speed


async def fill_orbit_with_garbage(canvas, window_columns, coroutines):
    '''Endlessly starts animating flying peace of garbage.'''

    while True:
        random_frame = random.choice([duck, hubble, lamp, trash_small, trash_medium, trash_large])
        border_size = 1
        random_column = random.randint(border_size, window_columns-2*border_size)
        coroutines.append(frames.animation.fly_garbage(canvas, random_column, random_frame))
        for i in range(20):
            await sleep()


async def fly_garbage(canvas, column, garbage_frame, speed=1):
    '''Animate garbage, flying from top to bottom.
    Сolumn position will stay same, as specified on start.
    '''

    rows_number, columns_number = canvas.getmaxyx()  # getmaxyx returns heigh and width of window

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    while row < rows_number:
        frames.common.draw_frame(canvas, row, column, garbage_frame)
        await sleep()
        frames.common.draw_frame(canvas, row, column, garbage_frame, negative=True)
        row += speed


async def sleep(tics=1):
    '''Pauses async func for given number of tics.'''

    for _ in range(tics):
        await asyncio.sleep(0)
