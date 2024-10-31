class MazeGame:
    def __init__(self, grid, stone_weights):
        self.grid = grid
        self.stone_weights = stone_weights
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.ares_pos = self.find_ares_position()
        self.switches = self.find_switch_positions()
        #self.goal_reached = False
        self.total_cost = 0

    def find_ares_position(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == '@' or self.grid[r][c] == '+':
                    return (r, c)
        return None

    def find_switch_positions(self):
        switches = set()
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c] == '.':
                    switches.add((r, c))
        return switches

    def is_goal_state(self):
        for row in self.grid:
            if '.' in row or '+' in row:
                return False
        return True

    def move(self, direction):
        dr, dc = direction
        ar, ac = self.ares_pos
        nr, nc = ar + dr, ac + dc

        if not (0 <= nr < self.rows and 0 <= nc < self.cols):
            return False
        if self.grid[nr][nc] == '#':
            return False

        if self.grid[nr][nc] == '$' or self.grid[nr][nc] == '*':
            stone_idx = self.get_stone_index((nr, nc))
            stone_weight = self.stone_weights[stone_idx] if stone_idx is not None else 1

            sr, sc = nr + dr, nc + dc
            if not (0 <= sr < self.rows and 0 <= sc < self.cols):
                return False
            if self.grid[sr][sc] != ' ' and self.grid[sr][sc] != '.':
                return False

            self.grid[sr][sc] = '*' if self.grid[sr][sc] == '.' else '$'
            self.grid[nr][nc] = ' ' if self.grid[nr][nc] == '$' else '.'
            self.total_cost += 1 + stone_weight

        self.grid[ar][ac] = ' ' if self.grid[ar][ac] == '@' else '.'
        self.grid[nr][nc] = '@' if self.grid[nr][nc] == ' ' else '+'
        self.ares_pos = (nr, nc)
        self.total_cost += 1

        self.print_grid()
        return True

    def get_stone_index(self, position):
        stone_count = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if (self.grid[r][c] == '$' or self.grid[r][c] == '*') and (r, c) == position:
                    return stone_count
                if self.grid[r][c] == '$' or self.grid[r][c] == '*':
                    stone_count += 1
        return None

    def print_grid(self):
        for row in self.grid:
            print(''.join(row))
        print(f"Total Cost: {self.total_cost}")
        print(f"Ares Position: {self.ares_pos}")
        print(f"Switches: {self.switches}")
        print()

