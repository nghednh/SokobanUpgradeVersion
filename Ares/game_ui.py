import tkinter as tk
from PIL import Image, ImageTk
import itertools
from game import MazeGame
class MazeGameUI:
    def __init__(self, root, grid, stone_weights):
        self.root = root
        self.root.title("Ares's Adventure")

        self.game = MazeGame(grid, stone_weights)
        self.grid_frame = tk.Canvas(root, width=800, height=600, bg="white")
        self.grid_frame.pack()
        self.label_cost = tk.Label(root, text=f"Total Cost: {self.game.total_cost}")
        self.label_cost.pack()
        self.goal_reached=False
        self.cell_size = 50
        self.animation_speed = 100  # Default speed for idle animation

        self.images = {
            '#': self.load_image("Ares/asset/Items/Boxes/Box3/Idle.png"),
            '$': self.load_image("Ares/asset/Other/Dust Particle.png"),
            '.': self.load_image("Ares/asset/Menu/Buttons/Close.png"),
            '*': self.load_image("Ares/asset/Items/Checkpoints/End/End (Idle).png"),
            ' ': self.load_image("Ares/asset/Background/Blue.png")
        }

        # Load animations for '@' and '+' characters separately
        self.ares_idle_animation = self.load_animation("Ares/asset/Main Characters/Mask Dude/Idle (32x32).png", 11)
        self.ares_double_jump_animation = self.load_animation("Ares/asset/Main Characters/Mask Dude/Hit (32x32).png", 7)
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
        new_animation_path = "Ares/asset/Main Characters/Mask Dude/Double Jump (32x32).png"
        self.ares_double_jump_animation = self.load_animation(new_animation_path, 6)
        self.ares_idle_animation = self.load_animation(new_animation_path, 6)

        # Update frame iterators to cycle through the new animations
        self.ares_double_jump_frames = itertools.cycle(self.ares_double_jump_animation)
        self.ares_idle_frames = itertools.cycle(self.ares_idle_animation)