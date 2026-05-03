class Edge:
    """
    Representa una calle (arista) entre dos cruces (nodos).
    
    Atributos:
        name        : identificador de la arista (ej. 'a1')
        edge_type   : 'ENTRADA', 'SALIDA' o None (arista interna)
        origin      : id del nodo origen
        destination : id del nodo destino
        cap_min     : capacidad mínima de vehículos
        cap_max     : capacidad máxima de vehículos
        flow        : flujo de entrada (solo para aristas ENTRADA)
    """

    def __init__(self, name, edge_type, origin, destination, cap_min, cap_max, flow=0):
        self.name        = name
        self.edge_type   = edge_type   # 'ENTRADA', 'SALIDA', o None
        self.origin      = origin
        self.destination = destination
        self.cap_min     = cap_min     # int
        self.cap_max     = cap_max     # int
        self.flow        = flow        # flujo real actual

    def __repr__(self):
        return (f"Edge({self.name}, {self.edge_type}, "
                f"{self.origin}->{self.destination}, "
                f"cap=[{self.cap_min},{self.cap_max}], flow={self.flow})")
