import pygame
import sys
from collections import deque

# ----------------------------------------------------
# Configurações da Janela
# ----------------------------------------------------
WIDTH, HEIGHT = 900, 900   # Janela 600×300
GRID_WIDTH = 300           # Largura da área do grid (esquerda)
TREE_WIDTH = WIDTH - GRID_WIDTH  # 300px para a árvore (direita)

ROWS, COLS = 5, 5
CELL_SIZE = GRID_WIDTH // COLS

# ----------------------------------------------------
# Cores
# ----------------------------------------------------
WHITE      = (240, 240, 240)  # Não visitado
LIGHT_GRAY = (180, 180, 180)  # Descoberto
DARK_GRAY  = (50,  50,  50)    # Parede ou finalizado
BLACK      = (0, 0, 0)         # Fundo e/ou estado de parede
RED        = (255, 0,   0)     # Fantasma (start)
YELLOW     = (255, 255, 0)     # Pac-Man (goal)
GREEN      = (0,   255, 0)     # Caminho final
TEXT_COLOR = (0,   0,   0)     # Cor do texto

# ----------------------------------------------------
# Labirinto (grid)
# 0 -> livre; 1 -> parede
# ----------------------------------------------------
maze = [
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
    [0,0,0,0,0],
]

start = (0, 0)
goal  = (4, 4)

# ----------------------------------------------------
# Mapeamento de estado (grid) -> cor
# ----------------------------------------------------
color_map = {
    'WHITE': WHITE,      # não visitado
    'GRAY':  LIGHT_GRAY, # descoberto
    'BLACK': DARK_GRAY,  # finalizado
    'WALL':  BLACK,      # parede
    'PATH':  GREEN       # caminho final
}

# ----------------------------------------------------
# Função para obter índice do nó (didático)
# ----------------------------------------------------
def node_index(r, c):
    return r * COLS + c

