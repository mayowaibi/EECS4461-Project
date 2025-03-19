import solara
import numpy as np
import matplotlib.pyplot as plt
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
        "marker": "o" if agent.type == 0 else ("s" if agent.type == 1 else "^"),  # Humans: Circles, Bots: Squares, AI: Triangles
        "size": 10 + (agent.engagement_rate * 5),  
        "alpha": min(1.0, 0.5 + agent.amplification_power * 0.4),  # Bots with more influence are more visible
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
#EngagementPlot = make_plot_component({"Engagement": "tab:orange"})  # Engagement trends (waiting for model.py update)

# Heatmap Function (Can be removed if we decide not to implement this feature in model.py) 
# def overlay_heatmap(agent_grid, model):
#    """Overlays AI influence as a heatmap directly on the agent grid."""
#    if hasattr(model, "ai_influence_map"):
#        data = np.array(model.ai_influence_map)  
#        fig, ax = plt.subplots()
#        ax.imshow(data, cmap="hot", alpha=0.5, interpolation="nearest")  
#        ax.set_xticks([])
#        ax.set_yticks([])
#        return fig  
#    return None


# --- Placeholder for Recommendation Algorithm (Waiting on agents.py update) ---


# Create Solara Visualization
page = SolaraViz(
    create_model(),  # Use function instead of direct initialization
    components=[
        make_space_component(agent_portrayal),  
        # overlay_heatmap,  # Heatmap overlaying agent grid (can be removed if we chose not to implement)  
        HappyPlot,
        AIClusterPlot,
        #EngagementPlot,  # Engagement trends (waiting for model.py update)
    ],
    model_params=model_params,
)

if __name__ == "__main__":
    page
  