from itertools import count
import sys
from collections import namedtuple
from time import time
from progress.bar import Bar
import os
import math
import datetime

Node = namedtuple("Node", ['x', 'y', 'index'])


def length(node1, node2):
    # Função que calcula distância euclidiana entre dois vértices do plano.
    return math.sqrt((node1.x - node2.x)**2 + (node1.y - node2.y)**2)

def calc_time_edge(node1, node2, speed_truck, speed_drone, flag_edge):
    # Função para calcular o tempo de viajem em uma aresta
    if flag_edge.lower() == "truck":
        time = length(node1, node2)/speed_truck
    elif flag_edge.lower() == "drone":
        time = length(node1, node2)/speed_drone
    else:
        return None
    return time

def calc_time_drone_nodes(drone_nodes, speed_drone, nodes):
    # vamos calcular o tempo consumido pela rota do drone
    time = 0
    for i in range(len(drone_nodes)):
        time += calc_time_edge(nodes[drone_nodes[i - 1]], nodes[drone_nodes[i]], 0, speed_drone, "drone")
    return time

def calc_time_truck_nodes(truck_nodes, speed_truck, nodes):
    # vamos calcular o tempo consumido pela rota do caminhão
    time = 0
    for i in range(len(truck_nodes)):
        time += calc_time_edge(nodes[truck_nodes[i - 1]], nodes[truck_nodes[i]], speed_truck, 0, "truck")
    return time

def calc_time_operation(truck_nodes, drone_nodes, speed_truck, speed_drone, nodes):
    # vamos calcular o tempo consumido por cada operação
    if len(drone_nodes) > 0:
        time_truck_route = calc_time_truck_nodes(truck_nodes, speed_truck, nodes)
        time_drone_route = calc_time_drone_nodes(drone_nodes, speed_drone, nodes)
        time = max(time_truck_route, time_drone_route)
    else:
        time = calc_time_truck_nodes(truck_nodes, speed_truck, nodes)
    return time

def calc_obj(operations, speed_truck, speed_drone, nodes):
    # vamos calcular a função objetivo do problema
    cost_obj = 0
    for i in range(len(operations)):
        truck_nodes = operations[i][0]
        drone_nodes = operations[i][1]
        cost_obj += calc_time_operation(truck_nodes, drone_nodes, speed_truck, speed_drone, nodes)
    return cost_obj

def pass_comments(lines):
    # Função para ignorar comentários
    # das entradas da instância e tratar "/n".
    lines = lines.split('\n')
    num_input = []
    for line in lines:
        if not line.strip().startswith('/'):
            num_input.append(line)
    return num_input

def create_nodes(node_count, file_location):
    # Função para ler informações da entrada 
    # e criar nossas triplas que representam nós
    # no grafo.
    file_location = file_location.replace("author_solutions", "")
    file_location = file_location.replace("-sMIP", "")
    with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
    lines = pass_comments(input_data)
    speed_truck = float(lines[0])
    speed_drone = float(lines[1])
    nodes = []
    for i in range(3, node_count + 3):
        line = lines[i]
        parts = line.split()
        # Pré-processamento para se adequar aos nosso algoritmos
        if parts[2] == "depot":
            parts[2] = 0
        elif parts[2].find("v") != -1:
            parts[2] = parts[2].replace("v", "")
        elif parts[2].find("u") != -1:
            parts[2] = parts[2].replace("u", "")
        elif parts[2].find("loc") != -1:
            parts[2] = parts[2].replace("loc", "")
        nodes.append(
            Node(float(parts[0]), float(parts[1]), int(parts[2])))
    return nodes, speed_truck, speed_drone

def verify_sol(input_data, file_location):
    # Função para coletar soluçao do autor.

    # Tratamento da entrada.
    sol_auth = pass_comments(input_data)
    # Primeira posiçao do arquivo armazena qtd de vértices.
    count_operation = int(float(sol_auth[0]))
    
    # Coleta as informaçoes correspendentes à essa instância.
    nodes, speed_truck, speed_drone = create_nodes(count_operation, file_location)

    # Construir o tour da solução do autor
    operations = []
    
    for i in range(1, count_operation + 1):
        line = sol_auth[i]
        parts = line.split()
        start = int(parts[0])
        end = int(parts[1])
        drone_node = int(parts[2])
        if drone_node == -1:
            continue
        internal_nodes = int(parts[3])
        truck_nodes = [start]
        for j in range(4, internal_nodes + 4):
            truck_nodes.append(int(parts[j]))
        if truck_nodes[internal_nodes] != end:
            truck_nodes.append(end)
        if drone_node > 0:
            drone_nodes = [start, drone_node, end]
        else:
            drone_nodes = []
        operations.append([truck_nodes, drone_nodes])
    # print(operations)
    return calc_sol(count_operation, nodes, operations, speed_truck, speed_drone)

