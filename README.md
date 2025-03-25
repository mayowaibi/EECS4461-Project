# YouTube's Silent Echo
EECS 4461 W25 Team 13 

## §A. Overview of Current Implementation State

Our simulation models the formation of echo chambers on YouTube by representing human users, social bots, and YouTube’s recommendation algorithm as agents in an agent-based modelling framework using the Mesa library. The system implements an interaction model where agents possess multiple attributes that influence their behaviour and impact on the environment.

The current implementation includes:
- Simulation of interactions between human and social bot agents
- Adjustment of model parameters before running the simulation
- Tracking of echo chamber formation
- Visualization of simulation trends over time 

## §B. How to Run the Simulation

### Installation Steps
1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
1. Navigate to the src directory:
   ```bash
   cd src/echochamber
   ```
2. Start the application:
   ```bash
   solara run app.py
   ```
3. Go to the displayed local URL using your browser (usually http://127.0.0.1:8765)
4. Run the simulation

## §C. Limitations and Planned Improvements
### Limitations
- Stopping condition based on a set step limit
- Lack of engagement metrics
- Lack of YouTube Recommendation Algorithm as a simulation entity

### Planned Improvements
- Implementation of a dynamic stopping condition
- Improved overall data collection and metrics
- Addition of YouTube Recommendation Algorithm as an agent
