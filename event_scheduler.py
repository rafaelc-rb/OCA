"""
Event Scheduler Module

This module provides functionality to schedule events optimally based on
constraints such as room capacity, availability, and event preferences.
It uses linear programming for optimization and generates a visual Gantt chart
to illustrate the schedule.
"""

import json
import pulp
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def load_data():
    """
    Load events and rooms data from JSON files.

    Returns:
        tuple: A tuple containing two lists:
            - events (list): A list of event dictionaries loaded from 'events.json'.
            - rooms (list): A list of room dictionaries loaded from 'rooms.json'.

    Raises:
        FileNotFoundError: If 'events.json' or 'rooms.json' files are not found.
        json.JSONDecodeError: If the JSON files contain invalid JSON.
    """
    with open('events.json', 'r') as f:
        events = json.load(f)
    with open('rooms.json', 'r') as f:
        rooms = json.load(f)
    return events, rooms

def prepare_data_structures(events, rooms):
    """
    Prepare necessary data structures for the optimization model.

    Args:
        events (list): List of event dictionaries.
        rooms (list): List of room dictionaries.

    Returns:
        tuple: Contains prepared data structures:
            - event_names (list): List of event names.
            - room_names (list): List of room names.
            - time_slots (list): List of available time slots.
            - event_dict (dict): Dictionary mapping event names to event data.
            - room_dict (dict): Dictionary mapping room names to room data.
    """
    event_names = [event['name'] for event in events]
    room_names = [room['name'] for room in rooms]
    time_slots = list(range(9, 18))  # Time slots from 9h to 17h inclusive
    event_dict = {event['name']: event for event in events}
    room_dict = {room['name']: room for room in rooms}
    return event_names, room_names, time_slots, event_dict, room_dict

def create_decision_variables(event_names, room_names, time_slots):
    """
    Create decision variables for the optimization model.

    Args:
        event_names (list): List of event names.
        room_names (list): List of room names.
        time_slots (list): List of available time slots.

    Returns:
        dict: Nested dictionary of decision variables x[e][r][s],
              where x[e][r][s] = 1 if event e is scheduled in room r at time s.
    """
    x = {}
    for e in event_names:
        x[e] = {}
        for r in room_names:
            x[e][r] = {}
            for s in time_slots:
                x[e][r][s] = pulp.LpVariable(f"x_{e}_{r}_{s}", cat='Binary')
    return x

def define_objective_function(model, x, event_dict, event_names, room_names, time_slots):
    """
    Define the objective function for the optimization model.

    The objective is to minimize the total deviation from preferred start times.

    Args:
        model (pulp.LpProblem): The optimization model.
        x (dict): Decision variables.
        event_dict (dict): Dictionary mapping event names to event data.
        event_names (list): List of event names.
        room_names (list): List of room names.
        time_slots (list): List of available time slots.
    """
    model += pulp.lpSum([
        x[e][r][s] * abs(s - event_dict[e]['preferred_start'])
        for e in event_names
        for r in room_names
        for s in time_slots
    ])

def add_constraints(model, x, event_dict, room_dict, event_names, room_names, time_slots):
    """
    Add constraints to the optimization model.

    Constraints include:
    - Each event must be scheduled exactly once.
    - Room capacity must be sufficient for the event.
    - Events must be scheduled within room availability.
    - No overlapping events in the same room.

    Args:
        model (pulp.LpProblem): The optimization model.
        x (dict): Decision variables.
        event_dict (dict): Dictionary mapping event names to event data.
        room_dict (dict): Dictionary mapping room names to room data.
        event_names (list): List of event names.
        room_names (list): List of room names.
        time_slots (list): List of available time slots.
    """
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
                for s in time_slots:
                    model += x[e][r][s] == 0, f"Capacity_{e}_{r}_{s}"

    # Room availability constraints
    for e in event_names:
        duration = event_dict[e]['duration']
        for r in room_names:
            availability = room_dict[r]['availability']
            available_starts = []
            for period in availability:
                start_time, end_time = period
                for s in range(start_time, end_time - duration + 1):
                    if s in time_slots:
                        available_starts.append(s)
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

