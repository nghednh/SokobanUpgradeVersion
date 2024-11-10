import time
from collections import deque
import heapq
import tracemalloc
import itertools

class PriorityQueueNode:
    def __init__(self, estimated_total_cost, cost, game, path):
        self.estimated_total_cost = estimated_total_cost
        self.cost = cost
        self.game = game
        self.path = path

    def __lt__(self, other):
        # Only compare by estimated_total_cost
        return self.estimated_total_cost < other.estimated_total_cost

class MazeGame:
    def __init__(self, grid, stone_weights):
        self.grid = grid
        self.stone_weights = stone_weights
        self.rows = len(grid)
        self.cols = len(grid[0]) if self.rows > 0 else 0
        self.stone_pos = self.find_stone_pos()
        self.button_pos = self.find_button_pos()
        self.ares_pos = self.find_ares_position()
        self.switches = self.find_switch_positions()
        #self.goal_reached = False
        self.total_cost = 0
        
    def dist(self,x, y):
        return abs(x[0]-y[0])+abs(x[1]-y[1])
    
    def heuristic(self,state):
        # print("Why do gods just eat one of our button?")
        # print(state[1])
        # print(self.button_pos)
        # print(self.stone_weights)
        mweight = 0
        for idx in range(len(self.stone_pos)):
            mweight = max(mweight,self.stone_weights[idx])
        hValue = 0
        for id in range(len(state[1])):
            mValue = self.cols*self.rows*mweight
            for idx in range(len(self.stone_pos)):
                mValue = min(mValue,self.dist((state[1][id][0],state[1][id][1]),self.button_pos[idx])*self.stone_weights[idx])
            hValue = hValue + mValue
        # print(hValue)
        return hValue

    def find_stone_pos(self):
        stonePos = []
        idx = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c]=='$' or self.grid[r][c]=='*': 
                    stonePos.append((r,c,idx))
                    idx = idx + 1
        return stonePos 

    def find_button_pos(self):
        #print(self.grid)
        buttonPos = []
        for r in range(self.rows):
            #print(self.grid[r])
            for c in range(self.cols):
                #print(self.grid[r][c])
                if self.grid[r][c]=='.' or self.grid[r][c]=='*' or self.grid[r][c]=='+':
                    buttonPos.append((r,c))
        return buttonPos

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
            self.total_cost +=stone_weight

        self.grid[ar][ac] = ' ' if self.grid[ar][ac] == '@' else '.'
        self.grid[nr][nc] = '@' if self.grid[nr][nc] == ' ' else '+'
        self.ares_pos = (nr, nc)
        self.total_cost += 1

        # self.print_grid()
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

    def reset(self):
        print(f"reset is valiable")


    def get_state(self):
        # The current state includes Ares's position, stone positions, and grid
        return (self.ares_pos, tuple(self.stone_pos))
    
    def getSuccessors(self):
        successors = []
        directions = [(-1, 0, 'U'), (1, 0, 'D'), (0, -1, 'L'), (0, 1, 'R')]
        stone_positions = {(stone[0], stone[1]) for stone in self.stone_pos}

        for dr, dc, move_dir in directions:
            if self.can_move(dr, dc):  # Check if Ares can move in this direction
                # Clone grid and move Ares to generate a successor state
                new_grid = [row[:] for row in self.grid]  # Deep copy of the grid
                new_game = MazeGame(new_grid, self.stone_weights)
                new_game.ares_pos = self.ares_pos  # Start from current Ares's position
                new_game.stone_pos = list(self.stone_pos)  # Start from current stone positions
                new_game.total_cost = self.total_cost  # Start from current cost
                target_r, target_c = self.ares_pos[0] + dr, self.ares_pos[1] + dc
                if (target_r, target_c) in stone_positions:
                    move_dir = move_dir.upper()  # Use lowercase for moves toward stones
                else:
                    move_dir = move_dir.lower()  # Use uppercase otherwise
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

    import heapq
    import tracemalloc
    import time

    def a_star(self):
        priority_queue = []  # Priority queue to store nodes by estimated total cost
        initial_state = self.get_state()
        initial_path = []
        initial_cost = 0
        initial_estimated_cost = initial_cost + self.heuristic(initial_state)

        # Add the initial state to the priority queue with estimated total cost
        node = PriorityQueueNode(initial_estimated_cost, initial_cost, self, initial_path)
        heapq.heappush(priority_queue, node)

        visited = set()  # To avoid revisiting the same state
        visited.add(initial_state)  # Mark initial state as visited

        print(f"Initial state: {initial_state}")

        # Track memory and time
        nodes_generated = 0
        tracemalloc.start()
        start_time = time.time()

        while priority_queue:
            # Pop the state with the lowest estimated total cost
            node = heapq.heappop(priority_queue)
            estimated_cost = node.estimated_total_cost
            current_cost = node.cost
            current_game = node.game
            path = node.path
            current_state = current_game.get_state()

            # print(
            #     f"Exploring state: {current_state}, Path: {path}, Cost: {current_cost}, Estimated Total Cost: {estimated_cost}")

            # Check if the current state is a goal state
            if current_game.is_goal_state():
                end_time = time.time()
                memory_used = tracemalloc.get_traced_memory()[1] / (1024 * 1024)  # Peak memory in MB
                tracemalloc.stop()

                # Steps are the length of the path taken to reach the goal
                steps = len(path)
                total_time = (end_time - start_time) * 1000  # Time in milliseconds

                return {
                    "cost": current_cost,
                    "steps": steps,
                    "nodes_generated": nodes_generated,
                    "time_ms": total_time,
                    "memory_mb": memory_used,
                    "solution_path": path
                }

            # Generate successors from the current state
            for successor_game, move_dir, move_cost in current_game.getSuccessors():
                successor_state = successor_game.get_state()

                if successor_state not in visited:
                    # Mark as visited to prevent re-exploration
                    visited.add(successor_state)

                    # Calculate the new path, cost, and estimated total cost
                    new_path = path + [move_dir]
                    new_cost = current_cost + move_cost
                    estimated_total_cost = new_cost + successor_game.heuristic(successor_state)

                    # Add the successor to the priority queue
                    node = PriorityQueueNode(estimated_total_cost, new_cost, successor_game, new_path)
                    heapq.heappush(priority_queue, node)

                    nodes_generated += 1

        # print("No solution found.")

        tracemalloc.stop()
        return {
            "cost": None,
            "steps": None,
            "nodes_generated": nodes_generated,
            "time_ms": (time.time() - start_time) * 1000,
            "memory_mb": tracemalloc.get_traced_memory()[1] / (1024 * 1024),
            "solution_path": None
        }



    def bfs(self):
        queue = deque([(self, [], 0)])  # start from initial state with an empty path
        visited = set()  # To avoid revisiting the same state
        initial_state = self.get_state()
        visited.add(initial_state)  # Add initial state to visited
        print(f"Initial state: {initial_state}")

        # Track memory and time
        nodes_generated = 0
        tracemalloc.start()
        start_time = time.time()

        while queue:
            (current_game, path, total_cost) = queue.popleft()
            current_state = current_game.get_state()

            # Check if current state is a goal state
            if current_game.is_goal_state():
                end_time = time.time()
                memory_used = tracemalloc.get_traced_memory()[1] / (1024 * 1024)  # Peak memory in MB
                tracemalloc.stop()

                # Steps are the length of the path taken to reach the goal
                steps = len(path)
                total_time = (end_time - start_time) * 1000  # Time in milliseconds

                return {
                    "cost": total_cost,
                    "steps": steps,
                    "nodes_generated": nodes_generated,
                    "time_ms": total_time,
                    "memory_mb": memory_used,
                    "solution_path": path
                }

            # Generate successors from the current state
            for successor_game, move_dir, move_cost in current_game.getSuccessors():
                successor_state = successor_game.get_state()
                nodes_generated += 1
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
                        #print(f"Enqueued successor state: {successor_game.get_state()}, Path so far: {new_path}, Cost: {total_cost + move_cost}")


        print("No solution found.")
        tracemalloc.stop()
        return {
            "cost": None,
            "steps": None,
            "nodes_generated": nodes_generated,
            "time_ms": (time.time() - start_time) * 1000,
            "memory_mb": tracemalloc.get_traced_memory()[1] / (1024 * 1024),
            "solution_path": None
        }

    import tracemalloc
    import time

    def dfs(self):
        stack = [(self, [], 0)]  # start from initial state with an empty path
        visited = set()  # To avoid revisiting the same state
        initial_state = self.get_state()
        visited.add(initial_state)  # Add initial state to visited
        print(f"Initial state: {initial_state}")

        # Track memory and time
        nodes_generated = 0
        tracemalloc.start()
        start_time = time.time()

        while stack:
            (current_game, path, total_cost) = stack.pop()
            current_state = current_game.get_state()

            # print(f"Exploring state: {current_state}, Path: {path}, Total cost: {total_cost}")

            # Check if current state is a goal state
            if current_game.is_goal_state():
                end_time = time.time()
                memory_used = tracemalloc.get_traced_memory()[1] / (1024 * 1024)  # Peak memory in MB
                tracemalloc.stop()

                # Steps are the length of the path taken to reach the goal
                steps = len(path)
                total_time = (end_time - start_time) * 1000  # Time in milliseconds

                return {
                    "cost": total_cost,
                    "steps": steps,
                    "nodes_generated": nodes_generated,
                    "time_ms": total_time,
                    "memory_mb": memory_used,
                    "solution_path": path
                }

            # Generate successors from the current state
            for successor_game, move_dir, move_cost in current_game.getSuccessors():
                successor_state = successor_game.get_state()
                nodes_generated += 1
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
                        #print(f"Enqueued successor state: {successor_game.get_state()}, Path so far: {new_path}, Cost: {total_cost + move_cost}")


        print("No solution found.")
        tracemalloc.stop()
        return {
            "cost": None,
            "steps": None,
            "nodes_generated": nodes_generated,
            "time_ms": (time.time() - start_time) * 1000,
            "memory_mb": tracemalloc.get_traced_memory()[1] / (1024 * 1024),
            "solution_path": None
        }

    def ucs(self):

        # Counter for tie-breaking
        counter = itertools.count()
    
        frontier = [(0, next(counter), self, [])]  # (cost, count, position, path)
        # Dictionary to track the minimum cost to reach each state
        path_cost = {self.get_state(): 0}
        initial_state = self.get_state()
        explored = set()
        explored.add(initial_state)
        print(f"Initial state: {initial_state}")
        # Track memory
        nodes_generated = 0
        tracemalloc.start()  
        start_time = time.time()
        while frontier:
            #pop the node with lowest cost 
            (cost,_,current_position,path) = heapq.heappop(frontier)
            current_state = current_position.get_state()
            # If we reach the goal, return the path
            if current_position.is_goal_state():
                end_time = time.time()
                memory_used = tracemalloc.get_traced_memory()[1] / (1024 * 1024)  # Peak memory in MB
                tracemalloc.stop()

                # Steps are the length of the path taken to reach the goal
                steps = len(path)
                total_time = (end_time - start_time) * 1000  # Time in milliseconds
            
                # Return all metrics and the solution path
                return {
                    "cost": cost,
                    "steps": steps,
                    "nodes_generated": nodes_generated,
                    "time_ms": total_time,
                    "memory_mb": memory_used,
                    "solution_path": path
            }

            for successor_game, move_dir, move_cost in current_position.getSuccessors():   
                successor_state = successor_game.get_state()
                nodes_generated += 1
                if successor_state not in explored or (cost + move_cost) < path_cost[successor_state]:
                        # add duplicated entry but when node expand this code in explored and has more cost than current cost 
                        # so it does not affect to algorithm
                    path_cost[successor_state] = cost + move_cost
                    new_path = path + [move_dir]
                    heapq.heappush(frontier, (cost + move_cost, next(counter), successor_game, new_path))
                    explored.add(successor_state)
                        #print(f"Enqueued successor state: {successor_game.get_state()}, Path so far: {new_path}, Cost: {cost + move_cost}")
        print(f"No Solution found.") 
        tracemalloc.stop()
        end_time = time.time()
        total_time = (end_time - start_time) * 1000  # Time in milliseconds
        memory_used = tracemalloc.get_traced_memory()[1] / (1024 * 1024)  # Peak memory in MB
               
        return {
        "cost": None,
        "steps": None,
        "nodes_generated": nodes_generated,
        "time_ms": total_time,
        "memory_mb": memory_used,
        "solution_path": None
    }
    