# ----------------------------------------------------
# Desenha o grid (lado esquerdo)
# ----------------------------------------------------
def draw_grid(screen, color):
    # Fundo do grid
    pygame.draw.rect(screen, BLACK, (0, 0, GRID_WIDTH, HEIGHT))
    font = pygame.font.SysFont(None, 17)
    
    for r in range(ROWS):
        for c in range(COLS):
            x = c * CELL_SIZE
            y = r * CELL_SIZE
            cell_state = color[(r, c)]
            cell_color = color_map[cell_state]
            
            pygame.draw.rect(screen, cell_color, (x, y, CELL_SIZE, CELL_SIZE))
            
            # Índice do nó
            text_surface = font.render(str(node_index(r, c)), True, TEXT_COLOR)
            text_rect = text_surface.get_rect(center=(x + CELL_SIZE//2, y + CELL_SIZE//2))
            screen.blit(text_surface, text_rect)
    
    # Redesenha start (fantasma) em vermelho
    sx, sy = start[1] * CELL_SIZE, start[0] * CELL_SIZE
    pygame.draw.rect(screen, RED, (sx, sy, CELL_SIZE, CELL_SIZE))
    s_text = font.render(str(node_index(start[0], start[1])), True, (0,0,0))
    s_rect = s_text.get_rect(center=(sx + CELL_SIZE//2, sy + CELL_SIZE//2))
    screen.blit(s_text, s_rect)
    
    # Redesenha goal (Pac-Man) em amarelo
    gx, gy = goal[1] * CELL_SIZE, goal[0] * CELL_SIZE
    pygame.draw.rect(screen, YELLOW, (gx, gy, CELL_SIZE, CELL_SIZE))
    g_text = font.render(str(node_index(goal[0], goal[1])), True, (0,0,0))
    g_rect = g_text.get_rect(center=(gx + CELL_SIZE//2, gy + CELL_SIZE//2))
    screen.blit(g_text, g_rect)

# ----------------------------------------------------
# Desenha uma linha com setinha
# ----------------------------------------------------
import math
def draw_arrow(screen, start_pos, end_pos, color=(0,0,0), thickness=2, node_radius=15):
    """
    Desenha uma seta de start_pos para end_pos,
    encurtando o início e o fim para não sobrepor os círculos dos nós.
    """
    # Descompacta coordenadas
    x1, y1 = start_pos
    x2, y2 = end_pos

    # Vetor direção (dx, dy)
    dx = x2 - x1
    dy = y2 - y1

    # Distância entre start e end
    dist = math.hypot(dx, dy)

    # Se dist for muito pequeno, evita divisão por zero
    if dist < 2 * node_radius:
        return  # Nós muito próximos ou sobrepostos, não desenha a seta

    # Normaliza (dx, dy) para obter direção unitária
    ux = dx / dist
    uy = dy / dist

    # "Encurtar" no início e no fim do vetor
    # Início: avança node_radius pixels a partir de start
    # Fim: recua node_radius pixels antes de end
    new_start = (x1 + node_radius * ux, y1 + node_radius * uy)
    new_end   = (x2 - node_radius * ux, y2 - node_radius * uy)

    # Desenha a linha principal
    pygame.draw.line(screen, color, new_start, new_end, thickness)

    # Para desenhar a ponta da seta, calculamos novamente
    # o ponto final "real" da linha (onde começa a flecha):
    arrow_tip = new_end
    # Tamanho da setinha
    arrow_len = 10
    arrow_angle = math.pi / 6  # ~30 graus

    # Ângulo da linha
    angle = math.atan2(y2 - y1, x2 - x1)
    # Ponta esquerda
    left_x = arrow_tip[0] - arrow_len * math.cos(angle - arrow_angle)
    left_y = arrow_tip[1] - arrow_len * math.sin(angle - arrow_angle)
    # Ponta direita
    right_x = arrow_tip[0] - arrow_len * math.cos(angle + arrow_angle)
    right_y = arrow_tip[1] - arrow_len * math.sin(angle + arrow_angle)

    # Desenha o triângulo da seta
    pygame.draw.polygon(screen, color, [
        arrow_tip,
        (left_x, left_y),
        (right_x, right_y)
    ])

# ----------------------------------------------------
# Desenha a "árvore" do BFS no lado direito,
# colocando nós em camadas conforme a distância do start
# ----------------------------------------------------
def draw_tree(screen, predecessor, dist):
    # Fundo da área da árvore (lado direito)
    tree_area = pygame.Rect(GRID_WIDTH, 0, TREE_WIDTH, HEIGHT)
    pygame.draw.rect(screen, (220, 220, 220), tree_area)
    
    font = pygame.font.SysFont(None, 17)
    
    # Agrupa nós por distância
    layers = {}  # dict: distance -> [nós]
    for node, d in dist.items():
        if d is not None:
            layers.setdefault(d, []).append(node)
    
    # Para desenhar cada camada (linha) top-down
    # dist=0 no topo, dist=1 abaixo, etc.
    # Calcula quantas camadas temos
    max_dist = max(d for d in dist.values() if d is not None) if dist else 0
    
    # Espaçamento vertical entre camadas
    layer_spacing = 50
    # Espaçamento horizontal entre nós na mesma camada
    node_spacing = 60
    
    for d in range(max_dist+1):
        if d not in layers:
            continue
        layer_nodes = layers[d]
        # y fixo para essa camada
        y = 30 + d * layer_spacing
        # Se a camada tem k nós, distribuímos horizontalmente
        k = len(layer_nodes)
        # Centro do lado direito
        center_x = GRID_WIDTH + TREE_WIDTH // 2
        # Ponto inicial para o primeiro nó (para centralizar a linha)
        start_x = center_x - (k-1) * node_spacing // 2
        
        for i, node in enumerate(layer_nodes):
            x = start_x + i * node_spacing
            # Desenha o nó como um círculo
            pygame.draw.circle(screen, (0,0,255), (x, y), 15)
            
            # Índice do nó
            idx = node_index(*node)
            text_surface = font.render(str(idx), True, (255,255,255))
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)
    
    # Desenha as setas (de predecessor para nó)
    for node, pred in predecessor.items():
        if pred is None:  # sem predecessor (nó inicial)
            continue
        # dist do node e do pred
        d_node = dist[node]
        d_pred = dist[pred]
        if d_node is None or d_pred is None:
            continue
        
        # Descobre onde cada um foi desenhado
        # y = 30 + d*layer_spacing
        # x = start_x + i*node_spacing (onde i é a posição do node na camada)
        
        # Para achar as posições, precisamos refazer o cálculo
        # ou criar um dicionário de posições ao desenhar as camadas.
        # Vamos criar esse dicionário agora para não repetir lógica:
    
def draw_tree_with_positions(screen, predecessor, dist):
    """Versão que salva posições (x,y) dos nós para desenhar as arestas."""
    tree_area = pygame.Rect(GRID_WIDTH, 0, TREE_WIDTH, HEIGHT)
    pygame.draw.rect(screen, (220, 220, 220), tree_area)
    
    font = pygame.font.SysFont(None, 17)
    
    # Agrupa nós por distância
    layers = {}
    for node, d in dist.items():
        if d is not None:
            layers.setdefault(d, []).append(node)
    
    max_dist = max(d for d in dist.values() if d is not None) if dist else 0
    layer_spacing = 50
    node_spacing  = 60
    center_x      = GRID_WIDTH + TREE_WIDTH // 2
    
    # Dicionário que guardará a posição de cada nó
    positions = {}
    
    # Desenha camadas e nós
    for d in range(max_dist+1):
        if d not in layers:
            continue
        layer_nodes = layers[d]
        y = 30 + d * layer_spacing
        k = len(layer_nodes)
        start_x = center_x - (k-1)*node_spacing//2
        
        for i, node in enumerate(layer_nodes):
            x = start_x + i*node_spacing
            # Armazena posição
            positions[node] = (x, y)
            # Desenha círculo
            pygame.draw.circle(screen, (0,0,255), (x, y), 15)
            # Desenha índice
            idx = node_index(*node)
            text_surface = font.render(str(idx), True, (255,255,255))
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)
    
    # Desenha arestas (setas)
    for node, pred in predecessor.items():
        if pred is None:
            continue
        if node in positions and pred in positions:
            start_pos = positions[node]
            end_pos   = positions[pred]
            draw_arrow(screen, start_pos, end_pos, color=(0,0,0), thickness=2, node_radius=15)

# ----------------------------------------------------
# Retorna vizinhos (4 direções)
# ----------------------------------------------------
def get_neighbors(r, c):
    direcoes = [(-1,0), (1,0), (0,-1), (0,1)]
    for dr, dc in direcoes:
        nr, nc = r+dr, c+dc
        if 0 <= nr < ROWS and 0 <= nc < COLS:
            yield nr, nc

# ----------------------------------------------------
# Espera a tecla seta para a direita
# ----------------------------------------------------
def wait_for_right_key():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    waiting = False

# ----------------------------------------------------
# BFS passo a passo (aguardando seta), e guarda distâncias
# ----------------------------------------------------
def bfs_visual(screen):
    color       = {}
    predecessor = {}
    dist        = {}  # armazena distância do start
    
    # Inicializa
    for r in range(ROWS):
        for c in range(COLS):
            if maze[r][c] == 1:
                color[(r,c)] = 'WALL'
                dist[(r,c)]  = None
            else:
                color[(r,c)] = 'WHITE'
                dist[(r,c)]  = None
    
    queue = deque()
    color[start] = 'GRAY'
    predecessor[start] = None
    dist[start] = 0
    queue.append(start)
    
    found = False
    
    while queue:
        u = queue.popleft()
        
        # Se chegamos no goal
        if u == goal:
            found = True
            # (não necessariamente paramos BFS aqui se quiser visitar todos)
            break
        
        # Explora vizinhos
        for v in get_neighbors(*u):
            if color[v] == 'WHITE':
                color[v] = 'GRAY'
                predecessor[v] = u
                dist[v] = dist[u] + 1 if dist[u] is not None else 0
                queue.append(v)
        
        # Finaliza u
        color[u] = 'BLACK'
        
        # Desenha a cada passo e espera tecla
        draw_grid(screen, color)
        draw_tree_with_positions(screen, predecessor, dist)
        pygame.display.update()
        wait_for_right_key()  # Aguardar seta → para avançar
    
    # Reconstruir caminho, se encontrado
    path = []
    if found:
        node = goal
        while node is not None:
            path.append(node)
            node = predecessor[node]
        path.reverse()
    
    return color, path, predecessor, dist

# ----------------------------------------------------
# Anima o caminho final no grid (aguardando seta)
# ----------------------------------------------------
def animate_path(screen, color, path, predecessor, dist):
    for node in path:
        color[node] = 'PATH'
        draw_grid(screen, color)
        draw_tree_with_positions(screen, predecessor, dist)
        pygame.display.update()
        wait_for_right_key()

# ----------------------------------------------------
# Main
# ----------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BFS com Visualização de Árvore em Camadas")
    
    color, path, predecessor, dist = bfs_visual(screen)
    
    # Anima o caminho final
    if path:
        animate_path(screen, color, path, predecessor, dist)
    
    # Loop final
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        draw_grid(screen, color)
        draw_tree_with_positions(screen, predecessor, dist)
        pygame.display.update()
        pygame.time.wait(50)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
