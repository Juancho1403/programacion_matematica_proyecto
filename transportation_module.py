# transportation_module.py
"""
Módulo 1: Asignación de Programadores a Tareas con Restricciones de Transporte
Paradigma: Programación Orientada a Objetos
Métodos de solución inicial: Esquina Noroeste, Vogel, Costo Mínimo
"""
from typing import List
import json
import os

class TransportAssignment:
    def __init__(
        self,
        cost_matrix: List[List[float]],
        supply: List[int],
        demand: List[int]
    ):
        # Validaciones básicas
        if len(cost_matrix) != len(supply):
            raise ValueError("Número de filas de matriz debe coincidir con tamaño de supply")
        if any(len(row) != len(demand) for row in cost_matrix):
            raise ValueError("Número de columnas de matriz debe coincidir con tamaño de demand")
        # Datos internos
        self.N = len(supply)
        self.M = len(demand)
        self.cost_matrix = cost_matrix
        self.supply = supply.copy()
        self.demand = demand.copy()
        # Solución: cantidad asignada de programador i a tarea j
        self.solution = [[0]*self.M for _ in range(self.N)]
        self.total_cost: float = 0.0

    def _reset(self):
        """Reinicializa solución y datos auxiliares."""
        self.solution = [[0]*self.M for _ in range(self.N)]
        self._supply = self.supply.copy()
        self._demand = self.demand.copy()

    def northwest_corner(self):
        """Inicializa usando el método de Esquina Noroeste."""
        self._reset()
        i, j = 0, 0
        while i < self.N and j < self.M:
            qty = min(self._supply[i], self._demand[j])
            self.solution[i][j] = qty
            self._supply[i] -= qty; self._demand[j] -= qty
            if self._supply[i] == 0: i += 1
            if self._demand[j] == 0: j += 1
        self._compute_cost()

    def vogel_approximation(self):
        """Inicializa usando la Aproximación de Vogel."""
        import copy
        self._reset()
        cost = copy.deepcopy(self.cost_matrix)
        supply = self._supply; demand = self._demand
        while any(supply) and any(demand):
            rows_pen = []
            for i in range(self.N):
                costs = [cost[i][j] for j in range(self.M) if demand[j]>0]
                if len(costs)>=2:
                    diff = sorted(costs)[1] - sorted(costs)[0]
                    rows_pen.append((diff, i))
            cols_pen = []
            for j in range(self.M):
                costs = [cost[i][j] for i in range(self.N) if supply[i]>0]
                if len(costs)>=2:
                    diff = sorted(costs)[1] - sorted(costs)[0]
                    cols_pen.append((diff, j))
            if not rows_pen and not cols_pen:
                break
            pen, idx = max(rows_pen+cols_pen, key=lambda x: x[0])
            if (pen, idx) in rows_pen:
                i = idx
                j = min((j for j in range(self.M) if demand[j]>0), key=lambda j: cost[i][j])
            else:
                j = idx
                i = min((i for i in range(self.N) if supply[i]>0), key=lambda i: cost[i][j])
            qty = min(supply[i], demand[j])
            self.solution[i][j] = qty
            supply[i] -= qty; demand[j] -= qty
        self._compute_cost()

    def minimum_cost(self):
        """Inicializa usando el Método de Costo Mínimo."""
        import copy
        self._reset()
        supply = self._supply; demand = self._demand
        cost = copy.deepcopy(self.cost_matrix)
        while any(supply) and any(demand):
            min_val = float('inf'); i_min=j_min=-1
            for i in range(self.N):
                for j in range(self.M):
                    if supply[i]>0 and demand[j]>0 and cost[i][j]<min_val:
                        min_val = cost[i][j]; i_min,j_min = i,j
            qty = min(supply[i_min], demand[j_min])
            self.solution[i_min][j_min] = qty
            supply[i_min] -= qty; demand[j_min] -= qty
        self._compute_cost()

    def _compute_cost(self):
        """Calcula costo total según la solución actual."""
        self.total_cost = sum(
            self.solution[i][j] * self.cost_matrix[i][j]
            for i in range(self.N) for j in range(self.M)
        )

    def report(self):
        """Imprime detalle de asignaciones y costo individual y total."""
        print("\n--- Reporte Transporte ---")
        for i in range(self.N):
            for j in range(self.M):
                qty = self.solution[i][j]
                if qty>0:
                    print(f"Programador {i} -> Tarea {j}: Cant={qty}, CostoUnit={self.cost_matrix[i][j]}")
        print(f"Costo Total Mínimo: {self.total_cost}\n")

    @staticmethod
    def from_json(file_path: str) -> 'TransportAssignment':
        """Carga datos desde un JSON externo."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return TransportAssignment(
            data['cost_matrix'], data['supply'], data['demand']
        )