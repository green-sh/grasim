from grasim.graph_generator import create_random_graph
import pygame
import numpy as np
import igraph as ig
import traceback
from dataclasses import dataclass
from grasim import savefile
from grasim.dijkstra import dijkstra
import os
import pathlib
from grasim.errors import ParseError
import grasim.config as config

@dataclass
class Game:
    """The game class that holds all the game state"""
    pygame.init()
    screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    font = pygame.font.Font(pygame.font.get_default_font(), config.FONT_SIZE)
    dijkstra_mode = False

def read_file(file: pathlib.Path):
    with file.open("r") as f:
        return f.readlines()

def show_error(message: str, game):
    error_font_display = game.font.render("We cannot parse this! " + message, True, config.ERROR_TEXT_COLOR)
    game.screen.blit(error_font_display, (100, 0))
    pygame.display.flip()
    game.clock.tick(1)
    return
    
def interpolate_coords(point1 : np.ndarray, point2 : np.ndarray, percent : float) -> np.ndarray:
    return (point2 - point1) * percent + point1 

def show_level(unparsed_save: str, game : Game):
    """The level screen"""
    offset = np.array([0.0, 0.0])
    zoom = 1

    try:
        graph = savefile.parse_text(unparsed_save)
    except ParseError as parse:
        show_error("This file cannot be parsed! " + parse.msg, game)
        return
    except Exception as e:
        traceback.print_exc()
        show_error("This file cannot be parsed! Uncaptured error: " + str(e), game)
        return

    adjancy_matrix = graph.graph_matrix.copy()
    # adjancy_matrix[adjancy_matrix == -1] = 0 # TODO: https://github.com/green-sh/grasim/issues/20
    # adjancy_matrix[adjancy_matrix != 0] = 1

    # Use igraph to make the graph pretty: position nodes better
    # Fix issue https://github.com/green-sh/grasim/issues/15 ugly graphs
    full_graph_adjancy = adjancy_matrix + adjancy_matrix.T
    full_graph_adjancy = np.where(full_graph_adjancy > -1, 1, 0) 

    layout = "auto"
    if len(graph.node_lookup) < 5:
        layout = "circle"
    points = np.array(ig.Graph.Adjacency(full_graph_adjancy, mode="directed").layout(layout).coords)

    points = points + abs(points.min(0))
    points = ((points / (abs(points).max(0) + 0.02)) * game.screen.get_size() * 0.9)

    cos, sin = np.cos(0.07), np.sin(0.07)
    ROTATION_MATRIX = np.array([[cos, sin], [-sin, cos]])

    dijkstra_table = dijkstra.init_dijkstra_table(num_nodes=graph.graph_matrix.shape[0], start_idx = graph.start_idx)
    dijkstra.dijkstra_step(dijkstra_table, graph, game.dijkstra_mode)

    screen_size = np.array(game.screen.get_size())
    font_display = pygame.surface.Surface(screen_size)
    font_display.set_colorkey((255, 0, 255))
    running = True # This can stop the game
    can_continue = False # c key continues until target reached
    should_draw = True # Only draw if something changed
    counter = 0
    skip_until_end = False
    hide_labels = False
    move_mode = False
    while running:

        if should_draw or skip_until_end:
            should_draw = False
            # drawing Nodes
            game.screen.fill(config.BACKGROUND_COLOR)
            font_display.fill((255, 0, 255))
            points_absolute_pos = (points - screen_size/2) * zoom + offset * zoom + screen_size/2
            # Draw nodes
            for point, name in zip(points_absolute_pos, graph.node_lookup.keys()):
                # If node is not done draw purple, otherwise green
                node_idx = graph.node_lookup[name]
                if graph.end_idx == node_idx:
                    pygame.draw.circle(game.screen, config.NODE_END_COLOR, point, 5)
                elif dijkstra_table[node_idx, 0] == np.inf:
                    pygame.draw.circle(game.screen, config.NODE_UNIDSCOVERED_COLOR, point, 5)
                elif dijkstra_table[node_idx, 2] != 1:
                    pygame.draw.circle(game.screen, config.NODE_DISCOVERED_COLOR, point, 5)
                else:
                    pygame.draw.circle(game.screen, config.NODE_DONE_COLOR, point, 5)
                
                heuristic_text = "" if game.dijkstra_mode else f"{graph.heuristics[graph.node_lookup[name]]:.0f}"
                estimated_total = f"{dijkstra_table[graph.node_lookup[name], 3]:.0f}"
                draw_name = "" if hide_labels else name

                font_screen = game.font.render(f"{draw_name}", False, config.NODE_NAME_COLOR, config.NODE_NAME_BACKGROUND)
                heur_screen = game.font.render(f"{heuristic_text}", False, config.NODE_HEURISTIC_COLOR)
                total_screen = game.font.render(f"{estimated_total}", False, config.NODE_ESTIMATED_TOTAL_COLOR)
                font_size = font_screen.get_size()
                font_display.blit(font_screen, point - [font_size[0]/2, font_size[1]+10])
                font_display.blit(heur_screen, point - [font_size[0]/2, font_size[1]*3+10])
                font_display.blit(total_screen, point - [font_size[0]/2, font_size[1]*2+10])

            # Draw final path
            if dijkstra_table[graph.end_idx, 2] == 1:
                skip_until_end = False
                traverse_idx = graph.end_idx
                while traverse_idx != graph.start_idx:
                    traverse_idx2 = int(dijkstra_table[traverse_idx, 1])
                    pygame.draw.line(game.screen,config.PATH_FINAL_COLOR , points_absolute_pos[traverse_idx], points_absolute_pos[traverse_idx2], 10)
                    traverse_idx = traverse_idx2

            # Draw Paths
            for idx1, idx2 in np.column_stack(np.where(graph.graph_matrix != -1)):

                # if path is explored draw green otherwise white
                if ((int(dijkstra_table[idx1, 1]) == idx2) and dijkstra_table[idx1, 2] == 1.0) or \
                    ((int(dijkstra_table[idx2, 1]) == idx1) and dijkstra_table[idx2, 2] == 1.0):
                    pygame.draw.line(game.screen,config.PATH_DONE, points_absolute_pos[idx1], points_absolute_pos[idx2], 5)
                else:
                    pygame.draw.line(game.screen,config.PATH_OPEN, points_absolute_pos[idx1], points_absolute_pos[idx2])
                # check if connection is directed
                if graph.graph_matrix[idx1, idx2] == graph.graph_matrix[idx2, idx1] and idx1 < idx2:
                    font_screen = game.font.render(f"{graph.graph_matrix[idx1, idx2]:.0f}", True, config.PATH_TEXT_COLOR)
                    direction = (points_absolute_pos[idx1] - points_absolute_pos[idx2])
                    distance = np.linalg.norm(direction)
                    moveAsideOffset = direction / distance
                    font_display.blit(font_screen, (points_absolute_pos[idx1] + points_absolute_pos[idx2])/2 + (moveAsideOffset * distance * config.NODE_TEXT_OFFSET))
                elif idx1 < idx2: # directed
                    distance1 = graph.graph_matrix[idx1, idx2]
                    distance2 = graph.graph_matrix[idx2, idx1]
                    if distance1 != -1:
                        font_screen_left = game.font.render(f"{distance1:.0f}", True, config.PATH_TEXT_COLOR)
                        font_display.blit(font_screen_left, interpolate_coords(points_absolute_pos[idx1], points_absolute_pos[idx2], 0.8))
                    if distance2 != -1:
                        font_screen_right = game.font.render(f"{distance2:.0f}", True, config.PATH_TEXT_COLOR)
                        font_display.blit(font_screen_right, interpolate_coords(points_absolute_pos[idx1], points_absolute_pos[idx2], 0.2))

            font_screen = game.font.render("Inputs: Step: <ENTER>, <BACK>, [c]ontinue, [r]otate, [h]ide labels | Navigate: +, -, <UP>, <DOWN>, <LEFT>, <RIGHT>", True, config.LEGEND_TEXT, config.LEGEND_BACKGROUND)
            font_display.blit(font_screen, screen_size-font_screen.get_size())

            counter_screen = game.font.render(f"Steps: {counter}", True, "white", "black")
            font_display.blit(counter_screen, (screen_size[0] - counter_screen.get_size()[0], counter_screen.get_size()[1]))
            # End drawing
        
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                should_draw = True
                if event.key == pygame.K_BACKSPACE:
                    running = False
                if event.key == pygame.K_RETURN:
                    can_continue = True
                if event.key == pygame.K_h:
                    hide_labels = not hide_labels
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_left, _, mouse_right = pygame.mouse.get_pressed(3)
                should_draw = True
                if mouse_left:
                    move_mode = True
                    pygame.mouse.get_rel() # reset relative position of mouse
                if mouse_right:
                    can_continue = True
            if event.type == pygame.MOUSEWHEEL:
                zoom *= 1 + event.y/10
            if event.type == pygame.MOUSEBUTTONUP:
                if mouse_left:
                    move_mode = False

        mouse_left, _, _ = pygame.mouse.get_pressed()
        if mouse_left and move_mode:
            offset += np.array(pygame.mouse.get_rel()) / abs(zoom)
            should_draw = True
            
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            offset[1] += 20 / abs(zoom)
            should_draw = True
        elif keys[pygame.K_DOWN]:
            offset[1] -= 20 / abs(zoom)
            should_draw = True
        if keys[pygame.K_LEFT]:
            offset[0] += 20 / abs(zoom)
            should_draw = True
        elif keys[pygame.K_RIGHT]:
            offset[0] -= 20 / abs(zoom)
            should_draw = True
        if keys[pygame.K_PLUS]:
            zoom *= 1.05
            #offset -= screen_size*0.1/2
            should_draw = True
        elif keys[pygame.K_MINUS]:
            zoom /= 1.05
            #offset += screen_size*0.1/2
            should_draw = True
        elif keys[pygame.K_r]:
            points = np.dot(ROTATION_MATRIX, (points - screen_size/2).T).T + screen_size/2
            should_draw = True
        elif keys[pygame.K_c]:
            skip_until_end = True
        
        if can_continue or skip_until_end:
            can_continue = False
            if dijkstra.dijkstra_step(dijkstra_table, graph, game.dijkstra_mode):
                counter += 1
        
        game.screen.blit(font_display, (0, 0))

        pygame.display.flip()

        # use this to make screen video
        # filename = "screen_%04d.png" % ( counter )
        # pygame.image.save( game.screen, filename )

        game.clock.tick(20)  # limits FPS to 60


