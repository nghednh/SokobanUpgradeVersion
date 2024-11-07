import time
from collections import deque
class MazeGame:
    def __init__(self, grid, stone_weights):
        self.grid = grid
        self.stone_weights = stone_weights
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.stone_pos = self.find_stone_pos()
        self.ares_pos = self.find_ares_position()
        self.switches = self.find_switch_positions()
        #self.goal_reached = False
        self.total_cost = 0
        

    def find_stone_pos(self):
        stonePos = []
        idx = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c]=='$' or self.grid[r][c]=='*': 
                    stonePos.append((r,c,idx))
                    idx = idx + 1
        return stonePos

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
    
    def moveStone(self,oldpos,newpos):
        #print("I hate python fuckery")
        #print(oldpos)
        #print(newpos)
        idx = self.get_stone_index(oldpos)
        newstone = (newpos[0], newpos[1] ,idx)
        self.stone_pos[idx] = newstone

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
            self.moveStone((nr,nc),(sr,sc))
            self.total_cost += 1 + stone_weight

        self.grid[ar][ac] = ' ' if self.grid[ar][ac] == '@' else '.'
        self.grid[nr][nc] = '@' if self.grid[nr][nc] == ' ' else '+'
        self.ares_pos = (nr, nc)
        self.total_cost += 1

        self.print_grid()
        return True

    def get_stone_index(self, position):
        stone_count = 0
        for stone in self.stone_pos:
            if (stone[0],stone[1]) == position:
                return stone[2]
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
        print(self.stone_pos)
        print()

    def get_state(self):
        # The current state includes Ares's position, stone positions, and grid
        return (self.ares_pos, tuple(self.stone_pos))
    
    def getSuccessors(self):
        successors = []
        directions = [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]
        
        for dr, dc, move_dir in directions:
            if self.can_move(dr, dc):  # Check if Ares can move in this direction
                # Clone grid and move Ares to generate a successor state
                new_grid = [row[:] for row in self.grid]  # Deep copy of the grid
                new_game = MazeGame(new_grid, self.stone_weights)
                new_game.ares_pos = self.ares_pos  # Start from current Ares's position
                new_game.stone_pos = list(self.stone_pos)  # Start from current stone positions
                new_game.total_cost = self.total_cost  # Start from current cost
                
                # Perform the move
                if new_game.move((dr, dc)):  # Move in direction (dr, dc)
                    # Capture the state after the move
                    successor_state = new_game.get_state()
                    cost = new_game.total_cost - self.total_cost
                    successors.append((new_game, move_dir, cost))

        return successors

    def can_move(self, dr, dc):
        ar, ac = self.ares_pos
        nr, nc = ar + dr, ac + dc

        if not (0 <= nr < self.rows and 0 <= nc < self.cols):  # Boundary check
            return False
        if self.grid[nr][nc] == '#':  # Wall check
            return False

        # Check if the move involves pushing a stone
        if self.grid[nr][nc] == '$' or self.grid[nr][nc] == '*':
            sr, sc = nr + dr, nc + dc
            if not (0 <= sr < self.rows and 0 <= sc < self.cols):  # Boundary check for stone push
                return False
            if self.grid[sr][sc] != ' ' and self.grid[sr][sc] != '.':  # Stone can't move to wall or other stone
                return False

        return True
    
    def bfs(self):
        queue = deque([(self, [], 0)])  # start from initial state with an empty path
        visited = set()  # To avoid revisiting the same state
        initial_state = self.get_state()
        visited.add(initial_state)  # Add initial state to visited
        print(f"Initial state: {initial_state}")

        while queue:
            (current_game, path, total_cost) = queue.popleft()
            current_state = current_game.get_state()
            print(f"Exploring state: {current_state}, Path: {path}, Total cost: {total_cost}")

            # Check if current state is a goal state
            if current_game.is_goal_state():
                print("Goal reached with path:", path)
                return path  # Return the path that leads to the goal

        # Generate successors from the current state
            for successor_game, move_dir, move_cost in current_game.getSuccessors():
                successor_state = successor_game.get_state()
                if successor_state not in visited:
                # Create a new MazeGame instance for the successor state
                    # successor_game = MazeGame([row[:] for row in current_game.grid], current_game.stone_weights)
                    # successor_game.ares_pos = successor_state[0]
                    # successor_game.stone_pos = list(successor_state[1])
                    # successor_game.total_cost = current_game.total_cost + move_cost

                # Mark as visited and enqueue for further exploration
                    visited.add(successor_state)
                    new_path = path + [move_dir]
                    queue.append((successor_game, new_path, total_cost + move_cost))
                    print(f"Enqueued successor state: {successor_game.get_state()}, Path so far: {new_path}, Cost: {total_cost + move_cost}")

        print("No solution found.")
        return None
    def dfs(self):
        stack = [(self, [], 0)]  # start from initial state with an empty path
        visited = set()  # To avoid revisiting the same state
        initial_state = self.get_state()
        visited.add(initial_state)  # Add initial state to visited
        print(f"Initial state: {initial_state}")

        while stack:
            (current_game, path, total_cost) = stack.pop()
            current_state = current_game.get_state()
            print(f"Exploring state: {current_state}, Path: {path}, Total cost: {total_cost}")

            # Check if current state is a goal state
            if current_game.is_goal_state():
                print("Goal reached with path:", path)
                return path  # Return the path that leads to the goal

        # Generate successors from the current state
            for successor_game, move_dir, move_cost in current_game.getSuccessors():
                successor_state = successor_game.get_state()
                if successor_state not in visited:
                # Create a new MazeGame instance for the successor state
                    # successor_game = MazeGame([row[:] for row in current_game.grid], current_game.stone_weights)
                    # successor_game.ares_pos = successor_state[0]
                    # successor_game.stone_pos = list(successor_state[1])
                    # successor_game.total_cost = current_game.total_cost + move_cost

                # Mark as visited and enqueue for further exploration
                    visited.add(successor_state)
                    new_path = path + [move_dir]
                    stack.append((successor_game, new_path, total_cost + move_cost))
                    print(f"Enqueued successor state: {successor_game.get_state()}, Path so far: {new_path}, Cost: {total_cost + move_cost}")

        print("No solution found.")
        return None
    

    

