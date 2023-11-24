import pygame
import numpy as np
import igraph as ig
from dataclasses import dataclass
from grasim import savefile

import glob

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

def start_game(unparsed_save: str, game : Game):

    offsetX = 0
    offsetY = 0
    zoom = 1

    font_screen = game.font.render("<ENTER> step; <BACK> choose save", True, "white", "black")
    game.screen.blit(font_screen, np.array(game.size)-font_screen.get_size())

    graph = savefile.parse_text(unparsed_save)

    adjancy_matrix = graph.graph_matrix.copy()
    adjancy_matrix[adjancy_matrix == -1] = 0
    adjancy_matrix[adjancy_matrix != 0] = 1

    # Use igraph to make the graph pretty: position nodes better
    points = np.array(ig.Graph.Adjacency(adjancy_matrix, mode="min").layout().coords)
    points = points + abs(points.min(0))
    points = ((points / abs(points).max(0) + 0.02) * game.size * 0.9)

    djakstrar_table = np.ones((graph.graph_matrix.shape[0], 4)) * [np.inf, 0, 0, np.inf] # distance, last_idx, done, estimated_total
    djakstrar_table[graph.start_idx] = [0, graph.start_idx, 0, 0]

    running = True
    can_continue = False
    should_draw = True
    while running:

        if should_draw:
            should_draw = False
            # drawing everything
            game.screen.fill("black")
            draw_points = points * zoom + [offsetX, offsetY]
            for point, name in zip(draw_points, graph.node_lookup.keys()):
                # If node is not done draw purple, otherwise green
                if djakstrar_table[graph.node_lookup[name], 0] == np.inf:
                    pygame.draw.circle(game.screen, "purple", point, 5)
                elif djakstrar_table[graph.node_lookup[name], 2] != 1:
                    pygame.draw.circle(game.screen, "green", point, 5)
                else:
                    pygame.draw.circle(game.screen, "orange", point, 5)
                font_screen = game.font.render(f"{name}{(graph.heuristics[graph.node_lookup[name]])}", True, "white", "black")
                game.screen.blit(font_screen, point+5)

            for idx1, idx2 in np.column_stack(np.where(graph.graph_matrix != -1)):
                # if path is explored draw green otherwise white
                if (int(djakstrar_table[idx1, 1]) == idx2) and djakstrar_table[idx1, 2] == 1.0:
                    pygame.draw.line(game.screen,"green", draw_points[idx1], draw_points[idx2], 5)
                else:
                    pygame.draw.line(game.screen,"white", draw_points[idx1], draw_points[idx2])
                font_screen = game.font.render(f"{graph.graph_matrix[idx1, idx2]}", True, "white", "black")
                game.screen.blit(font_screen, (draw_points[idx1] + draw_points[idx2])/2-5)

            if djakstrar_table[graph.end_idx, 2] == 1:
                traverse_idx = graph.end_idx
                while traverse_idx != graph.start_idx:
                    traverse_idx2 = int(djakstrar_table[traverse_idx, 1])
                    pygame.draw.line(game.screen,"orange", draw_points[traverse_idx], draw_points[traverse_idx2], 5)
                    traverse_idx = traverse_idx2
            # End drawing
        
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            should_draw = True
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSPACE:
                    running = False
                if event.key == pygame.K_RETURN:
                    can_continue = True
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            offsetY += 20*abs(zoom)
            should_draw = True
        elif keys[pygame.K_DOWN]:
            offsetY -= 20*abs(zoom)
            should_draw = True
        if keys[pygame.K_LEFT]:
            offsetX += 20*abs(zoom)
            should_draw = True
        elif keys[pygame.K_RIGHT]:
            offsetX -= 20*abs(zoom)
            should_draw = True
        if keys[pygame.K_PLUS]:
            zoom += 0.1
            offsetX -= game.size[0]*0.1/2
            offsetY -= game.size[1]*0.1/2
            should_draw = True
        elif keys[pygame.K_MINUS]:
            zoom -= 0.1 
            offsetX += game.size[0]*0.1/2
            offsetY += game.size[1]*0.1/2
            should_draw = True

        # expand
        valid_idx = np.where((djakstrar_table[:, 2] == 0) & (djakstrar_table[:, 3] != np.inf))[0]

        # if there is a valid node left to explore
        if (len(valid_idx) != 0) and can_continue:
            can_continue = False
            next_idx = valid_idx[djakstrar_table[valid_idx, 3].argmin()]

            djakstrar_table[next_idx][2] = 1

            for idx_expand in np.where(graph.graph_matrix[next_idx] != -1)[0]:
                distance = graph.graph_matrix[next_idx, idx_expand] + djakstrar_table[next_idx, 0]
                estimated_total = distance \
                    + graph.heuristics[idx_expand]
                # if is not done and distance is smaller than already there
                if djakstrar_table[idx_expand][2] == 0 \
                    and djakstrar_table[idx_expand][0] > estimated_total:
                    djakstrar_table[idx_expand] = [distance, next_idx, 0, estimated_total]
        

        pygame.display.flip()

        game.clock.tick(20)  # limits FPS to 60

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
        game.clock.tick(20)


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