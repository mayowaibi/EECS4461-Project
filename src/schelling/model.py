from mesa import Model
from mesa.datacollection import DataCollector
from mesa.examples.basic.schelling.agents import SchellingAgent
from mesa.space import SingleGrid


class Echochamber(Model):
    """Model class for the YouTube Echochamber model."""

    def __init__(
        self,
        height: int = 20,
        width: int = 20,
        density: float = 0.8,
        minority_pct: float = 0.5,
        human_homophily: float = 0.4,
        ai_homophily: float = 0.4,
        human_engagement: float = 0.5,
        ai_engagement: float = 0.5,
        ai_ratio: float = 0.5,
        radius: int = 1,
        seed=None,
    ):
        """
        Args:
            width: Width of the grid
            height: Height of the grid
            density: Initial chance for a cell to be populated (0-1)
            minority_pct: Chance for an agent to be in minority class (0-1)
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
        self.minority_pct = minority_pct
        self.human_homophily = human_homophily
        self.ai_homophily = ai_homophily
        self.human_engagement = human_engagement
        self.ai_engagement = ai_engagement
        self.ai_ratio = ai_ratio
        self.radius = radius

        # Initialize grid
        self.grid = SingleGrid(width, height, torus=True)
        self.agents = []

        # Track happiness
        self.happy = 0

        # Set up data collection
        self.datacollector = DataCollector(
            model_reporters={
                "happy": lambda m: m.happy / len(m.agents) if len(m.agents) > 0 else 0,
                "ai_cluster_pct": lambda m: (
                    sum(1 for a in m.agents if isinstance(a, AI_Agent) and a.is_clustered) / len(m.agents) * 100
                    if len(m.agents) > 0 else 0
                ),
                "avg_human_engagement": lambda m: (
                    sum(a.engagement for a in m.agents if isinstance(a, Human_Agent)) / len(m.agents)
                    if len(m.agents) > 0 else 0
                ),
                "avg_ai_engagement": lambda m: (
                    sum(a.engagement for a in m.agents if isinstance(a, AI_Agent)) / len(m.agents)
                    if len(m.agents) > 0 else 0
                ),
                "cross_type_interactions": lambda m: (
                    sum(a.cross_interactions for a in m.agents) / len(m.agents)
                    if len(m.agents) > 0 else 0
                ),
            },
            agent_reporters={
                "agent_type": lambda a: "AI" if isinstance(a, AI_Agent) else "Human",
                "content_preference": "content_preference",
                "engagement": "engagement",
                "is_clustered": "is_clustered"
            },
        )

        # Create agents and place them on the grid
        for _, pos in self.grid.coord_iter():
            if random.random() < self.density:
                is_ai = random.random() > self.human_ai_ratio
                preference = random.choice([0, 1, 2])  # Video Games, Sports, Politics
                engagement = (
                    random.uniform(0.5, 1.0) * engagement_ai if is_ai else random.uniform(0.2, 1.0) * engagement_human
                )
                
                if is_ai:
                    agent = AIAgent(self, preference, engagement, ai_homophily)
                else:
                    agent = UserAgent(self, preference, engagement, human_homophily)
                
                self.grid.place_agent(agent, pos)
                self.agents.append(agent)

        # Collect initial state
        self.datacollector.collect(self)

    def step(self):
        """Run one step of the model."""
        self.happy = 0  # Reset counter of happy agents
        self.agents.shuffle_do("step")  # Activate all agents in random order
        self.datacollector.collect(self)  # Collect data
        self.running = self.happy < len(self.agents)  # Continue until everyone is happy
