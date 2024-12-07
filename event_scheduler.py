import json
import numpy as np
import matplotlib.pyplot as plt
from pulp import LpProblem, LpVariable, LpBinary, lpSum, LpMinimize, LpStatus
import time
import argparse
import random

def load_data(events_file='events.json', rooms_file='rooms.json', use_fake_data=False, num_events=0, num_rooms=0):
    """
    Carrega os dados dos arquivos JSON de eventos e salas ou gera dados falsos.

    Args:
        events_file (str): Caminho para o arquivo JSON de eventos.
        rooms_file (str): Caminho para o arquivo JSON de salas.
        use_fake_data (bool): Indica se deve gerar dados falsos.
        num_events (int): Número de eventos a serem gerados.
        num_rooms (int): Número de salas a serem geradas.

    Returns:
        tuple: Uma tupla contendo a lista de eventos e a lista de salas.
    """
    if use_fake_data:
        events, rooms = generate_fake_data(num_events, num_rooms)
    else:
        with open(events_file, 'r', encoding='utf-8') as f:
            events = json.load(f)
        with open(rooms_file, 'r', encoding='utf-8') as f:
            rooms = json.load(f)
    return events, rooms

def generate_fake_data(num_events, num_rooms):
    """
    Gera dados falsos para eventos e salas.

    Args:
        num_events (int): Número de eventos a serem gerados.
        num_rooms (int): Número de salas a serem geradas.

    Returns:
        tuple: Uma tupla contendo a lista de eventos e a lista de salas.
    """
    events = []
    for i in range(num_events):
        event = {
            'id': f'Evento_{i+1}',
            'duration': random.randint(1, 4),  # Duração entre 1 e 4 horas
            'participants': random.randint(10, 100)  # Participantes entre 10 e 100
        }
        events.append(event)

    rooms = []
    for i in range(num_rooms):
        room = {
            'id': f'Sala_{i+1}',
            'capacity': random.randint(20, 120),  # Capacidade entre 20 e 120
            'availability': [[9, 18]]  # Disponibilidade das 9h às 18h
        }
        rooms.append(room)

    return events, rooms

def process_room_availabilities(rooms):
    """
    Processa as disponibilidades das salas para obter os horários disponíveis.

    Args:
        rooms (list): Lista de dicionários contendo informações das salas.

    Returns:
        dict: Dicionário com os horários disponíveis por sala.
    """
    room_available_times = {}
    for idx_r, room in enumerate(rooms):
        available_times = set()
        for interval in room['availability']:
            start, end = interval
            times_in_interval = list(range(start, end))
            available_times.update(times_in_interval)
        room_available_times[idx_r] = sorted(available_times)
    return room_available_times

def generate_possible_starts(events, rooms, room_available_times):
    """
    Gera possíveis horários de início para cada evento em cada sala.

    Args:
        events (list): Lista de eventos.
        rooms (list): Lista de salas.
        room_available_times (dict): Horários disponíveis por sala.

    Returns:
        tuple: Um dicionário de variáveis de decisão e um dicionário de possíveis inícios.
    """
    variables = {}
    possible_starts = {}
    for idx_e, event in enumerate(events):
        possible_starts[idx_e] = {}
        for idx_r, room in enumerate(rooms):
            if event['participants'] <= room['capacity']:
                possible_starts[idx_e][idx_r] = []
                duration = event['duration']
                room_times = room_available_times[idx_r]
                for interval in room['availability']:
                    start_avail, end_avail = interval
                    for start in range(start_avail, end_avail - duration + 1):
                        event_times = set(range(start, start + duration))
                        if event_times.issubset(room_times):
                            var_name = f"x_{idx_e}_{idx_r}_{start}"
                            variables[(idx_e, idx_r, start)] = LpVariable(var_name, cat=LpBinary)
                            possible_starts[idx_e][idx_r].append(start)
    return variables, possible_starts

def create_optimization_problem(events, rooms, variables, possible_starts):
    """
    Cria o problema de otimização, define a função objetivo e as restrições.

    Args:
        events (list): Lista de eventos.
        rooms (list): Lista de salas.
        variables (dict): Dicionário de variáveis de decisão.
        possible_starts (dict): Dicionário de possíveis inícios.

    Returns:
        LpProblem: O problema de otimização linear.
    """
    prob = LpProblem("Event_Scheduling", LpMinimize)

    # Função objetivo: minimizar a capacidade não utilizada
    prob += lpSum([
        (rooms[idx_r]['capacity'] - events[idx_e]['participants']) * var
        for (idx_e, idx_r, start), var in variables.items()
    ])

    # Restrição 1: cada evento deve ser alocado exatamente uma vez
    for idx_e in possible_starts:
        prob += lpSum([
            variables[(idx_e, idx_r, start)]
            for idx_r in possible_starts[idx_e]
            for start in possible_starts[idx_e][idx_r]
        ]) == 1, f"Event_{idx_e}_scheduled_once"

    # Restrição 2: nenhuma sobreposição de eventos em uma sala no mesmo horário
    times = list(range(9, 18))  # Horas de 9h às 17h
    for idx_r in range(len(rooms)):
        for t in times:
            overlapping_events = []
            for idx_e in possible_starts:
                for start in possible_starts[idx_e].get(idx_r, []):
                    duration = events[idx_e]['duration']
                    if start <= t < start + duration:
                        overlapping_events.append(variables[(idx_e, idx_r, start)])
            if overlapping_events:
                prob += lpSum(overlapping_events) <= 1, f"No_overlap_room_{idx_r}_time_{t}"
    return prob

