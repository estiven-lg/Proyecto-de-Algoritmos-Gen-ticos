class Node:
    """
    Representa un cruce (nodo) en la red de tráfico.
    Cada nodo tiene un semáforo que distribuye el flujo entrante
    entre sus aristas salientes mediante porcentajes.
    
    Atributos:
        node_id         : identificador único (ej. 'n1')
        outgoing_edges  : lista de aristas que salen de este nodo
        percentages     : dict {edge_name: porcentaje (0-1)}
                          La suma de todos los porcentajes debe ser 1.0
    """

    def __init__(self, node_id):
        self.node_id        = node_id
        self.outgoing_edges = []   # lista de objetos Edge
        self.percentages    = {}   # {edge_name: float}

    def add_outgoing_edge(self, edge):
        """Registra una arista saliente y asigna porcentaje uniforme."""
        self.outgoing_edges.append(edge)
        # redistribuye porcentajes de manera uniforme
        n = len(self.outgoing_edges)
        for e in self.outgoing_edges:
            self.percentages[e.name] = round(1.0 / n, 4)

    def set_percentages(self, pct_dict):
        """Establece los porcentajes normalizando para que sumen 1."""
        total = sum(pct_dict.values())
        if total == 0:
            raise ValueError(f"Nodo {self.node_id}: la suma de porcentajes es 0.")
        self.percentages = {k: v / total for k, v in pct_dict.items()}

    def __repr__(self):
        return f"Node({self.node_id}, salidas={[e.name for e in self.outgoing_edges]})"
