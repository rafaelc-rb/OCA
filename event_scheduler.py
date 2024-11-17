import json
from pulp import LpProblem, LpVariable, LpBinary, lpSum, LpMinimize, LpStatus
import matplotlib.pyplot as plt

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

# Coleta a alocação dos eventos para exibição e plotagem
allocation = []
for (idx_e, idx_r, start), var in variables.items():
    if var.varValue == 1:
        event = events[idx_e]
        room = rooms[idx_r]
        end_time = start + event['duration']
        print(f"Evento '{event['name']}' alocado na '{room['name']}' iniciando às {start}h até às {end_time}h.")
        allocation.append({
            'Event': event['name'],
            'Room': room['name'],
            'Start': start,
            'End': end_time
        })

# Cria o gráfico de Gantt
import numpy as np

fig, ax = plt.subplots(figsize=(10, 6))

# Cria uma paleta de cores para os eventos
event_names = [event['name'] for event in events]
colors = plt.get_cmap('tab20')

# Mapeia cada evento a uma cor distinta
color_dict = {event_name: colors(i / len(event_names)) for i, event_name in enumerate(event_names)}

# Prepara os dados para o gráfico
rooms_names = [room['name'] for room in rooms]
y_ticks = np.arange(len(rooms_names))
height = 0.8

for alloc in allocation:
    room_idx = rooms_names.index(alloc['Room'])
    ax.barh(room_idx, alloc['End'] - alloc['Start'], left=alloc['Start'], height=height,
            align='center', color=color_dict[alloc['Event']], edgecolor='black')
    ax.text(alloc['Start'] + (alloc['End'] - alloc['Start']) / 2, room_idx,
            alloc['Event'], va='center', ha='center', color='white', fontsize=9)

# Configurações do gráfico
ax.set_yticks(y_ticks)
ax.set_yticklabels(rooms_names)
ax.set_xlabel('Horário')
ax.set_ylabel('Salas')
ax.set_title('Programação de Eventos')

ax.set_xlim(9, 18)
ax.set_xticks(range(9, 19))
ax.grid(True, axis='x', linestyle='--', alpha=0.5)

plt.tight_layout()
plt.show()
