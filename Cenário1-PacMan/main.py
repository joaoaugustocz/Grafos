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
GREEN      = (60,   200, 60)     # Caminho final
TEXT_COLOR = (0,   0,   0)     # Cor do texto

# ----------------------------------------------------
# Tamanhos
# ----------------------------------------------------
TAM_No = 30
TAM_FonteNo = 40
EspacamentoCamadaNos = 80
EspacamentoEntreNos  = 90
# ----------------------------------------------------
# Labirinto (grid)
# 0 -> livre; 1 -> parede
# ----------------------------------------------------
maze = [
    [0,0,0,0,0],
    [0,1,1,0,1],
    [0,1,0,0,0],
    [0,1,0,1,0],
    [0,1,0,0,0],
]

# bipartido ?
# Grafo simples
# Rotulado
# Não Orientado
# Não Ponderado
# Desconexo



#  0   1   2   3   4
#  5  (X) (X)  8  (X)
# 10  (X) 12  13  14
# 15  (X) 17  (X) 19
# 20  (X) 22  23  24

# Lista de adjacencia:
ListaAdj = {
    0: [1, 5], 
    1: [0, 2], 
    2: [1, 3], 
    3: [2, 8, 4], 
    4: [3],       
    5: [0, 10], 
    6: [],       # (parede)
    7: [],       # (parede)
    8: [3, 13], 
    9: [],       # (parede)
    10: [5, 15], 
    11: [],      # (parede)
    12: [13, 17], 
    13: [8, 12, 14], 
    14: [13, 19], 
    15: [10, 20], 
    16: [],      # (parede)
    17: [12, 22], 
    18: [],      # (parede)
    19: [14, 24], 
    20: [15],
    21: [],      # (parede)
    22: [17, 23], 
    23: [22, 24], 
    24: [19, 23]
}
# MATRIZ DE ADJACENCIA
#  [ 
#      00  01  02  03  04  05  06  07  08  09  10  11  12  13  14  15  16  17  18  19  20  21  22  23  24
# 00  [0,  1,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 01  [1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 02  [0,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 03  [0,  0,  1,  0,  1,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 04  [0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 05  [1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 06  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 07  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 08  [0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 09  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 10  [0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 11  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 12  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0], 
# 13  [0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  1,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 14  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0], 
# 15  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0], 
# 16  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 17  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0], 
# 18  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 19  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1], 
# 20  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 21  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0], 
# 22  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  0,  0,  1,  0], 
# 23  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  1], 
# 24  [0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  0,  1,  0,  0,  0,  1,  0]
#  ]

def criarMatrizAdjacencia(ListaAdj):
    n = len(ListaAdj)
    # Inicializa uma matriz n x n com zeros
    matrix = [[0 for _ in range(n)] for _ in range(n)]
    
    # Para cada nó i, percorre seus vizinhos j
    for i in range(n):
        for j in ListaAdj[i]:
            matrix[i][j] = 1
            matrix[j][i] = 1  # Como o grafo é não direcionado
    
    return matrix
# Cada célula da matriz representa um nó do grafo.
# Uma aresta existe entre dois nós se houver um caminho 
# livre entre eles (isto é, se ambas as células não forem paredes).

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
    # Fundo do grid
    pygame.draw.rect(screen, BLACK, (0, 0, GRID_WIDTH, HEIGHT))
    font = pygame.font.SysFont(None, 17) # Fonte pequena para texto nos nós
    
    for r in range(ROWS):
        for c in range(COLS):
            x = c * CELL_SIZE
            y = r * CELL_SIZE
            cell_state = color[(r, c)]
            cell_color = color_map[cell_state]
            
            # Desenha o retângulo da célula
            pygame.draw.rect(screen, cell_color, (x, y, CELL_SIZE, CELL_SIZE))
            
            # Escreve o índice do nó no centro da célula
            text_surface = font.render(str(node_index(r, c)), True, TEXT_COLOR)
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

# ----------------------------------------------------
# Desenha uma linha com setinha
# ----------------------------------------------------
import math
def draw_arrow(screen, start_pos, end_pos, color=(0,0,0), thickness=2, node_radius=TAM_No):
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
    
    font = pygame.font.SysFont(None, TAM_FonteNo)
    
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
    layer_spacing = EspacamentoCamadaNos
    # Espaçamento horizontal entre nós na mesma camada
    node_spacing = EspacamentoEntreNos
    
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
            pygame.draw.circle(screen, (0,0,255), (x, y), TAM_No)
            
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
    
    font = pygame.font.SysFont(None, TAM_FonteNo)
    
    # Agrupa nós por distância
    layers = {}
    for node, d in dist.items():
        if d is not None:
            layers.setdefault(d, []).append(node)
    
    max_dist = max(d for d in dist.values() if d is not None) if dist else 0
    layer_spacing = EspacamentoCamadaNos
    node_spacing  = EspacamentoEntreNos
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
            pygame.draw.circle(screen, (0,0,255), (x, y), TAM_No)
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
            draw_arrow(screen, start_pos, end_pos, color=(0,0,0), thickness=2, node_radius=TAM_No)

