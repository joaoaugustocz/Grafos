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
TAM_FonteNo = 40                # Tamanho da fonte dos números
EspacamentoCamadaNos = 80       # Espaçamento vertical entre camadas
EspacamentoEntreNos  = 90       # Espaçamento horizontal entre nós

# ----------------------------------------------------
# Cores
# ----------------------------------------------------
WHITE      = (240, 240, 240)    # Estado "não visitado"
LIGHT_GRAY = (180, 180, 180)    # Estado "descoberto" (em recursão)
DARK_GRAY  = (50, 50, 50)       # Estado "finalizado"
BLACK      = (0, 0, 0)
RED        = (255, 0, 0)       # Nó instalado (destacado na animação final)
GREEN      = (60, 200, 60)
TEXT_COLOR = (0, 0, 0)

# Mapeamento dos estados para cores na visualização
color_map = {
    'WHITE': WHITE,   # Não visitado
    'GRAY':  LIGHT_GRAY,  # Descoberto
    'BLACK': DARK_GRAY    # Finalizado
}

# ----------------------------------------------------
# Grafo Dirigido Acíclico (DAG) representando as dependências
# Cada nó é uma biblioteca; uma aresta (u -> v) significa que para instalar u,
# deve-se instalar v primeiro.
# ----------------------------------------------------
graph = {
    0: [1, 2],
    1: [3],
    2: [3, 4],
    3: [5],
    4: [5],
    5: []
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
# Exibe os nós distribuídos por "profundidade" (depth),
# desenha as arestas conforme os predecessores e mostra a ordem parcial.
# ----------------------------------------------------
def draw_tree_dfs(screen, predecessor, depth, visited, topo_order):
    screen.fill((220, 220, 220))  # Fundo da área
    font = pygame.font.SysFont(None, TAM_FonteNo)
    
    # Agrupar nós conforme a profundidade
    layers = {}
    for node, d in depth.items():
        if d is not None:
            layers.setdefault(d, []).append(node)
    max_depth = max(layers.keys()) if layers else 0
    layer_spacing = EspacamentoCamadaNos
    node_spacing = EspacamentoEntreNos
    center_x = TREE_WIDTH // 2
    positions = {}
    
    # Desenha os nós conforme as camadas
    for d, nodes in layers.items():
        y = 30 + d * layer_spacing
        k = len(nodes)
        start_x = center_x - (k - 1) * node_spacing // 2
        for i, node in enumerate(nodes):
            x = start_x + i * node_spacing
            positions[node] = (x, y)
            # Escolhe a cor conforme o estado de visita
            node_color = color_map.get(visited[node], WHITE)
            pygame.draw.circle(screen, node_color, (x, y), TAM_No)
            text_surface = font.render(str(node), True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(x, y))
            screen.blit(text_surface, text_rect)
    
    # Desenha as arestas baseadas no predecessor
    for node, pred in predecessor.items():
        if pred is not None and node in positions and pred in positions:
            draw_arrow(screen, positions[pred], positions[node], color=(0, 0, 0), thickness=2, node_radius=TAM_No)
    
    # Exibe a ordem parcial obtida (lista topo_order)
    order_text = "Ordem Topológica (postorder parcial): " + " -> ".join(str(n) for n in topo_order)
    order_surface = font.render(order_text, True, BLACK)
    screen.blit(order_surface, (20, HEIGHT - 100))
    
    pygame.display.update()

# ----------------------------------------------------
# Função DFS recursiva para ordenação topológica com visualização
# - Atualiza o estado do nó (visited: 'WHITE' -> 'GRAY' -> 'BLACK')
# - Registra o predecessor e a profundidade para a visualização
# - Adiciona o nó à lista topo_order após processamento (em pós-ordem)
# Cada mudança de estado atualiza a exibição e aguarda a tecla seta →
# ----------------------------------------------------
def dfs(u, visited, topo_order, depth, predecessor, screen):
    visited[u] = 'GRAY'
    draw_tree_dfs(screen, predecessor, depth, visited, topo_order)
    wait_for_right_key()
    
    for v in graph[u]:
        if visited[v] == 'WHITE':
            predecessor[v] = u
            depth[v] = depth[u] + 1
            dfs(v, visited, topo_order, depth, predecessor, screen)
    
    visited[u] = 'BLACK'
    topo_order.append(u)
    draw_tree_dfs(screen, predecessor, depth, visited, topo_order)
    wait_for_right_key()

# ----------------------------------------------------
# Executa DFS para todos os nós (caso o grafo seja desconexo) e gera a ordem topológica
# Reverte a lista topo_order para apresentar a sequência correta de instalação.
# ----------------------------------------------------
def dfs_topo_visual(screen):
    visited = {}
    depth = {}
    predecessor = {}
    topo_order = []
    
    for node in graph.keys():
        visited[node] = 'WHITE'
        depth[node] = None
        predecessor[node] = None
    
    for node in graph.keys():
        if visited[node] == 'WHITE':
            depth[node] = 0
            dfs(node, visited, topo_order, depth, predecessor, screen)
    
    topo_order.reverse()  # Inverte para obter a ordem topológica correta
    draw_tree_dfs(screen, predecessor, depth, visited, topo_order)
    wait_for_right_key()
    return visited, topo_order, predecessor, depth

# ----------------------------------------------------
# Anima o processo de "instalação" dos pacotes (nós) conforme a ordem topológica
# A cada pressionamento da seta →, um nó é destacado (pintado de RED) para indicar
# que a biblioteca foi instalada.
# ----------------------------------------------------
def animate_installation(screen, topo_order):
    font = pygame.font.SysFont(None, TAM_FonteNo)
    installed = []
    
    for node in topo_order:
        installed.append(node)
        screen.fill((220, 220, 220))
        
        # Cria um dicionário auxiliar para definir cores: nós instalados ficam RED
        aux_visited = {}
        for n in graph.keys():
            if n in installed:
                aux_visited[n] = RED
            else:
                aux_visited[n] = DARK_GRAY  # Nós que já foram finalizados
        # Reutiliza a função de desenho da árvore; aqui, topo_order já contém a ordem final
        draw_tree_dfs(screen, {}, {n: 0 for n in graph.keys()}, aux_visited, topo_order)
        order_text = "Instalação: " + " -> ".join(str(n) for n in installed)
        order_surface = font.render(order_text, True, BLACK)
        screen.blit(order_surface, (20, HEIGHT - 50))
        pygame.display.update()
        wait_for_right_key()

# ----------------------------------------------------
# Função principal: inicializa o Pygame, executa DFS com visualização e anima a instalação
# ----------------------------------------------------
def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ordenação Topológica via DFS (Visualização)")
    
    visited, topo_order, predecessor, depth = dfs_topo_visual(screen)
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
