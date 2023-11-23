import pygame
import numpy as np
from dataclasses import dataclass

import glob
import re
from typing import TypeVar

@dataclass
class Game:
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    size = screen.get_size()
    clock = pygame.time.Clock()
    font = pygame.font.Font(pygame.font.get_default_font())

def read_file(filename: str):
    with open(filename, "r") as f:
        return f.readlines()


# list of (node1, distance, node2)
NodeDistances = list[tuple[str, int, str]]

def start_game(unparsed_save: str, game : Game):

    game.screen.fill("black")
    
    # TODO function: parse_graph
    nodes : set = set()
    heuristics_dict = {}
    distances : NodeDistances = []
    start : str | None
    end : str | None 

    node_node_connection_regex = re.compile(r"(\w+) -(\d+)- (\w+)")
    node_heuristic_regex = re.compile(r"(\w+)\((\d+)\)")
    node_start_regex = re.compile(r"START (\w+)")
    node_end_regex = re.compile(r"END (\w+)")

    for line_idx, line in enumerate(unparsed_save):        
        if match := node_node_connection_regex.match(line):
            node1, estimated_total, node2 = match.groups()
            nodes.add(node1)
            nodes.add(node2)
            distances.append((node1, float(estimated_total), node2))
        elif match := node_heuristic_regex.match(line):
            node, heuristic = match.groups()
            heuristics_dict[node] = float(heuristic)
        elif match := node_start_regex.match(line):
            start = str(match.group(1))
        elif match := node_end_regex.match(line):
            end = str(match.group(1))

    # Create Graph matrix
    graph_matrix = np.full((len(nodes), len(nodes)), -1, dtype=np.int16)
    
    # Lookuptable for variables 'A' -> 0, 'B' -> 1
    node_lookup = dict(zip(list(nodes), range(len(nodes)))) 
    # Write distance into graph
    for node1, estimated_total, node2 in distances:
        idx1 = node_lookup[node1]
        idx2 = node_lookup[node2]
        graph_matrix[idx1, idx2] = estimated_total
        graph_matrix[idx2, idx1] = estimated_total

    start_idx = node_lookup[start]
    end_idx = node_lookup[end]

    heuristics = [heuristics_dict[x] for x in node_lookup.keys()]

    # end function parse graph


    points = np.random.random((graph_matrix.shape[0], 2))
    points = (points * game.screen.get_size())

    for point, name in zip(points, node_lookup.keys()):
        pygame.draw.circle(game.screen, "purple", point, 5)
        font_screen = game.font.render(f"{name}{(heuristics_dict[name])}", True, "white", "black")
        game.screen.blit(font_screen, point+5)

    for idx1, idx2 in np.column_stack(np.where(graph_matrix != -1)):
        pygame.draw.line(game.screen,"white", points[idx1], points[idx2])
        font_screen = game.font.render(f"{graph_matrix[idx1, idx2]}", True, "white", "black")
        game.screen.blit(font_screen, (points[idx1] + points[idx2])/2-5)

    djakstrar_table = np.ones((graph_matrix.shape[0], 4)) * [np.inf, 0, 0, np.inf] # distance, last_idx, done, estimated_total
    djakstrar_table[start_idx] = [0, start_idx, 0, 0]

    running = True
    can_continue = False
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    running = False
                if event.key == pygame.K_RETURN:
                    can_continue = True

        # expand
        valid_idx = np.where((djakstrar_table[:, 2] == 0) & (djakstrar_table[:, 3] != np.inf))[0]

        # if there is a valid node left to explore
        if (len(valid_idx) != 0) and can_continue:
            can_continue = False
            next_idx = valid_idx[djakstrar_table[valid_idx, 3].argmin()]

            djakstrar_table[next_idx][2] = 1
            pygame.draw.circle(game.screen, "green", points[next_idx], 5)
            pygame.draw.line(game.screen, "green", points[next_idx], points[int(djakstrar_table[next_idx, 1])], 5)

            for idx_expand in np.where(graph_matrix[next_idx] != -1)[0]:
                distance = graph_matrix[next_idx, idx_expand] + djakstrar_table[next_idx, 0]
                estimated_total = distance \
                    + heuristics[idx_expand]
                # if is not done and distance is smaller than already there
                if djakstrar_table[idx_expand][2] == 0 \
                    and djakstrar_table[idx_expand][0] > estimated_total:
                    djakstrar_table[idx_expand] = [distance, next_idx, 0, estimated_total]
                    pygame.draw.circle(game.screen, "yellow", points[idx_expand], 5)
        
                if djakstrar_table[end_idx, 2] == 1:
                    traverse_idx = end_idx
                    while traverse_idx != start_idx:
                        traverse_idx2 = int(djakstrar_table[traverse_idx, 1])
                        pygame.draw.line(game.screen, "orange", points[traverse_idx], points[traverse_idx2], 5)
                        traverse_idx = traverse_idx2

        pygame.display.flip()

        game.clock.tick(60)  # limits FPS to 60


def select_level_screen(game: Game):

    saves = glob.glob("*.graph")

    selected_save = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_save -= 1
                if event.key == pygame.K_DOWN:
                    selected_save += 1
                if event.key == pygame.K_RETURN:
                    savefile = read_file(saves[selected_save])
                    start_game(savefile, game)

        for i, savename in enumerate(saves):
            color = "black"
            if i == selected_save:
                color = "red"
            save_screen = game.font.render(savename, 1, "white", color)
            game.screen.blit(save_screen, (0, 20*i))

        pygame.display.flip()


def start():
    # pygame setup
    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    select_level_screen(game)
                    game.screen.fill("black")

        # Show Hello Box
        button_size = [300, 100]
        pygame.draw.rect(game.screen, "white", 
            (game.size[0]/2-button_size[0]/2, game.size[1]/2-button_size[1]/2, button_size[0], button_size[1]), 2)
        
        text_surface = game.font.render("Press enter to start", True, "white", "black")
        game.screen.blit(text_surface, (game.size[0]/2 - text_surface.get_size()[0]/2, game.size[1]/2 - text_surface.get_size()[1]/2))

        pygame.display.flip()

        game.clock.tick(20)
        # pygame.event.wait()

if __name__ == "__main__":
    start()