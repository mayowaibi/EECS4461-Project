import solara
from mesa.visualization import (
    Slider,
    SolaraViz,
    make_plot_component,
    make_space_component,
)
from model import Echochamber  # Updated to match Isaac's model
from agents import UserAgent, AIAgent # Assuming that these will be implemented in agents.py

# Agent Portrayal Function 
def agent_portrayal(agent):
    """Defines how agents are displayed in the visualization based on content preference."""
    content_colors = {0: "tab:orange", 1: "tab:blue"}  # 0 = Orange, 1 = Blue
    portrayal = {
        "color": content_colors.get(agent.content_preference, "gray"),  # Ensure content preference drives color
        "marker": "o" if isinstance(agent, UserAgent) else "s",  # Humans = Circle, AI = Square
        "size": 10 + (agent.engagement * 5),  # Scale size based on engagement
        "text_color": "white",
    }
    return portrayal

# Defining UI Control Sliders 
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

# Initialize Model 
model = Echochamber(
    width=20, height=20, density=0.8, 
    human_homophily=0.4, ai_homophily=0.4, 
    human_engagement=0.5, ai_engagement=0.5, ai_ratio=0.5
)

# Visualization Components
HappyPlot = make_plot_component({"happy": "tab:green"})  # Tracks "happy" agents
EngagementPlot = make_plot_component({
    "avg_human_engagement": "tab:blue", 
    "avg_ai_engagement": "tab:red"
})  

AIClusterPlot = make_plot_component({"ai_cluster_pct": "tab:purple"})  # AI clustering metric

# Create Solara Visualization
page = SolaraViz(
    model,
    components=[
        make_space_component(agent_portrayal),  # Agent grid visualization
        HappyPlot,  # Happy agent count
        EngagementPlot,  # Engagement trend plot
        AIClusterPlot,  # AI Clustering visualization
    ],
    model_params=model_params,
)

if __name__ == "__main__":
    page  