def solve_problem(prob):
    """
    Resolve o problema de otimização linear.

    Args:
        prob (LpProblem): O problema de otimização linear.

    Returns:
        int: O status da solução.
    """
    prob.solve()
    return prob.status

def collect_allocation(variables, events, rooms):
    """
    Coleta a alocação dos eventos a partir das variáveis de decisão.

    Args:
        variables (dict): Dicionário de variáveis de decisão.
        events (list): Lista de eventos.
        rooms (list): Lista de salas.

    Returns:
        list: Lista de alocações com detalhes dos eventos.
    """
    allocation = []
    for (idx_e, idx_r, start), var in variables.items():
        if var.varValue == 1:
            event = events[idx_e]
            room = rooms[idx_r]
            end_time = start + event['duration']
            allocation.append({
                'Event': event['id'],
                'Room': room['id'],
                'Start': start,
                'End': end_time
            })
    return allocation

def display_results(status, allocation):
    """
    Exibe o status da solução e as alocações dos eventos.

    Args:
        status (int): O status da solução.
        allocation (list): Lista de alocações dos eventos.
    """
    print(f"Status da solução: {LpStatus[status]}\n")
    for alloc in allocation:
        print(f"Evento '{alloc['Event']}' alocado na '{alloc['Room']}' iniciando às {alloc['Start']}h até às {alloc['End']}h.")

def plot_schedule(allocation, events, rooms):
    """
    Cria um gráfico de Gantt para visualizar a programação dos eventos.

    Args:
        allocation (list): Lista de alocações dos eventos.
        events (list): Lista de eventos.
        rooms (list): Lista de salas.
    """
    fig, ax = plt.subplots(figsize=(10, 6))

    # Cria uma paleta de cores para os eventos
    event_ids = [event['id'] for event in events]
    colors = plt.get_cmap('tab20')

    # Mapeia cada evento a uma cor distinta
    color_dict = {event_id: colors(i / len(event_ids)) for i, event_id in enumerate(event_ids)}

    # Prepara os dados para o gráfico
    room_ids = [room['id'] for room in rooms]
    y_ticks = np.arange(len(room_ids))
    height = 0.8

    for alloc in allocation:
        room_idx = room_ids.index(alloc['Room'])
        ax.barh(room_idx, alloc['End'] - alloc['Start'], left=alloc['Start'], height=height,
                align='center', color=color_dict[alloc['Event']], edgecolor='black')
        ax.text(alloc['Start'] + (alloc['End'] - alloc['Start']) / 2, room_idx,
                alloc['Event'], va='center', ha='center', color='black', fontsize=9)

    # Configurações do gráfico
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(room_ids)
    ax.set_xlabel('Horário')
    ax.set_ylabel('Salas')
    ax.set_title('Programação de Eventos')

    ax.set_xlim(9, 18)
    ax.set_xticks(range(9, 19))
    ax.grid(True, axis='x', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.show()
    
def code_complexity_analysis(event_counts, room_counts):
    """
    Realiza a análise de complexidade do código para diferentes quantidades de eventos e salas.

    Args:
        event_counts (list): Lista com as quantidades de eventos a serem testadas.
        room_counts (list): Lista com as quantidades de salas a serem testadas.
    """
    execution_times = {num_rooms: [] for num_rooms in room_counts}

    for num_rooms in room_counts:
        print(f"Analisando para {num_rooms} salas...")
        for num_events in event_counts:
            print(f"  - {num_events} eventos")
            events, rooms = load_data(use_fake_data=True, num_events=num_events, num_rooms=num_rooms)
            start_time = time.time()
            room_available_times = process_room_availabilities(rooms)
            variables, possible_starts = generate_possible_starts(events, rooms, room_available_times)
            prob = create_optimization_problem(events, rooms, variables, possible_starts)
            solve_problem(prob)
            end_time = time.time()
            execution_times[num_rooms].append(end_time - start_time)

    # Plotando o gráfico de tempo de execução vs número de eventos para diferentes números de salas
    plt.figure(figsize=(10, 6))
    for num_rooms, times in execution_times.items():
        plt.plot(event_counts, times, marker='o', label=f'{num_rooms} Salas')

    plt.xlabel('Número de Eventos')
    plt.ylabel('Tempo de Execução (s)')
    plt.title('Análise de Complexidade do Código')
    plt.legend(title="Número de Salas")
    plt.grid(True)
    plt.show()

def main():
    """
    Função principal que coordena a execução do programa.
    """
    parser = argparse.ArgumentParser(description='Programa de Agendamento de Eventos')
    parser.add_argument('--analysis', action='store_true', help='Executa a análise de complexidade do código')
    parser.add_argument('--event_counts', type=str, default='5,10,30,50', help='Quantidades de eventos para análise, separadas por vírgula')
    parser.add_argument('--num_rooms', type=str, default='5,10,15', help='Quantidades de salas para análise, separadas por vírgula')
    args = parser.parse_args()

    if args.analysis:
        event_counts = [int(x) for x in args.event_counts.split(',')]
        room_counts = [int(x) for x in args.num_rooms.split(',')]
        code_complexity_analysis(event_counts, room_counts)
    else:
        # Fluxo padrão
        events, rooms = load_data()
        room_available_times = process_room_availabilities(rooms)
        variables, possible_starts = generate_possible_starts(events, rooms, room_available_times)
        prob = create_optimization_problem(events, rooms, variables, possible_starts)
        status = solve_problem(prob)
        allocation = collect_allocation(variables, events, rooms)
        display_results(status, allocation)
        plot_schedule(allocation, events, rooms)

if __name__ == "__main__":
    main()
