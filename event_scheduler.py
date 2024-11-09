import json
import pulp

def main():
    # Load events from JSON file
    with open('events.json', 'r') as f:
        events = json.load(f)
    
    # Load rooms from JSON file
    with open('rooms.json', 'r') as f:
        rooms = json.load(f)
    
    # Prepare data structures
    event_names = [event['name'] for event in events]
    room_names = [room['name'] for room in rooms]
    time_slots = list(range(9, 18))  # Time slots from 9h to 17h inclusive

    # Create dictionaries for quick access
    event_dict = {event['name']: event for event in events}
    room_dict = {room['name']: room for room in rooms}

    # Initialize the optimization model
    model = pulp.LpProblem("Event_Scheduling_Problem", pulp.LpMinimize)

    # Decision variables: x[e][r][s] = 1 if event e is scheduled in room r starting at time s
    x = {}
    for e in event_names:
        x[e] = {}
        for r in room_names:
            x[e][r] = {}
            for s in time_slots:
                x[e][r][s] = pulp.LpVariable(f"x_{e}_{r}_{s}", cat='Binary')

    # Objective function: Minimize total deviation from preferred start times
    model += pulp.lpSum([
        x[e][r][s] * abs(s - event_dict[e]['preferred_start'])
        for e in event_names
        for r in room_names
        for s in time_slots
    ])

    # Constraints

    # Each event must be scheduled exactly once
    for e in event_names:
        model += pulp.lpSum([
            x[e][r][s]
            for r in room_names
            for s in time_slots
        ]) == 1, f"Event_{e}_Scheduled_Once"

    # Room capacity constraints
    for e in event_names:
        participants = event_dict[e]['participants']
        for r in room_names:
            capacity = room_dict[r]['capacity']
            if capacity < participants:
                # Room cannot accommodate the event due to insufficient capacity
                for s in time_slots:
                    model += x[e][r][s] == 0, f"Capacity_{e}_{r}_{s}"

    # Room availability constraints
    for e in event_names:
        duration = event_dict[e]['duration']
        for r in room_names:
            availability = room_dict[r]['availability']
            available_starts = []
            for period in availability:
                start_time = period[0]
                end_time = period[1]
                # Possible start times within this availability period
                for s in range(start_time, end_time - duration + 1):
                    if s in time_slots:
                        available_starts.append(s)
            # Enforce that events can only start at available times
            for s in time_slots:
                if s not in available_starts:
                    model += x[e][r][s] == 0, f"Availability_{e}_{r}_{s}"

    # No overlapping events in the same room
    for r in room_names:
        for t in time_slots:
            model += pulp.lpSum([
                x[e][r][s]
                for e in event_names
                for s in time_slots
                if t >= s and t < s + event_dict[e]['duration']
            ]) <= 1, f"NonOverlap_{r}_{t}"

    # Solve the optimization problem
    solver = pulp.PULP_CBC_CMD()
    result_status = model.solve(solver)

    # Check if an optimal solution was found
    if result_status != pulp.LpStatusOptimal:
        print("No optimal solution found.")
        return

    # Extract and display the schedule
    schedule = []
    for e in event_names:
        for r in room_names:
            for s in time_slots:
                if pulp.value(x[e][r][s]) == 1:
                    event_info = {
                        'event': e,
                        'room': r,
                        'start_time': s,
                        'end_time': s + event_dict[e]['duration'],
                        'participants': event_dict[e]['participants']
                    }
                    schedule.append(event_info)

    # Print the optimal schedule
    print("Optimal Schedule:")
    for event in schedule:
        print(f"Event: {event['event']}")
        print(f"  Room: {event['room']}")
        print(f"  Time: {event['start_time']}h to {event['end_time']}h")
        print(f"  Participants: {event['participants']}\n")

if __name__ == "__main__":
    main()
