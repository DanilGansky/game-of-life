from random import randint
from typing import Tuple

import numpy as np


class Game:
    def __init__(self, width: int = 640, height: int = 480) -> None:
        self.width = width
        self.height = height
        self.generation = 0
        self._area = np.zeros((height, width))

        self.aging = False
        self._max_age = 3
        self._end_breeding_age = 1
        self._alpha = 255 // self._max_age

    @property
    def alpha(self) -> int:
        return self._alpha

    @property
    def max_age(self) -> int:
        return self._max_age

    @max_age.setter
    def max_age(self, max_age: int) -> None:
        self._max_age = max_age
        self._alpha = 255 // self._max_age

    @property
    def area(self) -> np.array:
        return self._area

    def reset(self) -> None:
        self.generation = 0
        self._area = np.zeros((self.height, self.width))

    def _get_cell_value(self) -> int:
        if self.aging:
            return self._max_age
        return 1

    def _destroy_cell(self, cell_value: int) -> int:
        if self.aging:
            if cell_value > 0:
                return cell_value - 1
        return 0

    def _check_age(self, cell_value: int) -> bool:
        if cell_value >= self.end_breeding_age:
            return True
        return False

    def _check_coords(self, x: int, y: int) -> Tuple[int, int, bool]:
        try:
            if self._area[y][x]:
                return x, y, True
            else:
                return x, y, False
        except IndexError:
            if x >= self.width:
                x = 0
            elif x < 0:
                x = self.width - 1

            if y >= self.height:
                y = 0
            elif y < 0:
                y = self.height - 1

            return self._check_coords(x, y)

    def spawn_or_destroy(self, x: int, y: int) -> None:
        x, y, status = self._check_coords(x, y)
        if status:
            self._area[y][x] = self._destroy_cell(self._area[y][x])
        else:
            self._area[y][x] = self._get_cell_value()

    def random_generate(self, count: int = 1000) -> np.array:
        self.generation = 0
        for i in range(count):
            x, y = randint(0, self.width - 1), randint(0, self.height - 1)
            self._area[y][x] = self._get_cell_value()
        return self._area

    def get_neighbours(self, x: int, y: int) -> Tuple[int, int]:
        count, count2 = 0, 0

        for tmp_x in range(x - 1, x + 2):
            for tmp_y in range(y - 1, y + 2):
                if tmp_x != x or tmp_y != y:
                    tmp_x, tmp_y, status = self._check_coords(tmp_x, tmp_y)
                    cell = self._area[tmp_y][tmp_x]

                    if status:
                        count += 1
                    if self.aging and self._check_age(cell):
                        count2 += 1

        return count, count2

    def next_generation(self) -> np.array:
        self.generation += 1
        new_area = np.copy(self._area)

        for x in range(self.width):
            for y in range(self.height):
                if self.aging:
                    neighbours, neighbours2 = self.get_neighbours(x, y)
                else:
                    neighbours = self.get_neighbours(x, y)[0]
                    neighbours2 = neighbours

                cell = self._area[y][x]

                if not cell and neighbours2 == 3:
                    new_area[y][x] = self._get_cell_value()
                elif cell and neighbours not in range(2, 4):
                    new_area[y][x] = 0
                elif self.aging and cell:
                    new_area[y][x] = self._destroy_cell(cell)

        self._area = new_area
        return self._area