def select_level_screen(game: Game, savedir : pathlib.Path):

    saves = [x for x in savedir.glob("*") if x.is_dir or x.suffix == ".graph"]

    if len(saves) == 0:
        saves.append(f"Couldn't find any saves in dir \"{savedir.name}\". You can start the programm with the -d <Directory> flag")

    selected_save_id = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_d:
                    game.dijkstra_mode = not game.dijkstra_mode
                if event.key == pygame.K_UP:
                    selected_save_id -= 1
                if event.key == pygame.K_DOWN:
                    selected_save_id += 1
                if event.key == pygame.K_BACKSPACE:
                    running = False
                if event.key == pygame.K_RETURN:
                    # Savefile was selected in selectio screen
                    if saves[selected_save_id].is_dir():
                        savedir = saves[selected_save_id]
                        saves = [x for x in savedir.glob("*") if x.is_dir or x.suffix == ".graph"] \
                                + [ savedir.joinpath("..") ]
                    else:
                        graphtext = read_file(saves[selected_save_id])
                        show_level(graphtext, game)

                selected_save_id = selected_save_id % len(saves)

        game.screen.fill(config.LEVEL_SELECTION_BACKGROUND)        
        
        # Draw
        yDrawPosition = 100 # Where to draw the level name
        for i, savename in enumerate(saves[selected_save_id:] + saves[:selected_save_id]):
            color = config.LEVEL_SELECTION_TEXT_BACK
            if savename == saves[selected_save_id]:
                color = config.LEVEL_SELECTION_TEXT_BACK_HOVER
            save_name_screen = game.font.render(savename.name, False, config.LEVEL_SELECTION_TEXT, color)
            game.screen.blit(save_name_screen, (100, yDrawPosition))
            yDrawPosition += save_name_screen.get_size()[1]
        
        if game.dijkstra_mode: # If dijkstra is chosen
            dijkstramode_text = "Current mode is: Dijkstra   Press D to switch to A*"
        else:
            dijkstramode_text = "Current mode is: A*         Press D to switch to Dijkstra"
        dijkstramode_font = game.font.render(dijkstramode_text, False, config.LEGEND_TEXT)
        game.screen.blit(dijkstramode_font, (game.screen.get_size()[0]-dijkstramode_font.get_size()[0], game.screen.get_size()[1]-20))

        pygame.display.flip()
        game.clock.tick(20)

def start_game(safedir = "."):
    # pygame setup
    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    select_level_screen(game, savedir=pathlib.Path(safedir))
                    game.screen.fill("black")

        # Show Hello Box
        button_size = [300, 100]
        pygame.draw.rect(game.screen, "white", 
            (game.screen.get_size()[0]/2-button_size[0]/2, game.screen.get_size()[1]/2-button_size[1]/2, button_size[0], button_size[1]), 2)
        
        text_surface = game.font.render("Press enter to start", True, "white", "black")
        game.screen.blit(text_surface, (game.screen.get_size()[0]/2 - text_surface.get_size()[0]/2, game.screen.get_size()[1]/2 - text_surface.get_size()[1]/2))

        pygame.display.flip()

        game.clock.tick(20)