import tkinter as tk
from PIL import Image, ImageTk
import itertools
from game import MazeGame
import time
from utils import parse_input
import re
import tracemalloc
class MazeGameUI:
    def __init__(self, root,grid, stone_weights):
        self.root = root
        self.root.title("Ares's Adventure")

        self.game = MazeGame(grid,stone_weights)
        self.grid_frame = tk.Canvas(root, width=1500, height=600, bg="white")
        self.grid_frame.pack()
        self.label_cost = tk.Label(root, text=f"Total Cost: {self.game.total_cost}")
        self.label_cost.pack()
        self.goal_reached=False
        self.cell_size = 50 
        self.level = 0
        match = re.search(r'\d+',"input-01.txt")
        if match:
            self.level = match.group()
        self.animation_speed = 100  # Default speed for idle animation

        self.images = {
            '#': self.load_image("asset/Items/Boxes/Box3/Idle.png"),
            '$': self.load_image("asset/Other/Dust Particle.png"),
            '.': self.load_image("asset/Menu/Buttons/Close.png"),
            '*': self.load_image("asset/Items/Checkpoints/End/End (Idle).png"),
            ' ': self.load_image("asset/Background/Blue.png")
        }

        # Load animations for '@' and '+' characters separately
        self.ares_idle_animation = self.load_animation("asset/Main Characters/Mask Dude/Idle (32x32).png", 11)
        self.ares_double_jump_animation = self.load_animation("asset/Main Characters/Mask Dude/Hit (32x32).png", 7)
        self.idle_animation_speed = 100  # Set speed for idle animation
        self.jump_animation_speed = 50  # Set speed for double jump animation
        # Frame iterators for each animation
        self.ares_idle_frames = itertools.cycle(self.ares_idle_animation)
        self.ares_double_jump_frames = itertools.cycle(self.ares_double_jump_animation)

        root.bind("<w>", lambda e: self.move((-1, 0)))
        root.bind("<a>", lambda e: self.move((0, -1)))
        root.bind("<s>", lambda e: self.move((1, 0)))
        root.bind("<d>", lambda e: self.move((0, 1)))

        self.draw_grid()
        
        self.animate()  # Start animation loop

        self.create_buttons()

        # Rest of initialization code...

    def create_buttons(self):
        # Frame to contain the buttons
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=10)

        # Button definitions
        btn1 = tk.Button(button_frame, text="DFS", command=self.dfs)
        btn2 = tk.Button(button_frame, text="BFS", command=self.bfs)
        btn3 = tk.Button(button_frame, text="UCS", command=self.ucs)
        btn4 = tk.Button(button_frame, text="A*", command=self.astar)
        btn_reset = tk.Button(button_frame,text = "Reset game",command= self.reset_game)
        # Dropdown menu for choosing level
        self.level_var = tk.StringVar(self.root)
        self.level_var.set("Select Level")  # Default text for the dropdown

        # Options for level selection
        level_options = {"Level 1": "input-01.txt", 
                         "Level 2": "input-02.txt", 
                         "Level 3": "input-03.txt",
                         "Level 4": "input-04.txt",
                         "Level 5": "input-05.txt",
                         "Level 6": "input-06.txt",
                         "Level 7": "input-07.txt",
                         "Level 8": "input-08.txt",
                         "Level 9": "input-09.txt",
                         "Level 10": "input-10.txt",}
        self.level_menu = tk.OptionMenu(button_frame, self.level_var, *level_options.keys())
        self.level_menu.pack(side="left", padx=5)
        btn5 = tk.Button(button_frame, text="Load Level", command=lambda: self.load_selected_level(level_options))
        btn5.pack(side="left", padx=5)
        btn1.pack(side="left", padx=10, pady=5)
        btn2.pack(side="left", padx=10, pady=5)
        btn3.pack(side="left", padx=10, pady=5)
        btn4.pack(side="left", padx=10, pady=5)
        btn_reset.pack(side="left", padx=10, pady=5)

    def load_selected_level(self, level_options):
        # Get the chosen level's filename from the level_options dictionary
        selected_level = self.level_var.get()
        if selected_level in level_options:
            filename = level_options[selected_level]
            self.grid_frame.delete("all")  # Clear the canvas
            self.label_cost.config(text="Total Cost: 0")  # Reset the cost label
            self.goal_reached = False  # Reset goal state          
            self.game = None  # Remove the current game instance
            gird, stone_weights = parse_input(filename)
            match = re.search(r'\d+',filename)
            if match:
                self.level = match.group()
            self.game = MazeGame(gird, stone_weights)
            self.reset_animation()
            self.draw_grid()

        else:
            print("Please select a valid level.")
    def reset_game(self):
        # Code to reset the game
        print("Game reset!")
        self.grid_frame.delete("all")  # Clear the canvas
        self.label_cost.config(text="Total Cost: 0")  # Reset the cost label
        self.goal_reached = False  # Reset goal state          
        self.game.reset()
       
        self.reset_animation()

        self.draw_grid()

    def show_hint(self):
        # Code to provide a hint to the user
        print("Hint: Try moving up!")
        # Display hint logic here

    def speed_up(self):
        # Code to increase the animation speed
        print("Speeding up!")
        self.animation_speed = max(10, self.animation_speed - 10)  # Speed up to a certain limit

    def load_image(self, path):
        image = Image.open(path).convert("RGBA")
        image = image.resize((self.cell_size, self.cell_size), Image.LANCZOS)
        return ImageTk.PhotoImage(image)

    def load_animation(self, path, frames):
        sprite_sheet = Image.open(path)
        frame_width = sprite_sheet.width // frames
        animation_frames = []
        for i in range(frames):
            frame = sprite_sheet.crop((i * frame_width, 0, (i + 1) * frame_width, sprite_sheet.height))
            frame = frame.resize((self.cell_size, self.cell_size), Image.LANCZOS)
            animation_frames.append(ImageTk.PhotoImage(frame))
        return animation_frames

    def draw_grid(self):
        self.grid_frame.delete("all")

        for r, row in enumerate(self.game.grid):
            for c, cell in enumerate(row):
                x1 = c * self.cell_size
                y1 = r * self.cell_size
                self.grid_frame.create_image(x1, y1, anchor='nw', image=self.images[' '])

                if cell == '@':
                    self.grid_frame.create_image(x1, y1, anchor='nw', image=next(self.ares_idle_frames))
                elif cell == '+':
                    self.grid_frame.create_image(x1, y1, anchor='nw', image=next(self.ares_double_jump_frames))
                elif cell != ' ':
                    self.grid_frame.create_image(x1, y1, anchor='nw', image=self.images[cell])

                if cell in {'$', '*'}:
                    stone_idx = self.game.get_stone_index((r, c))
                    if stone_idx is not None:
                        weight_text = str(self.game.stone_weights[stone_idx])
                        self.grid_frame.create_text(
                            x1 + self.cell_size / 2, y1 + self.cell_size / 2,
                            text=weight_text, fill="black", font=("Arial", 12),
                            anchor='center'
                        )

        self.label_cost.config(text=f"Total Cost: {self.game.total_cost}")

    def animate(self):
        # Call draw_grid to refresh the animation frames
        self.draw_grid()
        self.root.after(self.idle_animation_speed, lambda: next(self.ares_idle_frames))
        self.root.after(self.jump_animation_speed, lambda: next(self.ares_double_jump_frames))
        # Schedule animate to run again after self.animation_speed milliseconds
        self.root.after(self.animation_speed, self.animate)

    def move(self, direction):
        if self.game.move(direction):
            self.draw_grid()  # Update grid position immediately after move

            if self.game.is_goal_state() and not self.goal_reached:
                self.show_congratulations()
                self.goal_reached = True
                self.increase_speed_and_load_new_animation()

    def show_congratulations(self):
        print("Congratulations! You completed the challenge!")
        congrats = tk.Label(self.root, text="Congratulations! You completed the challenge!")
        congrats.pack()

    def increase_speed_and_load_new_animation(self):
        self.animation_speed = 40  # Increase speed after reaching goal

        # Load the new animation for Ares's idle and double jump actions
        new_animation_path = "asset/Main Characters/Mask Dude/Double Jump (32x32).png"
        self.ares_double_jump_animation = self.load_animation(new_animation_path, 6)
        self.ares_idle_animation = self.load_animation(new_animation_path, 6)

        # Update frame iterators to cycle through the new animations
        self.ares_double_jump_frames = itertools.cycle(self.ares_double_jump_animation)
        self.ares_idle_frames = itertools.cycle(self.ares_idle_animation)

    def reset_animation(self):
        self.animation_speed = 100  
        self.ares_idle_animation = self.load_animation("asset/Main Characters/Mask Dude/Idle (32x32).png", 11)
        self.ares_double_jump_animation = self.load_animation("asset/Main Characters/Mask Dude/Hit (32x32).png", 7)
        self.idle_animation_speed = 100  # Set speed for idle animation
        self.jump_animation_speed = 50  # Set speed for double jump animation
        # Frame iterators for each animation
        self.ares_idle_frames = itertools.cycle(self.ares_idle_animation)
        self.ares_double_jump_frames = itertools.cycle(self.ares_double_jump_animation)
        
    def dfs(self):
        solution_path=self.game.dfs()
        if solution_path:
            self.simulate_solution(solution_path)
        else:
            print("No solution")
        
    def bfs(self):
        solution_path=self.game.bfs()
        if solution_path:
            self.simulate_solution(solution_path)
        else:
            print("No solution")

    def ucs(self):
        result=self.game.ucs()
        solution_path = result["solution_path"]
        if solution_path:
            self.simulate_solution(solution_path)
            steps = result["steps"]
            nodes_generated = result["nodes_generated"]
            cost = result["cost"]
            time_ms = result["time_ms"]
            memory_mb = result["memory_mb"]
            self.write_output("UCS", solution_path, steps, cost, nodes_generated,time_ms,memory_mb)
        else:
            print("No solution")

    def astar(self):
        solution_path=self.game.a_star()
        if solution_path:
            self.simulate_solution(solution_path)
        else:
            print("No solution")

    def simulate_solution(self, solution_path):
   
        if not solution_path:
            print("No solution path provided.")
            return

        def step(index):
            if index < len(solution_path):
            # Mapping the direction and making the move
                direction_map = {
                'U': (-1, 0), 'D': (1, 0), 'L': (0, -1), 'R': (0, 1),
                'u': (-1, 0), 'd': (1, 0), 'l': (0, -1), 'r': (0, 1)
                }
                move_dir = solution_path[index]
                dr, dc = direction_map[move_dir]
                self.move((dr, dc))  # Move within the UI

            # Schedule the next step with a delay
            self.root.after(100, step, index + 1)

        # Start the first step
        step(0)
        
    def write_output(self,algorithm_name,solution_path, steps, cost, nodes_generated,time_ms,memory_mb):
    
        # Prepare the output file path
        output_filename = f"output-{self.level}.txt"

        # Prepare solution details for output
        solution_string = ''.join(solution_path)  

        # Write to output file
        with open(output_filename, 'w') as f:
            f.write(f"{algorithm_name}\n")
            f.write(f"Steps: {steps}, Cost: {cost}, Node: {nodes_generated}, "
                    f"Time (ms): {time_ms:.2f}, Memory (MB): {memory_mb:.2f}\n")
            f.write(solution_string)
