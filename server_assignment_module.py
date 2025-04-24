# server_assignment_module.py
"""
Módulo 2: Optimización de la Asignación de Solicitudes a Servidores
Paradigma: POO
Método: Húngaro + verificación de restricciones (capacidad, prioridad, balance)
"""
from typing import List, Optional
import json
import os

class Server:
    def __init__(self, id:int, cpu:int, memory:int, bandwidth:int):
        self.id = id
        self.cpu = cpu; self.memory = memory; self.bandwidth = bandwidth
        self.load_cpu=0; self.load_mem=0; self.load_bw=0

class Request:
    def __init__(self, id:int, cpu_req:int, mem_req:int, bw_req:int, priority:int):
        self.id=id
        self.cpu_req=cpu_req; self.mem_req=mem_req; self.bw_req=bw_req
        self.priority=priority

class ServerAssignment:
    def __init__(self, servers:List[Server], requests:List[Request], cost_matrix:List[List[float]]):
        self.servers=servers
        self.requests=sorted(requests, key=lambda r: -r.priority)
        self.S=len(servers); self.R=len(requests)
        if any(len(row)!=self.R for row in cost_matrix):
            raise ValueError("Matriz de costos debe tener R columnas")
        if len(cost_matrix)!=self.S:
            raise ValueError("Matriz de costos debe tener S filas")
        self.cost_matrix=cost_matrix
        self.assignment: List[Optional[int]]=[None]*self.R
        self.total_time: float=0.0

    def solve(self):
        n=max(self.S, self.R)
        cost=[[0]*n for _ in range(n)]
        for i in range(self.S):
            for j in range(self.R): cost[i][j]=self.cost_matrix[i][j]
        u=[0]*(n+1); v=[0]*(n+1); p=[0]*(n+1); way=[0]*(n+1)
        for i in range(1,n+1):
            p[0]=i; j0=0; minv=[float('inf')]*(n+1); used=[False]*(n+1)
            while True:
                used[j0]=True; i0=p[j0]; delta=float('inf'); j1=0
                for j in range(1,n+1):
                    if not used[j]:
                        cur = cost[i0-1][j-1]-u[i0]-v[j]
                        if cur<minv[j]: minv[j]=cur; way[j]=j0
                        if minv[j]<delta: delta=minv[j]; j1=j
                for j in range(n+1):
                    if used[j]: u[p[j]]+=delta; v[j]-=delta
                    else: minv[j]-=delta
                j0=j1
                if p[j0]==0: break
            while True:
                j1=way[j0]; p[j0]=p[j1]; j0=j1
                if j0==0: break
        for j in range(1,n+1):
            i=p[j]
            if i<=self.S and j<=self.R:
                self.assignment[j-1]=i-1
        for rid, sid in enumerate(self.assignment):
            if sid is not None:
                req=self.requests[rid]; srv=self.servers[sid]
                if (srv.load_cpu+req.cpu_req>srv.cpu or
                    srv.load_mem+req.mem_req>srv.memory or
                    srv.load_bw+req.bw_req>srv.bandwidth):
                    print(f"Warning: Capacidad excedida en servidor {srv.id} para solicitud {req.id}")
                srv.load_cpu+=req.cpu_req; srv.load_mem+=req.mem_req; srv.load_bw+=req.bw_req
                self.total_time+=self.cost_matrix[sid][rid]

    def report(self):
        print("\n--- Reporte Servidores ---")
        for rid, sid in enumerate(self.assignment):
            if sid is not None:
                req=self.requests[rid]; srv=self.servers[sid]
                print(f"Solicitud {req.id}(P{req.priority}) -> Servidor {srv.id} | Tiempo={self.cost_matrix[sid][rid]}")
        print(f"Tiempo Total: {self.total_time}\n")
        print("Carga por Servidor (CPU,Mem,BW):")
        for srv in self.servers:
            print(f"Servidor {srv.id}: CPU {srv.load_cpu}/{srv.cpu}, Mem {srv.load_mem}/{srv.memory}, BW {srv.load_bw}/{srv.bandwidth}")

    @staticmethod
    def from_json(file_path: str) -> 'ServerAssignment':
        """Carga estructuras desde un JSON externo."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        servers = [Server(**s) for s in data['servers']]
        requests = [Request(**r) for r in data['requests']]
        return ServerAssignment(servers, requests, data['cost_matrix'])