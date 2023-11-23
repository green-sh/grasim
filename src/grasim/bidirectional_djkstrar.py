# Example file showing a basic pygame "game loop"
import pygame
import numpy as np
from scipy import spatial

def distance(n, m):
    return np.linalg.norm(n - m)


# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))

# generate points
num_points = 10000
points = np.random.random((num_points, 2))
points = (points * screen.get_size())

nth_closest = 3
graph_table = np.full([len(points), len(points)], fill_value=np.False_, dtype=np.bool_)

screen.fill("black")
# Distribute points along the screen
kdtree = spatial.KDTree(points)
for idx in range(len(points)):
    # lookup closest in tree
    # +1 because of itself
    idx_closests = kdtree.query(points[idx], nth_closest+1)[1]
    for ydx in idx_closests:
        if idx != ydx:
            pygame.draw.line(screen, "purple", points[idx], points[ydx], width=1)
            graph_table[idx, ydx] = True
            graph_table[ydx, idx] = True

for point in points:
    pygame.draw.circle(screen, "purple", point, 1)

start_idx = 0
pygame.draw.circle(screen, "red", points[start_idx], 5)

end_idx = len(points)-1
pygame.draw.circle(screen, "blue", points[end_idx], 5)

# Store distances from start to each point, the travel point, wether or not it's done
djakstrar_table = np.ones((len(points), 3)) * [np.inf, 0, 0]

# Start with 0
djakstrar_table[0] = [0, 0, 0] # [Distance, last_idx, done]

clock = pygame.time.Clock()
frame_count = 0
running = True
while running:
    # poll for events
    # pygame.QUIT event means the user clicked X to close your window
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # expand
    valid_idx = np.where((djakstrar_table[:, 2] == 0) & (djakstrar_table[:, 0] != np.inf))[0]

    # if there is a valid node left to explore
    if (len(valid_idx) != 0):
        next_idx = valid_idx[djakstrar_table[valid_idx, 0].argmin()]

        djakstrar_table[next_idx][2] = 1
        pygame.draw.circle(screen, "green", points[next_idx], 1)
        pygame.draw.line(screen, "green", points[next_idx], points[int(djakstrar_table[next_idx, 1])], 1)

        for idx_expand in np.where(graph_table[next_idx])[0]:
            dist = distance(points[next_idx], points[idx_expand]) + djakstrar_table[next_idx, 0] \
                + distance(points[idx_expand], points[end_idx])
            # if is not done and distance is smaller than already there
            if djakstrar_table[idx_expand][2] == 0 \
                and djakstrar_table[idx_expand][0] > dist:
                djakstrar_table[idx_expand] = [dist, next_idx, 0]
                pygame.draw.circle(screen, "yellow", points[idx_expand], 1)
    
            if djakstrar_table[end_idx, 2] == 1:
                traverse_idx = end_idx
                while traverse_idx != start_idx:
                    traverse_idx2 = int(djakstrar_table[traverse_idx, 1])
                    pygame.draw.line(screen, "orange", points[traverse_idx], points[traverse_idx2])
                    traverse_idx = traverse_idx2

    pygame.display.flip()

    clock.tick(1000)  # limits FPS to 60

pygame.quit()