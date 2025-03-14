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
        max_steps: int = 100,
        seed=None,
    ):
        """
        Args:
            width: Width of the grid
            height: Height of the grid
            density: Initial chance for a cell to be populated (0-1)
            human_homophily: How similar human neighbors must be to be happy
            ai_homophily: How similar AI neighbors must be to be happy
            human_engagement: How likely a human agent is to engage with a video
            ai_engagement: How likely an AI agent is to engage with a video
            ai_ratio: Fraction of agents that are AI
            radius: Search radius for checking neighbor similarity
            seed: Seed for reproducibility
        """
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

        # Step counter
        self.max_steps = max_steps
        self.step_count = 0

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
                "total_human_engagement": lambda m: (
                    sum(a.likes + a.comments + a.shares for a in m.agent_list if a.type == 0)
                ),
                "total_ai_engagement": lambda m: (
                    sum(a.likes + a.comments + a.shares for a in m.agent_list if a.type == 1)
                ),
            },
            # Will be used as improvement for DEL 4 (To be deleted)
            agent_reporters={
                "agent_type": lambda a: "AI" if a.type == 1 else "Human",
                "content_preference": "content_preference",
                "engagement_rate": "engagement_rate",
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
        
        # Random agent activation
        agents_to_activate = self.agent_list.copy()
        random.shuffle(agents_to_activate)

        for agent in agents_to_activate:  
            agent.step()

        self.datacollector.collect(self)  # Collect data
        self.step_count += 1

        # Run model until all agents are happy or max_steps reached
        self.running = self.happy < len(self.agent_list) and self.step_count < self.max_steps