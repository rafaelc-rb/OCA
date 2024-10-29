import json
import pulp
import pandas as pd
import matplotlib.pyplot as plt

# Sample data (You can replace this with code to read from JSON files)
events = [
    {
        "name": "Workshop de IA",
        "duration": 3,
        "preferred_start": 9,
        "participants": 80
    },
    {
        "name": "Palestra sobre Cloud",
        "duration": 2,
        "preferred_start": 10,
        "participants": 40
    },
    {
        "name": "Sessão de Networking",
        "duration": 1,
        "preferred_start": 12,
        "participants": 60
    },
    {
        "name": "Treinamento DevOps",
        "duration": 4,
        "preferred_start": 14,
        "participants": 120
    },
    {
        "name": "Startups",
        "duration": 2,
        "preferred_start": 16,
        "participants": 100
    }
]

rooms = [
    {
        "name": "Sala A",
        "capacity": 150,
        "availability": [(9,12), (14,18)]
    },
    {
        "name": "Sala B",
        "capacity": 80,
        "availability": [(9,12), (13,17)]
    },
    {
        "name": "Sala C",
        "capacity": 50,
        "availability": [(9,17)]
    },
    {
        "name": "Sala D",
        "capacity": 100,
        "availability": [(10,13), (15,17)]
    }
]

# Time slots from 9 to 17 hours
time_slots = list(range(9, 18))

# Build room availability time slots
room_availability = {}
for room in rooms:
    available_times = set()
    for (start, end) in room['availability']:
        available_times.update(range(start, end))
    room_availability[room['name']] = available_times

# Build event occupied time slots
event_times = {}
for event in events:
    start = event['preferred_start']
    duration = event['duration']
    occupied_times = set(range(start, start + duration))
    event_times[event['name']] = occupied_times

# Build possible allocations x_{e,r}
allocation_vars = {}
for event in events:
    for room in rooms:
        # Check capacity
        if event['participants'] <= room['capacity']:
            # Check availability
            event_time = event_times[event['name']]
            room_time = room_availability[room['name']]
            if event_time.issubset(room_time):
                var_name = f"x_{event['name']}_{room['name']}"
                allocation_vars[(event['name'], room['name'])] = pulp.LpVariable(var_name, cat='Binary')

# Initialize the problem
prob = pulp.LpProblem("Event_Scheduling", pulp.LpMinimize)

# Objective function: Minimize total unused capacity
prob += pulp.lpSum([
    allocation_vars[(e['name'], r['name'])] * (r['capacity'] - e['participants'])
    for e in events for r in rooms if (e['name'], r['name']) in allocation_vars
])

# Constraint 1: Each event is assigned to exactly one room
for event in events:
    prob += pulp.lpSum([
        allocation_vars[(event['name'], room['name'])]
        for room in rooms if (event['name'], room['name']) in allocation_vars
    ]) == 1, f"Event_{event['name']}_assignment"

# Constraint 2: No overlapping events in the same room
for room in rooms:
    for t in time_slots:
        overlapping_events = []
        for event in events:
            if t in event_times[event['name']] and (event['name'], room['name']) in allocation_vars:
                overlapping_events.append(allocation_vars[(event['name'], room['name'])])
        if overlapping_events:
            prob += pulp.lpSum(overlapping_events) <= 1, f"Room_{room['name']}_time_{t}"

# Solve the problem
prob.solve()

# Output the results
allocation_results = []
for (event_name, room_name), var in allocation_vars.items():
    if var.varValue == 1:
        allocation_results.append({
            'Event': event_name,
            'Room': room_name,
            'Start_Time': next(e['preferred_start'] for e in events if e['name'] == event_name)
        })

# Display the allocation
allocation_df = pd.DataFrame(allocation_results)
print(allocation_df)

# Optionally, generate a Gantt chart to visualize the schedule
fig, ax = plt.subplots(figsize=(10, 6))

# Colors for events
colors = plt.cm.tab20.colors
color_map = {event['name']: colors[i % len(colors)] for i, event in enumerate(events)}

for allocation in allocation_results:
    event_name = allocation['Event']
    room_name = allocation['Room']
    start_time = allocation['Start_Time']
    duration = next(e['duration'] for e in events if e['name'] == event_name)
    ax.barh(room_name, duration, left=start_time, color=color_map[event_name], edgecolor='black')
    ax.text(start_time + duration / 2, room_name, event_name, va='center', ha='center', color='black')

ax.set_xlabel('Time')
ax.set_ylabel('Rooms')
ax.set_title('Event Schedule')
ax.set_xticks(time_slots)
ax.set_xticklabels([f"{t}h" for t in time_slots])
plt.tight_layout()
plt.show()
