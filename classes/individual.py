import random


class Individual:
    """
    Un individuo representa una configuración de semáforos:
    para cada nodo con múltiples salidas, almacena los porcentajes
    de tiempo que se da paso hacia cada arista saliente.

    Cromosoma: dict {node_id: {edge_name: float (0-1)}}
    La suma de porcentajes por nodo siempre es 1.0

    Atributos:
        chromosome : dict con los porcentajes
        fitness    : valor de aptitud calculado
    """

    def __init__(self, chromosome=None):
        self.chromosome = chromosome or {}
        self.fitness = 0.0

    @classmethod
    def random(cls, graph):
        """Crea un individuo con porcentajes aleatorios para cada nodo."""
        chromo = {}
        for nid, node in graph.nodes.items():
            out = node.outgoing_edges
            if len(out) <= 1:
                continue   # nodo con una sola salida, sin decisión
            vals = [random.random() for _ in out]
            total = sum(vals)
            chromo[nid] = {e.name: v / total for e, v in zip(out, vals)}
        return cls(chromo)

    def evaluate(self, graph):
        """Calcula el fitness = suma del flujo que llega a aristas SALIDA."""
        flow = graph.simulate_flow(self.chromosome)
        total_exit = sum(
            flow[e.name]
            for e in graph.edges.values()
            if e.edge_type == 'SALIDA'
        )
        self.fitness = total_exit
        return self.fitness

    def __repr__(self):
        return f"Individual(fitness={self.fitness:.2f})"
