import tkinter as tk
from utils import parse_input
from game_ui import MazeGameUI

def main():
    grid, stone_weights = parse_input("input-03.txt")
    root = tk.Tk()
    app = MazeGameUI(root,grid, stone_weights)
    root.mainloop()


if __name__ == "__main__":
    main()