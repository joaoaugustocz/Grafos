#!/usr/bin/env python3
import pygame
import sys
import math

# ----------------------------------------------------
# Configurações da Janela e Parâmetros Visuais
# ----------------------------------------------------
WIDTH, HEIGHT = 900, 700        # Dimensões da janela
TREE_WIDTH = WIDTH              # Utilizamos toda a janela para a árvore

TAM_No = 30                     # Tamanho dos nós (círculos)
TAM_FonteNo = 40                # Tamanho da fonte dos rótulos
EspacamentoCamadaNos = 80       # Espaçamento vertical entre camadas
EspacamentoEntreNos  = 90       # Espaçamento horizontal entre nós

# ----------------------------------------------------
# Cores
# ----------------------------------------------------
WHITE      = (240, 240, 240)    # Estado "não visitado"
LIGHT_GRAY = (180, 180, 180)    # Estado "descoberto"
DARK_GRAY  = (50, 50, 50)       # Estado "finalizado"
BLACK      = (0, 0, 0)
RED        = (255, 0, 0)       # Nó instalado (destacado na animação final)
GREEN      = (60, 200, 60)
TEXT_COLOR = (0, 0, 0)

# Mapeamento dos estados para cores na visualização
color_map = {
    'WHITE': WHITE,      # Não visitado
    'GRAY':  LIGHT_GRAY, # Em recursão/descoberto
    'BLACK': DARK_GRAY   # Finalizado
}

# ----------------------------------------------------
# Grafo Dirigido Acíclico (DAG) representando as dependências
# Cada nó é uma biblioteca (letra) e uma aresta (u -> v) indica que para instalar u,
# é necessário instalar v primeiro.
# ----------------------------------------------------
graph = {
    "A": ["B", "C"],
    "B": ["D"],
    "C": ["D", "E"],
    "D": ["F"],
    "E": ["F"],
    "F": []
}

# ----------------------------------------------------
# Função utilitária: Desenha uma seta entre dois pontos
# ----------------------------------------------------
def draw_arrow(screen, start_pos, end_pos, color=(0, 0, 0), thickness=2, node_radius=TAM_No):
    x1, y1 = start_pos
    x2, y2 = end_pos
    dx = x2 - x1
    dy = y2 - y1
    dist = math.hypot(dx, dy)
    if dist < 2 * node_radius:
        return
    ux = dx / dist
    uy = dy / dist
    new_start = (x1 + node_radius * ux, y1 + node_radius * uy)
    new_end   = (x2 - node_radius * ux, y2 - node_radius * uy)
    pygame.draw.line(screen, color, new_start, new_end, thickness)
    
    # Desenha a ponta da seta
    arrow_tip = new_end
    arrow_len = 10
    arrow_angle = math.pi / 6
    angle = math.atan2(y2 - y1, x2 - x1)
    left_x = arrow_tip[0] - arrow_len * math.cos(angle - arrow_angle)
    left_y = arrow_tip[1] - arrow_len * math.sin(angle - arrow_angle)
    right_x = arrow_tip[0] - arrow_len * math.cos(angle + arrow_angle)
    right_y = arrow_tip[1] - arrow_len * math.sin(angle + arrow_angle)
    pygame.draw.polygon(screen, color, [
        arrow_tip,
        (left_x, left_y),
        (right_x, right_y)
    ])

# ----------------------------------------------------
# Função de espera: prossegue quando a tecla seta → é pressionada
# ----------------------------------------------------
def wait_for_right_key():
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                waiting = False

# ----------------------------------------------------
# Função para desenhar a árvore de DFS
# Distribui os nós por camadas de acordo com a "profundidade" (depth),
# desenha as arestas conforme os predecessores e exibe a ordem parcial.
# ----------------------------------------------------
def draw_tree_dfs(screen, predecessor, depth, visited, topo_order):
    screen.fill((220, 220, 220))  # Fundo da área
    font = pygame.font.SysFont(None, TAM_FonteNo)
    
    # Agrupar nós por profundidade
    layers = {}
    for node, d in depth.items():
        if d is not None:
            layers.setdefault(d, []).append(node)
    max_depth = max(layers.keys()) if layers else 0
    layer_spacing = EspacamentoCamadaNos
    node_spacing = EspacamentoEntreNos
    center_x = TREE_WIDTH // 2
    positions = {}
    
    # Desenha os nós distribuídos por camadas
    for d, nodes in layers.items():
        y = 30 + d * layer_spacing
        k = len(nodes)
        start_x = center_x - (k - 1) * node_spacing // 2
        for i, node in enumerate(nodes):
            x = start_x + i * node_spacing
            positions[node] = (x, y)
            node_color = color_map.get(visited[node], WHITE)
            pygame.draw.circle(screen, node_color, (x, y), TAM_No)
            text_surface = font.render(node, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)
    
    # Desenha as arestas baseado no predecessor
    for node, pred in predecessor.items():
        if pred is not None and node in positions and pred in positions:
            draw_arrow(screen, positions[pred], positions[node], color=(0, 0, 0), thickness=2, node_radius=TAM_No)
    
    # Exibe a ordem parcial obtida
    order_text = "Ordem Topológica (postorder parcial): " + " -> ".join(str(n) for n in topo_order)
    order_surface = font.render(order_text, True, BLACK)
    screen.blit(order_surface, (20, HEIGHT - 100))
    
    pygame.display.update()

