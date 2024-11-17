import json
from pulp import LpProblem, LpVariable, LpBinary, lpSum, LpMinimize, LpStatus

# Carrega os dados dos arquivos JSON
with open('events.json', 'r', encoding='utf-8') as f:
    events = json.load(f)

with open('rooms.json', 'r', encoding='utf-8') as f:
    rooms = json.load(f)

# Define o intervalo de tempo (horas disponíveis)
times = list(range(9, 18))  # Horas de 9h às 17h

# Processa as salas para obter horários disponíveis
room_available_times = {}
for idx_r, room in enumerate(rooms):
    available_times = set()
    for interval in room['availability']:
        start, end = interval
        # Considera intervalos como [start, end), excluindo o 'end'
        times_in_interval = list(range(start, end))
        available_times.update(times_in_interval)
    room_available_times[idx_r] = sorted(available_times)

# Gera possíveis horários de início para cada evento em cada sala
variables = {}
possible_starts = {}
for idx_e, event in enumerate(events):
    possible_starts[idx_e] = {}
    for idx_r, room in enumerate(rooms):
        if event['participants'] <= room['capacity']:
            possible_starts[idx_e][idx_r] = []
            duration = event['duration']
            room_times = room_available_times[idx_r]
            # Encontra possíveis horários de início dentro das disponibilidades da sala
            for interval in room['availability']:
                start_avail, end_avail = interval
                for start in range(start_avail, end_avail - duration + 1):
                    # Verifica se todos os tempos do evento estão disponíveis
                    event_times = set(range(start, start + duration))
                    if event_times.issubset(room_times):
                        variables[(idx_e, idx_r, start)] = LpVariable(f"x_{idx_e}_{idx_r}_{start}", cat=LpBinary)
                        possible_starts[idx_e][idx_r].append(start)

# Cria o problema de otimização
prob = LpProblem("Event_Scheduling", LpMinimize)

# Função objetivo: minimizar a capacidade não utilizada
prob += lpSum([
    (room['capacity'] - event['participants']) * variables[(idx_e, idx_r, start)]
    for (idx_e, idx_r, start), var in variables.items()
    for event in [events[idx_e]]
    for room in [rooms[idx_r]]
])

# Restrição 1: cada evento deve ser alocado exatamente uma vez
for idx_e, event in enumerate(events):
    prob += lpSum([
        variables[(idx_e, idx_r, start)]
        for idx_r in possible_starts[idx_e]
        for start in possible_starts[idx_e][idx_r]
    ]) == 1, f"Event_{idx_e}_scheduled_once"

# Restrição 2: nenhuma sobreposição de eventos em uma sala no mesmo horário
for idx_r, room in enumerate(rooms):
    for t in times:
        overlapping_events = []
        for idx_e, event in enumerate(events):
            duration = event['duration']
            for start in possible_starts.get(idx_e, {}).get(idx_r, []):
                if start <= t < start + duration:
                    overlapping_events.append(variables[(idx_e, idx_r, start)])
        if overlapping_events:
            prob += lpSum(overlapping_events) <= 1, f"No_overlap_room_{idx_r}_time_{t}"

# Resolve o problema
prob.solve()

# Exibe o status da solução
print(f"Status da solução: {LpStatus[prob.status]}\n")

# Exibe a alocação dos eventos
for (idx_e, idx_r, start), var in variables.items():
    if var.varValue == 1:
        event = events[idx_e]
        room = rooms[idx_r]
        print(f"Evento '{event['name']}' alocado na '{room['name']}' iniciando às {start}h até às {start + event['duration']}h.")
