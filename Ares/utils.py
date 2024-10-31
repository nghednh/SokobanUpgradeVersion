def parse_input(file_path):
    with open(file_path, 'r') as f:
        weight_line = f.readline().strip()
        stone_weights = []
        for token in weight_line.split():
            try:
                stone_weights.append(int(token))
            except ValueError:
                print(f"Warning: Found non-integer value in weights: {token}")
                continue

        grid = []
        for line in f:
            line = line.rstrip()
            if line:
                grid.append(list(line))

    return grid, stone_weights