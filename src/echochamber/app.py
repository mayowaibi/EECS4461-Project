import solara
import matplotlib.pyplot as plt
import pandas as pd
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
def DisplayModelInfo(model):
    # Count agent types
    human_count = sum(1 for a in model.agent_list if a.type == 0)
    bot_count = sum(1 for a in model.agent_list if a.type == 1 and a.ai_subtype == 0)
    recsys_count = sum(1 for a in model.agent_list if a.type == 1 and a.ai_subtype == 1)

    markdown_text = f"""
    ## 🧠 **Model Legend**

    <table style="width:100%; border-collapse:collapse;">
        <thead>
            <tr>
                <th style="font-size: 18px; text-align:left; padding: 6px; border-bottom: 2px solid #ccc;">👥 Agent Type (Shape)</th>
                <th style="font-size: 18px; text-align:left; padding: 6px; border-bottom: 2px solid #ccc;">🎬 Content Preference (Color)</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="font-size: 15px; padding: 6px; text-align:left"><strong>Human Agent</strong> <span style="font-family:monospace;">(●)</span></td>
                <td style="font-size: 15px; padding: 6px; text-align:left"><strong>Video Games</strong> <span style="color:orange; font-weight:bold;">(Orange)</span></td>
            </tr>
            <tr>
                <td style="font-size: 15px; padding: 6px; text-align:left"><strong>Social Bot</strong> <span style="font-family:monospace;">(■)</span></td>
                <td style="font-size: 15px; padding: 6px; text-align:left"><strong>Sports</strong> <span style="color:blue; font-weight:bold;">(Blue)</span></td>
            </tr>
            <tr>
                <td style="font-size: 15px; padding: 6px; text-align:left"><strong>Recommendation Algorithm</strong> <span style="font-family:monospace;">(▲)</span></td>
                <td style="font-size: 15px; padding: 6px; text-align:left"><strong>Politics</strong> <span style="color:red; font-weight:bold;">(Red)</span></td>
            </tr>
        </tbody>
    </table>

    ### 📊 **Agent Counts**
    
    <span style="font-size: 15px;">👥 <strong>Total Human User Agents:</strong> {human_count}</span><br>
    <span style="font-size: 15px;">🤖 <strong>Total Social Bot Agents:</strong> {bot_count}</span><br>
    <span style="font-size: 15px;">📡 <strong>Total Recommendation Algorithm Agents:</strong> {recsys_count}</span><br>
    """
    return solara.Markdown(markdown_text)

NetworkPlot = make_plot_component({
    "Average Connection Strength": "tab:purple",
    "Network Density": "tab:red"
})

RecommendationPlot = make_plot_component({
    "Recommendation Influence Reach": "tab:orange",
    "Average Recommendation Strength": "tab:blue",
    "Recommendation Success Rate": "tab:green"
})

EchoChamberPlot = make_plot_component({
    "Happy Agents %": "tab:green",
    "Social Bot Cluster %": "tab:purple",
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
        DisplayModelInfo,
        EchoChamberPlot,
        RecommendationPlot,
        NetworkPlot,
        EngagementPlot,
    ],
    model_params=model_params,
)

if __name__ == "__main__":
    page
  