# ----------------------------------------------------
# Função DFS recursiva para ordenação topológica com visualização
# Atualiza os estados dos nós (visited: 'WHITE' -> 'GRAY' -> 'BLACK'), registra
# os predecessores e profundidade, e adiciona o nó à lista topo_order após o processamento.
# Em cada mudança de estado, atualiza a exibição e aguarda a tecla seta →.
# Utiliza a ordem alfabética na iteração dos vizinhos.
# ----------------------------------------------------
def dfs(u, visited, topo_order, depth, predecessor, screen):
    visited[u] = 'GRAY'
    draw_tree_dfs(screen, predecessor, depth, visited, topo_order)
    wait_for_right_key()
    
    for v in sorted(graph[u]):  # Usa ordem alfabética
        if visited[v] == 'WHITE':
            predecessor[v] = u
            depth[v] = depth[u] + 1
            dfs(v, visited, topo_order, depth, predecessor, screen)
    
    visited[u] = 'BLACK'
    topo_order.append(u)
    draw_tree_dfs(screen, predecessor, depth, visited, topo_order)
    wait_for_right_key()

# ----------------------------------------------------
# Executa DFS a partir da biblioteca escolhida e, em seguida,
# para nós que não foram visitados, em ordem alfabética.
# Gera e inverte a lista topo_order para a ordem topológica correta.
# ----------------------------------------------------
def dfs_topo_visual(screen, start_lib):
    visited = {}
    depth = {}
    predecessor = {}
    topo_order = []
    
    for node in graph.keys():
        visited[node] = 'WHITE'
        depth[node] = None
        predecessor[node] = None
    
    # Inicia a DFS na biblioteca escolhida, se válida
    if start_lib in graph:
        depth[start_lib] = 0
        dfs(start_lib, visited, topo_order, depth, predecessor, screen)
    
    # Para garantir que todos os nós sejam processados (caso o grafo seja desconexo)
    for node in sorted(graph.keys()):
        if visited[node] == 'WHITE':
            depth[node] = 0
            dfs(node, visited, topo_order, depth, predecessor, screen)
    
    topo_order.reverse()  # Inverte para obter a ordem correta de instalação
    draw_tree_dfs(screen, predecessor, depth, visited, topo_order)
    wait_for_right_key()
    return visited, topo_order, predecessor, depth

# ----------------------------------------------------
# Anima o processo de "instalação" das bibliotecas conforme a ordem topológica.
# A cada pressionamento da seta →, um nó é destacado (pintado de RED)
# para indicar que a biblioteca foi instalada.
# ----------------------------------------------------
def animate_installation(screen, topo_order):
    font = pygame.font.SysFont(None, TAM_FonteNo)
    installed = []
    
    for node in topo_order:
        installed.append(node)
        screen.fill((220, 220, 220))
        
        # Define as cores: os nós instalados ficam RED, os demais DARK_GRAY
        aux_visited = {}
        for n in graph.keys():
            if n in installed:
                aux_visited[n] = RED
            else:
                aux_visited[n] = DARK_GRAY
        draw_tree_dfs(screen, {}, {n: 0 for n in graph.keys()}, aux_visited, topo_order)
        order_text = "Instalação: " + " -> ".join(str(n) for n in installed)
        order_surface = font.render(order_text, True, BLACK)
        screen.blit(order_surface, (20, HEIGHT - 50))
        pygame.display.update()
        wait_for_right_key()

# ----------------------------------------------------
# Função principal: inicializa o Pygame, permite escolher a biblioteca inicial,
# executa a DFS com visualização e anima a instalação.
# ----------------------------------------------------
def main():
    # Permite escolher a biblioteca inicial via input
    start_lib = input("Digite a biblioteca inicial (ex: A): ").strip().upper()
    if start_lib not in graph:
        print("Biblioteca inválida. Iniciando com A por padrão.")
        start_lib = "A"
    
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ordenação Topológica via DFS (Visualização)")
    
    visited, topo_order, predecessor, depth = dfs_topo_visual(screen, start_lib)
    animate_installation(screen, topo_order)
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        pygame.time.wait(50)
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

