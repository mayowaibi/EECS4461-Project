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
        human_engagement=0.5, ai_engagement=0.5, ai_ratio=0.5,
        recsys_ratio=0.3  # Added: control ratio of recommendation algorithms to social bots
    )

# Agent Portrayal Function 
def agent_portrayal(agent: EchoChamberAgent):
    """Defines how agents are displayed in the visualization based on content preference."""
    content_colors = {0: "tab:orange", 1: "tab:blue", 2: "tab:red"}  
    portrayal = {
        "color": content_colors.get(agent.preference, "gray"),
        "marker": ("o" if agent.type == 0 else  # Human
                  "s" if (agent.type == 1 and agent.ai_subtype == 0) else  # Social Bot
                  "^"),  # Recommendation Algorithm
        "size": 10 + (agent.engagement_rate * 5),
        "alpha": min(1.0, 0.5 + (agent.network_influence * 0.5)),
    }
    
    # Add visual indicators for recommendation algorithms
    if agent.type == 1 and agent.ai_subtype == 1:
        portrayal["size"] += agent.recommendation_strength * 2
        portrayal["alpha"] = min(1.0, 0.5 + agent.success_rate)
    
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
    "recsys_ratio": Slider("Recommendation Algorithm Ratio", 0.3, 0.0, 1.0, 0.1),
    "width": 20,
    "height": 20,
}

# Visualization components
NetworkPlot = make_plot_component({
    "Average Connection Strength": "tab:purple",
    "Network Density": "tab:red"
})

RecommendationPlot = make_plot_component({
    "Recommendation Success Rate": "tab:green",
    "Average Recommendation Strength": "tab:blue"
})

EchoChamberPlot = make_plot_component({
    "Happy Agents %": "tab:green",
    "AI Cluster %": "tab:purple"
})

EchoChamberStrengthPlot = make_plot_component({
    "Echo Chamber Strength": "tab:red"
})

EngagementPlot = make_plot_component({
    "Total Likes": "tab:cyan",
    "Total Comments": "tab:blue",
    "Total Shares": "tab:purple"
})

# Create visualization
page = SolaraViz(
    create_model(),
    components=[
        make_space_component(agent_portrayal),
        NetworkPlot,
        RecommendationPlot,
        EchoChamberPlot,
        EchoChamberStrengthPlot,
        EngagementPlot
    ],
    model_params=model_params,
)

if __name__ == "__main__":
    page
  