def calc_sol(count_operation, nodes, operations, speed_truck, speed_drone):
    # Nessa função é calculado o custo da solução
    # obtida pelo autor do dataset
    cost_obj = int(calc_obj(operations, speed_truck, speed_drone, nodes))
    
    # convertendo o tempo para horas:
    cost_obj = str(datetime.timedelta(seconds=cost_obj))
    
    # tempo do tour no output data
    output_data = cost_obj + '\n'

    # TODO: formar os circuitos do caminhão e drone
    # output_data += " ".join([str(tour[i]) for i in range(node_count)]) + '\n'

    return output_data


if __name__ == '__main__':
    # Função "main" seleciona o input na linha de comando
    # decide se roda todas as instâncias ou apenas uma específica
    # Formatos:
    # python tspd.py "info"
    # info pode ser:
    # Caminho da instância a ser executada.
    # 1 - Roda apenas DoubleCenter
    # 2 - Roda apenas SingleCenter
    # 3 - Roda apenas Uniform
    # 4 - Roda todas
    # após resolução do problema
    # escreve em arquivo a solução obtida. 
    if len(sys.argv) > 1:
        if sys.argv[1].strip() == "1":
            count = 0
            path = ".\\data\\instances\\doublecenter\\author_solutions"
            file_location = []
            for file in os.listdir(path):
                if file.endswith(".txt") and file.find("tsp") == -1:
                    count += 1
                    file_location.append(f"{path}\{file}".strip())
        elif sys.argv[1].strip() == "2":
            count = 0
            path = ".\\data\\instances\\singlecenter\\author_solutions"
            file_location = []
            for file in os.listdir(path):
                if file.endswith(".txt") and file.find("tsp") == -1:
                    count += 1
                    file_location.append(f"{path}\{file}".strip())
        elif sys.argv[1].strip() == "3":
            count = 0
            path = ".\\data\\instances\\uniform\\author_solutions"
            file_location = []
            for file in os.listdir(path):
                if file.endswith(".txt") and file.find("tsp") == -1:
                    count += 1
                    file_location.append(f"{path}\{file}".strip())
        elif sys.argv[1].strip() == "4": # Faça todos os passos anteriores
            count = 0
            path = ".\\data\\instances\\doublecenter\\author_solutions"
            file_location = []
            for file in os.listdir(path):
                if file.endswith(".txt") and file.find("tsp") == -1:
                    count += 1
                    file_location.append(f"{path}\{file}".strip())
            
            path = ".\\data\\instances\\singlecenter\\author_solutions"
            for file in os.listdir(path):
                if file.endswith(".txt") and file.find("tsp") == -1:
                    count += 1
                    file_location.append(f"{path}\{file}".strip())
            
            path = ".\\data\\instances\\uniform\\author_solutions"
            for file in os.listdir(path):
                if file.endswith(".txt") and file.find("tsp") == -1:
                    count += 1
                    file_location.append(f"{path}\{file}".strip())
        else:
            file_location = sys.argv[1].strip()
            with open(file_location, 'r') as input_data_file:
                input_data = input_data_file.read()
            output_data = verify_sol(input_data, file_location)
            file_location = file_location.replace("instances", "solutions") 
            file_location = file_location.replace("author_solutions", "")
            file_location = file_location.split(".txt")
            solution_file = open(file_location[0] + "-author-value" + ".sol", "w")
            solution_file.write(output_data)
            solution_file.close()
            sys.exit()
        with Bar('Processing...', max=count) as bar:
            for file in file_location:
                with open(file, 'r') as input_data_file:
                    input_data = input_data_file.read()
                output_data = verify_sol(input_data, file)
                file = file.replace("instances", "solutions") 
                file = file.replace("author_solutions", "")
                file = file.split(".txt")
                solution_file = open(file[0] + "-author-value" + ".sol", "w")
                solution_file.write(output_data)
                solution_file.close()
                bar.next()
    else:
        print('This test requires an input file.  Please select one from the data directory. \
             (i.e. python solver.py ./data/instances/singlecenter/author_solutions/singlecenter-1-n5-tsp.txt)')