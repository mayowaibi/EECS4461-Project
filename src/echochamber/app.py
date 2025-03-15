import solara
from mesa.visualization import (
    Slider,
    SolaraViz,
    make_plot_component,
    make_space_component,
)
from model import EchoChamber  
from agents import EchoChamberAgent  

# Function to create a new model instance when needed
def create_model():
    return EchoChamber(
        width=20, height=20, density=0.8, 
        human_homophily=0.4, ai_homophily=0.4, 
        human_engagement=0.5, ai_engagement=0.5, ai_ratio=0.5
    )

# Agent Portrayal Function 
def agent_portrayal(agent: EchoChamberAgent):
    """Defines how agents are displayed in the visualization based on content preference."""
    content_colors = {0: "tab:orange", 1: "tab:blue", 2: "tab:red"}  
    portrayal = {
        "color": content_colors.get(agent.preference, "gray"),  
        "marker": "o" if agent.type == 0 else ("^" if agent.bot_cluster_size > 1 else "s"),  
        "size": 10 + (agent.engagement_rate * 5),  
        "alpha": min(1.0, 0.5 + agent.amplification_power * 0.2),  # Bots with more influence are more visible
    }
    return portrayal

# Define UI Control Sliders 
model_params = {
    "seed": {"type": "InputText", "value": 42, "label": "Random Seed"},
    "density": Slider("Agent Density", 0.8, 0.1, 1.0, 0.1),
    "human_homophily": Slider("Human Homophily", 0.4, 0.0, 1.0, 0.1),
    "ai_homophily": Slider("AI Homophily", 0.4, 0.0, 1.0, 0.1),
    "human_engagement": Slider("Human Engagement", 0.5, 0.0, 1.0, 0.1),
    "ai_engagement": Slider("AI Engagement", 0.5, 0.0, 1.0, 0.1),
    "ai_ratio": Slider("AI Population Ratio", 0.5, 0.0, 1.0, 0.1),
    "width": 20,
    "height": 20,
}

# Visualization Components
HappyPlot = make_plot_component({"Happy Agents": "tab:green"})  
AIClusterPlot = make_plot_component({"AI Cluster Percentage": "tab:purple"})  

# Create Solara Visualization
page = SolaraViz(
    create_model(),  # Use function instead of direct initialization
    components=[
        make_space_component(agent_portrayal),  
        HappyPlot,
        AIClusterPlot,  
    ],
    model_params=model_params,
)

if __name__ == "__main__":
    page
  