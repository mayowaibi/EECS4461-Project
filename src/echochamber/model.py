from mesa import Model
from mesa.datacollection import DataCollector
from mesa.space import SingleGrid
from agents import EchoChamberAgent  
import random

class EchoChamber(Model):
    """Model class for the YouTube Echo chamber model."""

    def __init__(
        self,
        height=20,
        width=20,
        density=0.8,
        human_homophily=0.4,
        ai_homophily=0.4,
        human_engagement=0.5,
        ai_engagement=0.5,
        ai_ratio=0.5,
        recsys_ratio=0.3,
        radius=1,
        max_steps=100,
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
            recsys_ratio: Fraction of AI agents that are recommendation algorithms
            radius: Search radius for checking neighbor similarity
            max_steps: Maximum number of steps before simulation stops
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
        self.recsys_ratio = recsys_ratio
        self.radius = radius
        

        # Step counter
        self.max_steps = max_steps
        self.step_count = 0

        # Initialize grid
        self.grid = SingleGrid(width, height, torus=True)
        self.agent_list = [] 

        # Track happiness
        self.happy = 0

        # Create agents
        for _, pos in self.grid.coord_iter():
            if random.random() < self.density:
                is_ai = random.random() < self.ai_ratio # AI ratio control
                ai_subtype = None
                
                if is_ai:
                    # Determine if AI agent is recommendation algorithm or social bot
                    is_recsys = random.random() < self.recsys_ratio
                    ai_subtype = 1 if is_recsys else 0
                
                preference = random.choice([0, 1, 2]) # Video Games, Sports, Politics
                engagement = (
                    random.uniform(0.5, 1.0) * ai_engagement if is_ai
                    else random.uniform(0.2, 1.0) * human_engagement
                )
                
                agent = EchoChamberAgent(
                    model=self,
                    agent_type=1 if is_ai else 0,  # AI = 1, Human = 0
                    content_preference=preference,
                    base_homophily=ai_homophily if is_ai else human_homophily,
                    engagement_rate=engagement,
                    ai_subtype=ai_subtype,
                )
                
                self.grid.place_agent(agent, pos)
                self.agent_list.append(agent)  

        # Data collection
        self.datacollector = DataCollector(
            model_reporters={
                # Happy agents and cluster tracking
                "Happy Agents %": lambda m: (m.happy / len(m.agent_list)) * 100 if m.agent_list else 0,
                "AI Cluster %": lambda m: sum(
                    1 for a in m.agent_list 
                    if a.type == 1 and a.ai_subtype == 0 and a.bot_cluster_size > 1
                ) / len(m.agent_list) * 100 if m.agent_list else 0,
                
                # Network metrics
                "Average Connection Strength": self._get_avg_connection_strength,
                "Network Density": self._get_network_density,
                
                # Recommendation metrics
                "Recommendation Success Rate": self._get_recommendation_success_rate,
                "Average Recommendation Strength": self._get_avg_recommendation_strength,
                
                # Echo chamber metrics (now separate)
                "Echo Chamber Strength": self._get_echo_chamber_strength,
                
                # Engagement metrics
                "Total Likes": lambda m: sum(a.likes for a in m.agent_list),
                "Total Comments": lambda m: sum(a.comments for a in m.agent_list),
                "Total Shares": lambda m: sum(a.shares for a in m.agent_list),
            },
            agent_reporters={
                "Type": lambda a: "Human" if a.type == 0 else ("Bot" if a.ai_subtype == 0 else "RecSys"),
                "Preference": "preference",
                "Engagement": "engagement_rate",
                "Network Influence": "network_influence",
                "Echo Chamber Strength": "echo_chamber_strength",
                "Connection Count": lambda a: len(a.connections),
                "Bot Cluster Size": lambda a: a.bot_cluster_size if (a.type == 1 and a.ai_subtype == 0) else 0,
                "Is Happy": lambda a: a.current_homophily <= a.echo_chamber_strength,
            }
        )

        # Collect initial state
        self.datacollector.collect(self)

    def _get_type_percentage(self, agent_type, ai_subtype=None):
        """Calculate percentage of specific agent type"""
        count = sum(1 for a in self.agent_list 
                   if a.type == agent_type and 
                   (ai_subtype is None or a.ai_subtype == ai_subtype))
        return (count / len(self.agent_list)) * 100 if self.agent_list else 0

    def _get_avg_connection_strength(self):
        """Calculate average connection strength across all agents"""
        strengths = [
            strength['strength']
            for agent in self.agent_list
            for strength in agent.connections.values()
        ]
        return sum(strengths) / len(strengths) if strengths else 0

    def _get_network_density(self):
        """Calculate network density"""
        total_possible = len(self.agent_list) * (len(self.agent_list) - 1)
        total_connections = sum(len(a.connections) for a in self.agent_list)
        return total_connections / total_possible if total_possible > 0 else 0

    def _get_recommendation_success_rate(self):
        """Calculate average recommendation success rate"""
        recsys_agents = [a for a in self.agent_list if a.type == 1 and a.ai_subtype == 1]
        return sum(a.success_rate for a in recsys_agents) / len(recsys_agents) if recsys_agents else 0

    def _get_avg_recommendation_strength(self):
        """Calculate average recommendation strength"""
        recsys_agents = [a for a in self.agent_list if a.type == 1 and a.ai_subtype == 1]
        return sum(a.recommendation_strength for a in recsys_agents) / len(recsys_agents) if recsys_agents else 0

    def _get_echo_chamber_strength(self):
        """Calculate average echo chamber strength"""
        return sum(a.echo_chamber_strength for a in self.agent_list) / len(self.agent_list) if self.agent_list else 0

    def _get_content_homogeneity(self):
        """Calculate content preference homogeneity"""
        preferences = [0, 1, 2]
        counts = [sum(1 for a in self.agent_list if a.preference == p) for p in preferences]
        max_count = max(counts)
        return max_count / len(self.agent_list) if self.agent_list else 0

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