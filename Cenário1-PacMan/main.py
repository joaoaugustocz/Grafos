import pygame
import sys
from collections import deque

# ----------------------------------------------------
# Configurações gerais
# ----------------------------------------------------
WIDTH, HEIGHT = 300, 300      # Tamanho da janela
ROWS, COLS = 10, 10           # Tamanho do grid (20x20)
CELL_SIZE = WIDTH // COLS     # Tamanho de cada célula na tela

# Cores (R, G, B)
WHITE  = (255, 255, 255)
BLACK  = (0,   0,   0)
GRAY   = (80, 80,   80)
RED    = (255, 0,   0)
LIGHT_G = (160, 160, 160)
GREEN  = (0,   255, 0)
BLUE   = (0,   0,   255)
YELLOW = (255, 255, 0)

# tempo

pausaAnimacao = 20

# ----------------------------------------------------
# Exemplo de labirinto (grid):
# 0 -> caminho livre
# 1 -> parede/obstáculo
# Você pode montar seu próprio grid ou gerar aleatoriamente.
# ----------------------------------------------------
maze = [
    [0,0,0,0,1,0,0,0,0,0],
    [0,1,1,0,1,0,1,1,1,0],
    [0,1,0,0,0,0,0,0,1,0],
    [0,0,0,1,1,1,1,0,0,0],
    [0,1,1,1,0,0,0,0,1,0],
    [0,0,0,0,0,1,0,0,0,0],
    [0,1,1,1,0,1,1,1,1,1],
    [0,0,0,0,0,0,0,1,0,0],
    [0,1,1,0,1,1,0,0,0,1],
    [0,0,0,0,0,0,0,1,0,0]
]

# Posição inicial (lin, col) - Ex.: Fantasma Vermelho
start = (0, 0)

# Posição alvo (lin, col) - Ex.: Pac-Man
goal = (9, 9)

# ----------------------------------------------------
# Função para desenhar o grid na tela
# ----------------------------------------------------
def draw_grid(screen, maze, visited, path):
    screen.fill(BLACK)

    for row in range(ROWS):
        for col in range(COLS):
            x = col * CELL_SIZE
            y = row * CELL_SIZE

            # Parede
            if maze[row][col] == 1:
                color = GRAY
            # Caminho visitado (mas não é parede)
            elif (row, col) in visited:
                color = LIGHT_G
            else:
                color = WHITE

            pygame.draw.rect(screen, color, (x, y, CELL_SIZE, CELL_SIZE))

    # Desenha o caminho final em destaque (verde)
    for (r, c) in path:
        x = c * CELL_SIZE
        y = r * CELL_SIZE
        pygame.draw.rect(screen, GREEN, (x, y, CELL_SIZE, CELL_SIZE))

    # Desenha o início (fantasma)
    sx, sy = start[1] * CELL_SIZE, start[0] * CELL_SIZE
    pygame.draw.rect(screen, RED, (sx, sy, CELL_SIZE, CELL_SIZE))

    # Desenha o objetivo (Pac-Man)
    gx, gy = goal[1] * CELL_SIZE, goal[0] * CELL_SIZE
    pygame.draw.rect(screen, YELLOW, (gx, gy, CELL_SIZE, CELL_SIZE))

    pygame.display.update()

# ----------------------------------------------------
# Função para obter vizinhos válidos (4 direções)
# ----------------------------------------------------
def get_neighbors(r, c):
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in directions:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            yield nr, nc

# ----------------------------------------------------
# BFS passo-a-passo para permitir visualização
# ----------------------------------------------------
def bfs_visual(screen, maze, start, goal):
    queue = deque()
    queue.append(start)
    visited = set()
    visited.add(start)
    
    # predecessor: dicionário para reconstruir o caminho
    predecessor = {}
    
    found = False

    while queue:
        current = queue.popleft()
        # Se chegamos ao destino, para a busca
        if current == goal:
            found = True
            break
        
        # Para cada vizinho
        for neighbor in get_neighbors(*current):
            r, c = neighbor
            # Se não for parede e não visitamos ainda
            if maze[r][c] == 0 and neighbor not in visited:
                visited.add(neighbor)
                predecessor[neighbor] = current
                queue.append(neighbor)

        # Desenha o estado atual do BFS
        draw_grid(screen, maze, visited, [])

        # Pequena pausa para ver a animação
        pygame.time.wait(pausaAnimacao)
        
    # Reconstruir o caminho se encontrado
    path = []
    if found:
        node = goal
        while node != start:
            path.append(node)
            node = predecessor[node]
        path.append(start)
        path.reverse()

    return path

# ----------------------------------------------------
# Função principal
# ----------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BFS Visual - Pac-Man Demo")

    # Executa o BFS com visualização
    path = bfs_visual(screen, maze, start, goal)

    # Loop final para exibir o caminho encontrado
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Desenha o grid + caminho final
        draw_grid(screen, maze, set(), path)
        pygame.time.wait(10)

    keys=pygame.key.get_pressed()

    print(keys)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
