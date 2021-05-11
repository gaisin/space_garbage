'''Async funcs for frames animation.'''

import asyncio
import curses
import random

import frames.common

from frames.obstacles import Obstacle
from frames.garbage import duck, hubble, lamp, trash_small, trash_medium, trash_large
from frames.physics import update_speed
from frames.rocket import rocket_frame_1, rocket_frame_2
from frames.explosion import explosion_frames
from frames.text import game_over


BULLET_SPEED = -1  # less is faster
GARBAGE_FALLING_SPEED = 5
GARBAGE_GENERATION_SPEED = 30

class AnimationHandler:

    def __init__(self, canvas, coroutines):
        self.obstacles = []
        self.obstacles_in_last_collisions = []
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
                self.coroutines.append(self.fire(start_row, frame_center_column, rows_speed=BULLET_SPEED))

            row_speed, column_speed = update_speed(row_speed, column_speed, rows_direction,
                                                columns_direction)
            start_row = (start_row + row_speed) % window_rows
            start_column = (start_column + column_speed) % window_columns

            if iteration % flame_animation_speed == 0:
                current_frame, next_frame = next_frame, current_frame

            frame_rows, frame_columns = frames.common.get_frame_size(current_frame)
            for obstacle in self.obstacles:
                if obstacle.has_collision(start_row, start_column, frame_rows, frame_columns):
                    self.coroutines.append(self.show_gameover())
                    return

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

            for obstacle in self.obstacles:
                if obstacle.has_collision(row, column):
                    self.obstacles_in_last_collisions.append(obstacle)
                    return

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
            await self.sleep(tics=GARBAGE_GENERATION_SPEED)

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
            obstacle_start_row, obstacle_start_column = obstacle.get_bounding_box_corner_pos()

            frames.common.draw_frame(self.canvas, row, column, garbage_frame)
            frames.common.draw_frame(self.canvas, obstacle_start_row, obstacle_start_column, obstacle.get_bounding_box_frame())

            await self.sleep(tics=GARBAGE_FALLING_SPEED)

            frames.common.draw_frame(self.canvas, row, column, garbage_frame, negative=True)
            frames.common.draw_frame(self.canvas, obstacle_start_row, obstacle_start_column, obstacle.get_bounding_box_frame(), negative=True)

            self.obstacles.remove(obstacle)

            if obstacle in self.obstacles_in_last_collisions:
                shift_for_better_alignment = 2
                await self.explode(row+frame_rows/2+shift_for_better_alignment,
                                   column+frame_columns/2-shift_for_better_alignment)
                break

            row += speed

    async def explode(self, center_row, center_column):
        '''Draws explode animation.'''

        rows, columns = frames.common.get_frame_size(explosion_frames[0])
        corner_row = center_row - rows / 2
        corner_column = center_column - columns / 2

        curses.beep()

        for frame in explosion_frames:
            frames.common.draw_frame(self.canvas, corner_row, corner_column, frame)
            await self.sleep()
            frames.common.draw_frame(self.canvas, corner_row, corner_column, frame, negative=True)
            await self.sleep()

    async def sleep(self, tics=1):
        '''Pauses async func for given number of tics.'''

        for _ in range(tics):
            await asyncio.sleep(0)

    async def show_gameover(self):
        '''Shows "GameOver" in the middle of the screen.'''

        while True:
            rows_number, columns_number = self.canvas.getmaxyx()
            frame_rows, frame_columns = frames.common.get_frame_size(game_over)

            start_row = (rows_number - frame_rows) / 2
            start_column = (columns_number - frame_columns) / 2

            frames.common.draw_frame(self.canvas, start_row, start_column, game_over)

            await self.sleep()
