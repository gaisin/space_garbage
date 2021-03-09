'''Async funcs for frames animation.'''

import asyncio
import curses
import random

import frames.common

from frames.obstacles import Obstacle
from frames.garbage import duck, hubble, lamp, trash_small, trash_medium, trash_large
from frames.physics import update_speed
from frames.rocket import rocket_frame_1, rocket_frame_2


class AnimationHandler:

    def __init__(self, canvas, coroutines):
        self.obstacles = []
        self.canvas = canvas
        self.coroutines = coroutines

    async def animate_spaceship(self, window_rows, window_columns, step_size):
        '''Displays spaceship animation.'''

        frame_rows, frame_columns = frames.common.get_frame_size(rocket_frame_1)
        start_row = (window_rows - frame_rows) // 2
        start_column = (window_columns - frame_columns) // 2
        flame_animation_speed = 2
        border_size = 1

        current_frame = rocket_frame_1
        next_frame = rocket_frame_2

        iteration = 0
        row_speed = column_speed = 0
        while True:
            frames.common.draw_frame(self.canvas, start_row, start_column, current_frame)

            iteration += 1
            await self.sleep()

            frames.common.draw_frame(self.canvas, start_row, start_column, current_frame, negative=True)

            rows_direction, columns_direction, space_pressed = frames.common.read_controls(self.canvas)

            if space_pressed:
                frame_center_column = start_column + frame_columns // 2
                self.coroutines.append(self.fire(start_row, frame_center_column))

            row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction,
                                                columns_direction)
            start_row += row_speed
            start_column += column_speed

            if iteration % flame_animation_speed == 0:
                current_frame, next_frame = next_frame, current_frame

    async def blink(self, row, column, symbol='*'):
        '''Displays animation of a star.'''

        while True:
            self.canvas.addstr(row, column, symbol, curses.A_DIM)
            await self.sleep(random.randint(10, 20))

            self.canvas.addstr(row, column, symbol)
            await self.sleep(random.randint(3, 6))

            self.canvas.addstr(row, column, symbol, curses.A_BOLD)
            await self.sleep(random.randint(5, 10))

            self.canvas.addstr(row, column, symbol)
            await self.sleep(random.randint(3, 6))

    async def fire(self, start_row, start_column, rows_speed=-0.3, columns_speed=0):
        '''Displays animation of gun shot, direction and speed can be specified.'''

        row, column = start_row, start_column

        self.canvas.addstr(round(row), round(column), '*')
        await self.sleep()

        self.canvas.addstr(round(row), round(column), 'O')
        await self.sleep()
        self.canvas.addstr(round(row), round(column), ' ')

        row += rows_speed
        column += columns_speed

        symbol = '-' if columns_speed else '|'

        rows, columns = self.canvas.getmaxyx()  # getmaxyx returns heigh and width of window
        max_row, max_column = rows - 1, columns - 1

        curses.beep()

        while 0 < row < max_row and 0 < column < max_column:
            self.canvas.addstr(round(row), round(column), symbol)
            await self.sleep()
            self.canvas.addstr(round(row), round(column), ' ')
            row += rows_speed
            column += columns_speed

    async def fill_orbit_with_garbage(self, window_columns):
        '''Endlessly starts animating flying peace of garbage.'''

        while True:
            random_frame = random.choice([duck, hubble, lamp, trash_small, trash_medium, trash_large])
            border_size = 1
            random_column = random.randint(border_size, window_columns-2*border_size)
            self.coroutines.append(self.fly_garbage(random_column, random_frame))
            for i in range(20):
                await self.sleep()

    async def fly_garbage(self, column, garbage_frame, speed=1):
        '''Animate garbage, flying from top to bottom.
        Сolumn position will stay same, as specified on start.
        '''

        rows_number, columns_number = self.canvas.getmaxyx()  # getmaxyx returns heigh and width of window

        column = max(column, 0)
        column = min(column, columns_number - 1)

        row = 0

        frame_rows, frame_columns = frames.common.get_frame_size(garbage_frame)

        while row < rows_number:
            obstacle = Obstacle(row, column, frame_rows, frame_columns)
            self.obstacles.append(obstacle)
            frames.common.draw_frame(self.canvas, row, column, garbage_frame)
            await self.sleep()
            frames.common.draw_frame(self.canvas, row, column, garbage_frame, negative=True)
            self.obstacles.remove(obstacle)
            row += speed

    async def sleep(self, tics=1):
        '''Pauses async func for given number of tics.'''

        for _ in range(tics):
            await asyncio.sleep(0)