def solve_model(model):
    """
    Solve the optimization model.

    Args:
        model (pulp.LpProblem): The optimization model to solve.

    Returns:
        int: The status of the solution (e.g., pulp.LpStatusOptimal).
    """
    solver = pulp.PULP_CBC_CMD(msg=False)
    result_status = model.solve(solver)
    return result_status

def extract_schedule(x, event_dict, event_names, room_names, time_slots):
    """
    Extract the schedule from the optimization model solution.

    Args:
        x (dict): Decision variables.
        event_dict (dict): Dictionary mapping event names to event data.
        event_names (list): List of event names.
        room_names (list): List of room names.
        time_slots (list): List of available time slots.

    Returns:
        list: List of dictionaries containing scheduled event information.
    """
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
    return schedule

def print_schedule(schedule):
    """
    Print the optimal schedule to the console.

    Args:
        schedule (list): List of scheduled events to print.
    """
    print("Optimal Schedule:")
    for event in schedule:
        print(f"Event: {event['event']}")
        print(f"  Room: {event['room']}")
        print(f"  Time: {event['start_time']}h to {event['end_time']}h")
        print(f"  Participants: {event['participants']}\n")

def generate_gantt_chart(schedule, room_names):
    """
    Generate a Gantt chart illustrating the schedule.

    Args:
        schedule (list): List of scheduled events.
        room_names (list): List of room names.

    Displays:
        A matplotlib plot showing the Gantt chart of the schedule.
    """
    # Assign colors to events
    colors = plt.cm.tab20.colors
    event_colors = {event['event']: colors[i % len(colors)] for i, event in enumerate(schedule)}
    
    fig, ax = plt.subplots(figsize=(12, 6))

    # Create a mapping from rooms to y positions
    room_positions = {room: i for i, room in enumerate(room_names)}
    y_ticks = []
    y_labels = []

    for event in schedule:
        room = event['room']
        start = event['start_time']
        end = event['end_time']
        y_pos = room_positions[room]
        ax.barh(y_pos, end - start, left=start, height=0.4, color=event_colors[event['event']], edgecolor='black')
        ax.text(start + (end - start)/2, y_pos, event['event'], va='center', ha='center', color='white', fontsize=9)
        if room not in y_labels:
            y_ticks.append(y_pos)
            y_labels.append(room)

    ax.set_yticks(list(room_positions.values()))
    ax.set_yticklabels(room_names)
    ax.set_xlabel('Time (h)')
    ax.set_ylabel('Rooms')
    ax.set_title('Event Schedule Gantt Chart')
    ax.set_xlim(9, 18)
    ax.set_xticks(range(9, 19))
    ax.grid(True, axis='x', linestyle='--', alpha=0.7)

    plt.tight_layout()
    plt.show()

def main():
    """
    Main function to execute the event scheduling optimization and visualization.

    Steps:
    - Load data from JSON files.
    - Prepare data structures for optimization.
    - Initialize the optimization model.
    - Create decision variables.
    - Define the objective function.
    - Add constraints to the model.
    - Solve the model.
    - Extract and display the schedule.
    - Generate and display the Gantt chart.
    """
    # Load data
    events, rooms = load_data()
    
    # Prepare data structures
    event_names, room_names, time_slots, event_dict, room_dict = prepare_data_structures(events, rooms)
    
    # Initialize the optimization model
    model = pulp.LpProblem("Event_Scheduling_Problem", pulp.LpMinimize)
    
    # Create decision variables
    x = create_decision_variables(event_names, room_names, time_slots)
    
    # Define the objective function
    define_objective_function(model, x, event_dict, event_names, room_names, time_slots)
    
    # Add constraints
    add_constraints(model, x, event_dict, room_dict, event_names, room_names, time_slots)
    
    # Solve the optimization problem
    result_status = solve_model(model)
    
    # Check if an optimal solution was found
    if result_status != pulp.LpStatusOptimal:
        print("No optimal solution found.")
        return
    
    # Extract and display the schedule
    schedule = extract_schedule(x, event_dict, event_names, room_names, time_slots)
    print_schedule(schedule)
    
    # Generate and display the Gantt chart
    generate_gantt_chart(schedule, room_names)

if __name__ == "__main__":
    main()
