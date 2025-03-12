import pygame
import sys
from collections import deque

# ----------------------------------------------------
# Configurações gerais
# ----------------------------------------------------
WIDTH, HEIGHT = 300, 300  # Tamanho da janela
ROWS, COLS = 5, 5         # Tamanho do grid
CELL_SIZE = WIDTH // COLS # Tamanho de cada célula na tela

# Cores (R, G, B)
WHITE      = (240, 240, 240)  # Não visitado
LIGHT_GRAY = (180, 180, 180)  # Descoberto (GRAY no pseudocódigo)
DARK_GRAY  = (50,  50,  50)    # Parede
BLACK      = (0, 0, 0)   # Finalizado
RED        = (255, 0,   0)     # Fantasma (início)
YELLOW     = (255, 255, 0)     # Pac-Man (destino)
GREEN      = (0,   255, 0)     # Caminho final
TEXT_COLOR = (0,   0,   0)     # Cor do texto dentro das células

# Tempo de pausa (ms) para a animação do BFS
ANIMATION_DELAY = 500
# Tempo de pausa (ms) para a animação do caminho final
PATH_DELAY = 300

# ----------------------------------------------------
# Labirinto (grid):
# 0 -> caminho livre
# 1 -> parede/obstáculo
# ----------------------------------------------------
maze = [
    [0,0,0,0,1],
    [0,1,1,1,1],
    [0,1,0,1,1],
    [0,0,0,1,1],
    [1,1,0,0,0],
]

# Início (ex.: Fantasma)
start = (0, 0)
# Destino (ex.: Pac-Man)
goal = (4, 3)

# ----------------------------------------------------
# Mapeamento do estado do BFS -> cor de exibição
# ----------------------------------------------------
color_map = {
    'WHITE': WHITE,      # Não visitado
    'GRAY':  LIGHT_GRAY, # Descoberto
    'BLACK': DARK_GRAY,      # Finalizado
    'WALL':  BLACK,  # Parede
    'PATH':  GREEN       # Caminho final
}

# ----------------------------------------------------
# Converte (row, col) para índice do nó (apenas didático)
# Ex.: linha=2, coluna=3 -> num_nó = 2*COLS + 3
# ----------------------------------------------------
def node_index(r, c):
    return r * COLS + c

# ----------------------------------------------------
# Função para desenhar o grid na tela
#   - Usa as cores de acordo com o dicionário color[]
#   - Desenha também o número do nó dentro do quadrado
#   - Desenha o início (Fantasma) e o fim (Pac-Man) por cima
# ----------------------------------------------------
def draw_grid(screen, color):
    screen.fill(BLACK)
    font = pygame.font.SysFont(None, 17)  # Fonte pequena para texto nos nós

    for row in range(ROWS):
        for col in range(COLS):
            x = col * CELL_SIZE
            y = row * CELL_SIZE

            cell_state = color[(row, col)]
            cell_color = color_map[cell_state]

            # Desenha o retângulo da célula
            pygame.draw.rect(screen, cell_color, (x, y, CELL_SIZE, CELL_SIZE))

            # Escreve o índice do nó no centro da célula
            text_surface = font.render(str(node_index(row, col)), True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2))
            screen.blit(text_surface, text_rect)

    # Desenha o início (fantasma) em vermelho
    sx, sy = start[1] * CELL_SIZE, start[0] * CELL_SIZE
    pygame.draw.rect(screen, RED, (sx, sy, CELL_SIZE, CELL_SIZE))
    s_text = font.render(str(node_index(start[0], start[1])), True, (0,0,0))
    s_rect = s_text.get_rect(center=(sx + CELL_SIZE//2, sy + CELL_SIZE//2))
    screen.blit(s_text, s_rect)

    # Desenha o destino (Pac-Man) em amarelo
    gx, gy = goal[1] * CELL_SIZE, goal[0] * CELL_SIZE
    pygame.draw.rect(screen, YELLOW, (gx, gy, CELL_SIZE, CELL_SIZE))
    g_text = font.render(str(node_index(goal[0], goal[1])), True, (0,0,0))
    g_rect = g_text.get_rect(center=(gx + CELL_SIZE//2, gy + CELL_SIZE//2))
    screen.blit(g_text, g_rect)

    pygame.display.update()

# ----------------------------------------------------
# Retorna os vizinhos válidos (4 direções)
# ----------------------------------------------------
def get_neighbors(r, c):
    direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    for dr, dc in direcoes:
        nr, nc = r + dr, c + dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            yield nr, nc

# ----------------------------------------------------
# BFS passo a passo, colorindo nós conforme pseudocódigo do professor
#   color[u] = WHITE/GRAY/BLACK
#   predecessor[u] para reconstruir caminho
# ----------------------------------------------------
def bfs_visual(screen):
    # Inicialização
    color = {}
    predecessor = {}
    queue = deque()

    # Define cor inicial de cada célula --> branco para caminho lire e Preto para parede
    for r in range(ROWS):
        for c in range(COLS):
            if maze[r][c] == 1:
                color[(r, c)] = 'WALL'   # Parede
            else:
                color[(r, c)] = 'WHITE'  # Não visitado

    # Nó inicial
    color[start] = 'GRAY'
    predecessor[start] = None #o pai do nó inicial n é ninguém
    queue.append(start)

    found = False

    # Loop BFS
    while queue:
        u = queue.popleft() #desempilha (proximo nó a analizar vizinhos)

        # Se u == goal, paramos
        if u == goal:
            found = True
            break

        # Explora vizinhos
        for v in get_neighbors(*u):
            if color[v] == 'WHITE':  # Ainda não descoberto
                color[v] = 'GRAY'
                predecessor[v] = u
                queue.append(v)

        # Terminamos de explorar u(Todos os vizinhos de u foram descobertos)
        color[u] = 'BLACK'

        # Desenha o estado atual do BFS
        draw_grid(screen, color)
        pygame.time.wait(ANIMATION_DELAY)

    # Reconstruir o caminho se encontrado
    path = []
    if found:
        node = goal
        while node is not None:
            path.append(node)
            node = predecessor[node]
        path.reverse()

    return color, path

# ----------------------------------------------------
# Anima o caminho final passo a passo em verde
# ----------------------------------------------------
def animate_path(screen, color, path):
    # Para cada nó no caminho, atualizamos sua cor para 'PATH'
    for node in path:
        color[node] = 'PATH'
        draw_grid(screen, color)
        pygame.time.wait(PATH_DELAY)

# ----------------------------------------------------
# Função principal
# ----------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BFS - Visualização Didática")

    # 1) Executa o BFS com visualização
    color, path = bfs_visual(screen)

    # 2) Anima o caminho final em verde, passo a passo
    if path:
        animate_path(screen, color, path)

    # 3) Mantém a janela aberta até o usuário fechar
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        draw_grid(screen, color)
        pygame.time.wait(50)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