# ----------------------------------------------------
# Retorna os vizinhos válidos (4 direções)
# ----------------------------------------------------
def get_neighbors(r, c):
    direcoes = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # Lista de movimentos: cima, baixo, esquerda e direita
    for dr, dc in direcoes:                        # Itera sobre cada direção
        nr, nc = r + dr, c + dc                     # Calcula a nova linha (nr) e nova coluna (nc) para o vizinho
        if 0 <= nr < ROWS and 0 <= nc < COLS:        # Verifica se as coordenadas estão dentro dos limites do grid
            yield nr, nc                           # Se estiverem, retorna (gera) esse vizinho
            # o yield é bom pra economizar memoria

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
    # Inicialização
    color = {}
    predecessor = {}
    queue = deque()
    dist        = {}  # armazena distância do start
    
    # Define cor inicial de cada célula --> branco para caminho livre e preto para parede
    for r in range(ROWS):
        for c in range(COLS):
            if maze[r][c] == 1:
                color[(r, c)] = 'WALL'   # Parede
            else:
                color[(r, c)] = 'WHITE'  # Não visitado
            dist[(r,c)]  = None

    
    
    # Nó inicial
    color[start] = 'GRAY'
    predecessor[start] = None  # o pai do nó inicial não é ninguém
    dist[start] = 0
    queue.append(start)
    
    found = False
    
    # Loop BFS
    while queue:
        u = queue.popleft()  # desempilha (próximo nó a analisar vizinhos)
        
        # Se chegamos no goal
        if u == goal:
            found = True
            # (não necessariamente paramos BFS aqui se quiser visitar todos)
            break
        
        # Explora vizinhos
        for v in get_neighbors(*u):
            if color[v] == 'WHITE':  # Ainda não descoberto
                color[v] = 'GRAY'
                predecessor[v] = u
                dist[v] = dist[u] + 1 if dist[u] is not None else 0
                queue.append(v)
        
        # Terminamos de explorar u (todos os vizinhos de u foram descobertos)
        color[u] = 'BLACK'
        
        # Desenha a cada passo e espera a tecla
        draw_grid(screen, color)
        draw_tree_with_positions(screen, predecessor, dist)
        pygame.display.update()
        wait_for_right_key()  # Aguardar seta → para avançar
    

    # Reconstruir o caminho se encontrado
    path = []                           # Cria uma lista vazia para armazenar o caminho encontrado
    if found:                           # Se o objetivo (goal) foi alcançado no BFS
        node = goal                     # Inicia a reconstrução a partir do nó de destino (goal)
        while node is not None:         # Enquanto houver um nó (até chegar ao início, onde predecessor é None)
            path.append(node)           # Adiciona o nó atual à lista do caminho
            node = predecessor[node]    # Atualiza o nó atual para o seu predecessor (nó anterior no caminho)
    path.reverse()                      # Inverte a lista, para que o caminho fique na ordem correta: do início (start) ao destino (goal)


    
    return color, path, predecessor, dist

# ----------------------------------------------------
# Anima o caminho final no grid (aguardando seta)
# ----------------------------------------------------
def animate_path(screen, color, path, predecessor, dist):
    # Para cada nó no caminho, atualizamos sua cor para 'PATH' e aguardamos a tecla
    for node in path:
        color[node] = 'PATH'
        draw_grid(screen, color)
        #draw_tree_with_positions(screen, predecessor, dist)
        pygame.display.update()
        wait_for_right_key()

def inverter_setas_verdes(screen, predecessor, dist, green_nodes):
    """
    Redesenha a área do grafo invertendo o sentido das setas somente
    para as arestas cujos dois nós (o nó e seu predecessor) pertencem ao caminho verde.
    As demais arestas permanecem na orientação normal.
    """
    tree_area = pygame.Rect(GRID_WIDTH, 0, TREE_WIDTH, HEIGHT)
    pygame.draw.rect(screen, (220,220,220), tree_area)
    
    font = pygame.font.SysFont(None, TAM_FonteNo)
    layers = {}
    for node, d in dist.items():
        if d is not None:
            layers.setdefault(d, []).append(node)
    
    max_dist = max(d for d in dist.values() if d is not None) if dist else 0
    layer_spacing = EspacamentoCamadaNos
    node_spacing  = EspacamentoEntreNos
    center_x = GRID_WIDTH + TREE_WIDTH // 2
    positions = {}
    
    # Recalcula as posições de cada nó na árvore
    for d in range(max_dist+1):
        if d not in layers:
            continue
        layer_nodes = layers[d]
        y = 30 + d * layer_spacing
        k = len(layer_nodes)
        start_x = center_x - (k-1) * node_spacing // 2
        for i, node in enumerate(layer_nodes):
            x = start_x + i * node_spacing
            positions[node] = (x, y)
            # Desenha o nó: se faz parte do caminho verde, pinta de verde; senão, azul.
            node_color = GREEN if node in green_nodes else (0,0,255)
            pygame.draw.circle(screen, node_color, (x, y), TAM_No)
            idx = node_index(*node)
            text_surface = font.render(str(idx), True, (255,255,255))
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)
    
    # Desenha as setas: inverte a direção somente se ambos os nós estão no caminho verde.
    for node, pred in predecessor.items():
        if pred is None:
            continue
        if node in positions and pred in positions:
            if node in green_nodes and pred in green_nodes:
                # Inverte a seta: desenha de (posição do nó) para (posição do predecessor)
                draw_arrow(screen, positions[pred], positions[node], color=GREEN, thickness=2, node_radius=TAM_No)
            else:
                # Desenha normalmente: de predecessor para o nó
                draw_arrow(screen, positions[node], positions[pred], color=(0,0,0), thickness=2, node_radius=TAM_No)
    
    pygame.display.update()



