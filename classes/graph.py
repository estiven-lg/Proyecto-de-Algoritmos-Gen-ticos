import csv
import io
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx

from .edge import Edge
from .node import Node


class Graph:
    """Grafo dirigido que modela la red de tráfico."""
    
    def __init__(self):
        self.nodes = {}  # {node_id: Node}
        self.edges = {}  # {edge_name: Edge}
    
    def add_node(self, node):
        self.nodes[node.node_id] = node
    
    def add_edge(self, edge):
        self.edges[edge.name] = edge
        # Registrar en nodos
        if edge.origin in self.nodes:
            self.nodes[edge.origin].add_outgoing_edge(edge)
    
    @staticmethod
    def from_csv_string(csv_string):
        """Crea un grafo desde un string CSV."""
        graph = Graph()
        reader = csv.DictReader(io.StringIO(csv_string.strip()))
        
        for row in reader:
            name = row['Arista']
            edge_type = row['TipoArista'].strip() if row['TipoArista'].strip() else None
            origin = row['NodoOrigen'].strip()
            destination = row['NodoDestino'].strip()
            cap_min = float(row['CapacidadMinima'].strip() or 0)
            cap_max = float(row['CapacidadMaxima'].strip() or 1000)
            flow = float(row['FlujoEntrada'].strip()) if row['FlujoEntrada'].strip() else 0
            
            # Crear nodos si no existen
            if origin not in graph.nodes:
                graph.add_node(Node(origin))
            if destination not in graph.nodes:
                graph.add_node(Node(destination))
            
            # Crear y agregar arista
            edge = Edge(name, edge_type, origin, destination, cap_min, cap_max, flow)
            graph.add_edge(edge)
        
        return graph

    def simulate_flow(self, percentages=None):
        """Simula propagación de flujo usando porcentajes de nodos."""
        flow = {}
        for edge in self.edges.values():
            flow[edge.name] = 0
        
        # Inicializar con flujos de entrada
        for edge in self.edges.values():
            if edge.edge_type == 'ENTRADA':
                flow[edge.name] = edge.flow
        
        # Propagar flujo (BFS topológico)
        visited = set()
        queue = []
        
        for edge in self.edges.values():
            if edge.edge_type == 'ENTRADA' and edge.destination:
                if edge.destination not in visited:
                    queue.append(edge.destination)
                    visited.add(edge.destination)
        
        while queue:
            node_id = queue.pop(0)
            node = self.nodes.get(node_id)
            if node is None or not node.outgoing_edges:
                continue
            
            # Sumar flujo entrante
            total_in = sum(flow.get(e.name, 0) for e in self.edges.values() 
                          if e.destination == node_id)
            
            if total_in > 0:
                # Distribuir usando porcentajes del nodo
                for out_edge in node.outgoing_edges:
                    pct = node.percentages.get(out_edge.name, 1.0/len(node.outgoing_edges))
                    if percentages and node_id in percentages:
                        pct = percentages[node_id].get(out_edge.name, pct)
                    flow[out_edge.name] = total_in * pct
                    if out_edge.destination and out_edge.destination not in visited:
                        queue.append(out_edge.destination)
                        visited.add(out_edge.destination)
        
        return flow

    @property
    def entry_edges(self):
        return [e for e in self.edges.values() if e.edge_type == 'ENTRADA']

    @property
    def exit_edges(self):
        return [e for e in self.edges.values() if e.edge_type == 'SALIDA']

    # ====== MÉTODO DRAW MEJORADO ======
    
    def draw(self, title="Red de Tráfico", flow_on_edge=None, show_flow=True, ax=None):
        """
        Dibuja el grafo con estilo mejorado usando networkx + matplotlib.
        Si show_flow=True, colorea aristas según saturación.
        """
        G = nx.DiGraph()

        # Agregar nodos
        for node_id in self.nodes:
            G.add_node(node_id)

        # Agregar aristas y preparar estilos
        edge_labels = {}
        edge_colors = []
        for edge in self.edges.values():
            if edge.origin and edge.destination:
                G.add_edge(edge.origin, edge.destination)
                
                # Etiqueta de arista
                if show_flow and flow_on_edge:
                    f = flow_on_edge.get(edge.name, 0)
                    label = f'{edge.name}\n{f:.0f}/{edge.cap_max}'
                else:
                    label = f'{edge.name}\n[{edge.cap_min},{edge.cap_max}]'
                edge_labels[(edge.origin, edge.destination)] = label

                # Color según tipo
                if edge.edge_type == 'ENTRADA':
                    edge_colors.append('#2ecc71')   # Verde = entrada
                elif edge.edge_type == 'SALIDA':
                    edge_colors.append('#e74c3c')   # Rojo = salida
                else:
                    # Gradiente para aristas normales
                    if show_flow and flow_on_edge and edge.cap_max > 0:
                        f = flow_on_edge.get(edge.name, 0)
                        ratio = min(f / edge.cap_max, 1.0)
                        edge_colors.append(plt.cm.Blues(0.3 + ratio * 0.7))
                    else:
                        edge_colors.append('#3498db')   # Azul

        if ax is None:
            fig, ax = plt.subplots(figsize=(14, 8))

        pos = nx.spring_layout(G, seed=42, k=2.5, iterations=50)

        # Color de nodos según rol
        node_colors = []
        for n in G.nodes():
            is_source = not any(e.destination == n for e in self.edges.values())
            is_sink = not any(e.origin == n for e in self.edges.values())
            
            if is_source:
                node_colors.append('#f39c12')      # Naranja = fuente
            elif is_sink:
                node_colors.append('#9b59b6')      # Morado = sumidero
            else:
                node_colors.append('#ecf0f1')      # Gris = interno

        # Dibujar
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                               node_size=1200, edgecolors='#2c3e50', linewidths=2.5)
        nx.draw_networkx_labels(G, pos, ax=ax, font_size=11, font_weight='bold')
        nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors,
                               arrows=True, arrowsize=25, width=2.5,
                               connectionstyle='arc3,rad=0.1')
        nx.draw_networkx_edge_labels(G, pos, edge_labels, ax=ax,
                                     font_size=8, bbox=dict(boxstyle='round,pad=0.3',
                                     fc='white', alpha=0.85))

        # Leyenda
        legend = [
            mpatches.Patch(color='#2ecc71', label='ENTRADA'),
            mpatches.Patch(color='#e74c3c', label='SALIDA'),
            mpatches.Patch(color='#3498db', label='NORMAL'),
            mpatches.Patch(color='#f39c12', label='Nodo fuente'),
            mpatches.Patch(color='#9b59b6', label='Nodo sumidero'),
        ]
        ax.legend(handles=legend, loc='upper left', fontsize=10, framealpha=0.95)
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15)
        ax.axis('off')
        plt.tight_layout()
        return ax

    def __repr__(self):
        return f"Graph(nodes={list(self.nodes.keys())}, edges={list(self.edges.keys())})"
