# main.py
"""
Interfaz de consola: ambos módulos con validación, lectura archivo o consola, JSON de prueba.
"""
import json
import os
from transportation_module import TransportAssignment
from server_assignment_module import Server, Request, ServerAssignment

def load_data_prompt():
    print("¿Cargar datos desde JSON? (s/n) [n]: ")
    return input().lower().startswith('s')

def read_matrix(rows:int, cols:int)->list:
    matriz=[]
    for i in range(rows):
        while True:
            s=input(f"Fila {i+1} (valores separados por espacio) [enter para defecto]: ")
            if not s: return []
            row=list(map(float,s.split()))
            if len(row)==cols: break
            print("Número de columnas incorrecto.")
        matriz.append(row)
    return matriz
def main():
    while True:
        print("1: Transporte | 2: Servidores | 3: Salir")
        opt=input("Módulo: ")
        if opt=='1':
            try:
                if load_data_prompt():
                    ta = TransportAssignment.from_json('data.json')
                    print("Método inicial: 1=Noroeste,2=Vogel,3=Costo Mínimo [1]: ")
                    meth=input() or '1'
                    getattr(ta, {'1':'northwest_corner','2':'vogel_approximation','3':'minimum_cost'}[meth])()
                else:
                    N=int(input("# Programadores [2]: ") or 2)
                    M=int(input("# Tareas [2]: ") or 2)
                    print("Método inicial: 1=Noroeste,2=Vogel,3=Costo Mínimo [1]: ")
                    meth=input() or '1'
                    cost=read_matrix(N,M) or [[5,8],[7,3]]
                    supply=list(map(int,input(f"Supply ({N} vals) [1 1]: ").split() or [1]*N))
                    demand=list(map(int,input(f"Demand ({M} vals) [1 1]: ").split() or [1]*M))
                    ta=TransportAssignment(cost,supply,demand)
                    getattr(ta, {'1':'northwest_corner','2':'vogel_approximation','3':'minimum_cost'}[meth])()
                ta.report()
            except Exception as e: print(f"Error: {e}")
        elif opt=='2':
            try:
                if load_data_prompt():
                    sa = ServerAssignment.from_json('data.json')
                    sa.solve()
                else:
                    S=int(input("# Servidores [2]: ") or 2)
                    R=int(input("# Solicitudes [2]: ") or 2)
                    servers=[]; requests=[]
                    for i in range(S):
                        vals=input(f"Servidor {i} (cpu mem bw) [10 10 10]: ")
                        cpu,mem,bw=map(int,vals.split()) if vals else (10,10,10)
                        servers.append(Server(i,cpu,mem,bw))
                    for j in range(R):
                        vals=input(f"Solicitud {j} (cpu mem bw prio) [3 3 3 1]: ")
                        c,m,b,p=map(int,vals.split()) if vals else (3,3,3,1)
                        requests.append(Request(j,c,m,b,p))
                    cost=read_matrix(S,R) or [[2,5],[6,4]]
                    sa=ServerAssignment(servers,requests,cost)
                    sa.solve()
                sa.report()
            except Exception as e: print(f"Error: {e}")
        elif opt=='3': break
        else: print("Opción inválida.")

if __name__=='__main__': main()