def animate_tree_path_reverse(screen, predecessor, dist, path):
    """
    Anima a área do grafo (lado direito) pintando os nós do menor caminho de verde,
    mas de forma invertida, ou seja, partindo do Pac-Man (goal) até o Fantasma (start).
    A cada pressionamento da tecla seta para a direita, um nó a mais (na ordem reversa)
    é pintado de verde na visualização.
    """
    # Conjunto para armazenar os nós que já foram animados (pintados de verde)
    green_nodes = set()
    
    # Percorre o caminho em ordem reversa (do goal para o start)
    for node in reversed(path):
        green_nodes.add(node)
        
        # Re-desenha a área do grafo com os nós atualizados:
        # Utiliza a mesma lógica de draw_tree_with_positions, mas se o nó estiver no conjunto green_nodes,
        # ele será desenhado com a cor GREEN; caso contrário, com a cor azul (0, 0, 255).
        tree_area = pygame.Rect(GRID_WIDTH, 0, TREE_WIDTH, HEIGHT)
        pygame.draw.rect(screen, (220, 220, 220), tree_area)
    
        font = pygame.font.SysFont(None, TAM_FonteNo)
    
        # Agrupa os nós por distância (camadas)
        layers = {}
        for node_key, d in dist.items():
            if d is not None:
                layers.setdefault(d, []).append(node_key)
    
        max_dist = max(d for d in dist.values() if d is not None) if dist else 0
        layer_spacing = EspacamentoCamadaNos
        node_spacing  = EspacamentoEntreNos
        center_x      = GRID_WIDTH + TREE_WIDTH // 2
    
        positions = {}
    
        # Desenha cada camada de nós
        for d in range(max_dist + 1):
            if d not in layers:
                continue
            layer_nodes = layers[d]
            y = 30 + d * layer_spacing
            k = len(layer_nodes)
            start_x = center_x - (k - 1) * node_spacing // 2
            for i, node_key in enumerate(layer_nodes):
                x = start_x + i * node_spacing
                positions[node_key] = (x, y)
                # Se o nó estiver no conjunto green_nodes, ele é desenhado em verde; caso contrário, em azul.
                node_color = GREEN if node_key in green_nodes else (0, 0, 255)
                pygame.draw.circle(screen, node_color, (x, y), TAM_No)
                idx = node_index(*node_key)
                text_surface = font.render(str(idx), True, (255, 255, 255))
                text_rect = text_surface.get_rect(center=(x, y))
                screen.blit(text_surface, text_rect)
    
        # Desenha as setas (arestas) entre os nós conforme os predecessores
        for node_key, pred in predecessor.items():
            if pred is None:
                continue
            if node_key in positions and pred in positions:
                # Se tanto o nó quanto seu predecessor estão no caminho animado (green_nodes), a seta fica verde;
                # caso contrário, permanece preta.
                arrow_color = GREEN if (node_key in green_nodes and pred in green_nodes) else (0, 0, 0)
                start_pos = positions[pred]
                end_pos = positions[node_key]
                draw_arrow(screen, end_pos, start_pos, color=arrow_color, thickness=2, node_radius=TAM_No)
    
        pygame.display.update()
        wait_for_right_key()  # Aguarda o pressionamento da seta para avançar o próximo passo

   # Ao final, inverte o sentido das setas apenas para as arestas que conectam nós do caminho verde
    inverter_setas_verdes(screen, predecessor, dist, green_nodes)
    wait_for_right_key()
# ----------------------------------------------------
# Main
# ----------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("BFS com Visualização de Árvore em Camadas")
    
    # 1) Executa o BFS com visualização
    color, path, predecessor, dist = bfs_visual(screen)
    
    # 2) Anima o caminho final em verde, passo a passo com a tecla seta para a direita
    if path:
        animate_tree_path_reverse(screen, predecessor, dist, path)
        animate_path(screen, color, path, predecessor, dist)
    
    # 3) Mantém a janela aberta até o usuário fechar
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        draw_grid(screen, color)
        pygame.display.update()
        pygame.time.wait(50)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()


