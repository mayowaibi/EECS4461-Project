from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid
from agents import SchellingAgent  
import random

class Echochamber(Model):
    """Model class for the YouTube Echo Chamber model."""

    def __init__(
        self,
        height: int = 20,
        width: int = 20,
        density: float = 0.8,
        human_homophily: float = 0.4,
        ai_homophily: float = 0.4,
        human_engagement: float = 0.5,
        ai_engagement: float = 0.5,
        ai_ratio: float = 0.5,
        radius: int = 1,
        seed=None,
    ):
        super().__init__(seed=seed)

        # Model parameters
        self.height = height
        self.width = width
        self.density = density
        self.human_homophily = human_homophily
        self.ai_homophily = ai_homophily
        self.human_engagement = human_engagement
        self.ai_engagement = ai_engagement
        self.ai_ratio = ai_ratio
        self.radius = radius

        # Initialize grid
        self.grid = SingleGrid(width, height, torus=True)
        self.agent_list = [] 

        # Track happiness
        self.happy = 0

        # Track bot clusters
        self.bot_clusters = {}

        # Set up data collection
        self.datacollector = DataCollector(
            model_reporters={
                "happy": lambda m: m.happy / len(m.agent_list) if len(m.agent_list) > 0 else 0,  
                "ai_cluster_pct": lambda m: (
                    sum(1 for a in m.agent_list if a.type == 1 and a.bot_cluster_size > 1) / len(m.agent_list) * 100
                    if len(m.agent_list) > 0 else 0
                ),
                "avg_human_engagement": lambda m: (
                    sum(a.engagement_rate for a in m.agent_list if a.type == 0) / len(m.agent_list)
                    if len(m.agent_list) > 0 else 0
                ),
                "avg_ai_engagement": lambda m: (
                    sum(a.engagement_rate for a in m.agent_list if a.type == 1) / len(m.agent_list)
                    if len(m.agent_list) > 0 else 0
                ),
            },
            agent_reporters={
                "agent_type": lambda a: "AI" if a.type == 1 else "Human",
                "content_preference": "preference",
                "engagement": "engagement_rate",
                "bot_cluster_size": "bot_cluster_size",
            },
        )

        # Create agents and place them on the grid
        for _, pos in self.grid.coord_iter():
            if random.random() < self.density:
                is_ai = random.random() < self.ai_ratio  # AI ratio control
                preference = random.choice([0, 1, 2])  # Video Games, Sports, Politics
                engagement = (
                    random.uniform(0.5, 1.0) * ai_engagement if is_ai else random.uniform(0.2, 1.0) * human_engagement
                )
                
                agent = SchellingAgent(
                    model=self,
                    agent_type=1 if is_ai else 0,  # AI = 1, Human = 0
                    content_preference=preference,
                    base_homophily=ai_homophily if is_ai else human_homophily,
                    engagement_rate=engagement,
                )
                
                self.grid.place_agent(agent, pos)
                self.agent_list.append(agent)  

        # Collect initial state
        self.datacollector.collect(self)

    def step(self):
        """Run one step of the model."""
        self.happy = 0  # Reset counter of happy agents
        
        # Manual agent activation (since no scheduler)
        for agent in self.agent_list:  
            agent.step()

        self.datacollector.collect(self)  # Collect data
        self.running = self.happy < len(self.agent_list)  