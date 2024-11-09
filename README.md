# Event Scheduler Module

The **Event Scheduler Module** is a Python application that optimizes event scheduling based on constraints such as room capacity, availability, and event preferences. It leverages linear programming to find the optimal schedule and generates a visual Gantt chart to illustrate the result.

## Table of Contents

- [Event Scheduler Module](#event-scheduler-module)
  - [Table of Contents](#table-of-contents)
  - [Features](#features)
  - [Requirements](#requirements)
  - [Installation](#installation)
  - [Usage](#usage)
  - [Configuration](#configuration)
    - [events.json](#eventsjson)
    - [rooms.json](#roomsjson)
  - [Output](#output)
  - [Acknowledgments](#acknowledgments)
- [Contact](#contact)

## Features

- **Optimal Scheduling**: Uses linear programming to schedule events optimally.
- **Constraints Handling**: Considers room capacities, availabilities, and event preferences.
- **Visual Representation**: Generates a Gantt chart to visualize the event schedule.
- **Flexible Configuration**: Easily modify events and rooms through JSON files.

## Requirements

- Python 3.6 or higher
- [PuLP](https://coin-or.github.io/pulp/) library for linear programming
- [Matplotlib](https://matplotlib.org/) for generating the Gantt chart

## Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/rafaelc-rb/OCA.git
   ```

2. **Install Dependencies**

   It's recommended to use a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

   Install the required Python packages:

   ```bash
   pip install -r requirements.txt
   ```

   **Note**: If you don't have a `requirements.txt`, you can install the packages individually:

   ```bash
   pip install pulp matplotlib
   ```

## Usage

1. **Prepare the Data**

   Ensure that `events.json` and `rooms.json` are correctly configured with your events and rooms data.

2. **Run the Script**

   ```bash
   python event_scheduler.py
   ```

3. **View the Output**

   - The optimal schedule will be printed in the console.
   - A Gantt chart will be displayed illustrating the schedule.

## Configuration

### events.json

Define your events in `events.json`. Each event should have the following fields:

- `name`: The name of the event.
- `duration`: Duration of the event in hours.
- `preferred_start`: Preferred start time (hour).
- `participants`: Number of participants expected.

**Example**:

```json
[
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
```

### rooms.json

Define your rooms in `rooms.json`. Each room should have the following fields:

- `name`: The name of the room.
- `capacity`: Maximum capacity of the room.
- `availability`: A list of available time periods (start and end times).

**Example**:

```json
[
    {
        "name": "Sala A",
        "capacity": 150,
        "availability": [[10, 12], [14, 18]]
    },
    {
        "name": "Sala B",
        "capacity": 80,
        "availability": [[9, 12], [13, 17]]
    },
    {
        "name": "Sala C",
        "capacity": 50,
        "availability": [[9, 17]]
    },
    {
        "name": "Sala D",
        "capacity": 100,
        "availability": [[11, 13], [15, 17]]
    }
]
```

## Output

After running the script, you'll receive:

1. **Optimal Schedule in Console**:

   ```plaintext
   Optimal Schedule:
   Event: Workshop de IA
     Room: Sala B
     Time: 9h to 12h
     Participants: 80

   Event: Palestra sobre Cloud
     Room: Sala A
     Time: 10h to 12h
     Participants: 40

   Event: Sessão de Networking
     Room: Sala D
     Time: 11h to 12h
     Participants: 60

   Event: Treinamento DevOps
     Room: Sala A
     Time: 14h to 18h
     Participants: 120

   Event: Startups
     Room: Sala D
     Time: 15h to 17h
     Participants: 100
   ```

2. **Gantt Chart Visualization**:

   A Gantt chart will pop up showing the schedule across different rooms and times.

   ![Gantt Chart Example](gantt_chart_example.png)

## Acknowledgments

- [PuLP](https://coin-or.github.io/pulp/) for the optimization library.
- [Matplotlib](https://matplotlib.org/) for plotting the Gantt chart.
- Thanks to all contributors and the open-source community.

# Contact

For any inquiries or issues, please open an issue on the GitHub repository or contact rafaelcrd.ribeiro@gmail.com.
