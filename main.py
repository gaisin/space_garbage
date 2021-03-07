'''Game entry point.'''

import curses
import random
import time

import frames.animation


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
        coroutines.append(frames.animation.blink(canvas, random_row, random_column,
                                                 symbol=random_symbol))

    central_row = window_rows // 2
    central_column = window_columns // 2
    coroutines.append(frames.animation.fire(canvas, central_row, central_column))

    coroutines.append(frames.animation.animate_spaceship(canvas, window_rows, window_columns,
                                                         SPACESHIP_STEP_SIZE))

    coroutines.append(frames.animation.fill_orbit_with_garbage(canvas, window_columns, coroutines))

    while True:
        for coroutine in coroutines.copy():
            try:
                coroutine.send(None)
                canvas.refresh()
                canvas.border()
            except StopIteration:
                coroutines.remove(coroutine)
            if not coroutines:
                break
        time.sleep(TICKS_DELAY)


if __name__ == '__main__':
  curses.update_lines_cols()
  curses.wrapper(draw)
