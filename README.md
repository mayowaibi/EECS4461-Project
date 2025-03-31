# YouTube's Silent Echo
EECS 4461 W25 Team 13 

## §A. Overview of Phenomenon Modeled

Our simulation models the emergence of echo chambers on YouTube, where users are increasingly exposed to ideologically similar content due to reinforcement by both social bots and algorithmic recommendation systems. This phenomenon is driven by selective exposure, where individuals prefer interacting with like-minded content, and by AI agents that amplify or personalize content based on user behavior and engagement patterns.

The simulation captures:
- How human users cluster ideologically when influenced by homophily, social signals, and content engagement
- How social bots reinforce echo chambers by artificially amplifying preferred content within clusters
- How recommendation algorithms adapt to both user behavior and bot influence to personalize content suggestions
- The emergent feedback loops between agents that lead to polarization and reduced exposure to diverse viewpoints over time
- Key dynamics underlying real-world phenomena like filter bubbles and algorithmic bias in digital media platforms

Our simulation was implemented in an agent-based modelling framework using the Python Mesa library.

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

## §C. Key Findings/Observations
- AI amplification accelerates echo chamber formation
- User satisfaction doesn't always converge
- Basic engagement metrics (likes, comments, shares) can drive complex patterns
- Recommendations adapt to and amplify bias
- Our simulation can inform real-world design
