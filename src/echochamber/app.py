import solara
from mesa.visualization import (
    Slider,
    SolaraViz,
    make_plot_component,
    make_space_component,
)
from model import EchoChamber
from agents import EchoChamberAgent  


# Create model instance 
def create_model():
    return EchoChamber(
        width=20,
        height=20,
        density=0.8,
        human_homophily=0.4,
        ai_homophily=0.4,
        human_engagement=0.5,
        ai_engagement=0.5,
        ai_ratio=0.5
    )


# Agent portrayal function for grid visualization
def agent_portrayal(agent: EchoChamberAgent):
    content_colors = {0: "tab:orange", 1: "tab:blue", 2: "tab:red"}  
    portrayal = {
        "color": content_colors.get(agent.preference, "gray"),
        "marker": "o" if agent.type == 0 else ("s" if agent.type == 1 else "^"),  # 0: Human, 1: Bot, 2: Algorithm
        "size": 10 + (agent.engagement_rate * 5),
        "alpha": min(1.0, 0.5 + agent.amplification_power * 0.4),  # Optional: adjust for influence visibility
    }
    return portrayal


# UI controls
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


# Visualization outputs
HappyPlot = make_plot_component({"Happy Agents": "tab:green"})
AIClusterPlot = make_plot_component({"AI Cluster Percentage": "tab:purple"})

# Placeholder for new required plots
# InfluenceLearningPlot = make_plot_component({"Learning/Influence Progress": "tab:blue"})
# EchoStrengthPlot = make_plot_component({"Echo Chamber Strength": "tab:orange"})


# Interface layout
page = SolaraViz(
    create_model(),
    components=[
        make_space_component(agent_portrayal),
        HappyPlot,
        AIClusterPlot,
        # InfluenceLearningPlot,
        # EchoStrengthPlot,
    ],
    model_params=model_params,
)

if __name__ == "__main__":
    page
  