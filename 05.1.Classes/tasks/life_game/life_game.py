import copy


class LifeGame(object):
    """
    Class for Game life
    """

    __field: list[list[int]] = [[]]
    __columns: int = 0
    __rows: int = 0

    def __init__(self, initial_state: list[list[int]]):
        """
        Inits field and borders
        :param initial_state: initial field
        """
        self.__field = copy.deepcopy(initial_state)
        self.__rows = len(initial_state)
        self.__columns = 0 if len(initial_state) == 0 else len(initial_state[0])

    def __get_neighbours(self, x: int, y: int) -> list[tuple[int, int]]:
        dir_x = ([-1] if x > 0 else []) + [0] + ([1] if x < self.__rows - 1 else [])
        dir_y = ([-1] if y > 0 else []) + [0] + ([1] if y < self.__columns - 1 else [])
        neighbours = [(x + x_pos, y + y_pos) for x_pos in dir_x for y_pos in dir_y if x_pos != 0 or y_pos != 0]
        return neighbours

    def __get_life_neighbours(self, neighbours: list[tuple[int, int]], param: int) -> int:
        return len([1 for x, y in neighbours if self.__field[x][y] == param])

    def __process_point(self, x: int, y: int) -> int:
        point = self.__field[x][y]
        neighbours = self.__get_neighbours(x, y)
        fishes_near = self.__get_life_neighbours(neighbours, 2)
        krevs_near = self.__get_life_neighbours(neighbours, 3)
        if point == 0:
            # 0 - empty
            if fishes_near == 3:
                return 2
            if krevs_near == 3:
                return 3
            return 0
        if point == 1:
            # 1 - stone
            return 1
        if point == 2:
            # 2 - fish
            if fishes_near >= 4:
                return 0
            if fishes_near <= 1:
                return 0
            return 2
        assert point == 3
        # 3 - krev
        if krevs_near >= 4:
            return 0
        if krevs_near <= 1:
            return 0
        return 3

    def get_next_generation(self) -> list[list[int]]:
        """
        Calculates and returns next generation of life game
        :return: next generation
        """
        new_generation = copy.deepcopy(self.__field)
        for row_ind in range(self.__rows):
            for column_ind in range(self.__columns):
                new_generation[row_ind][column_ind] = self.__process_point(row_ind, column_ind)
        self.__field = copy.deepcopy(new_generation)
        del new_generation
        return self.__field
