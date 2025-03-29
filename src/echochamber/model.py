from mesa import Model
from mesa.space import SingleGrid
from mesa.datacollection import DataCollector
from agents import EchoChamberAgent
import random

class EchoChamber(Model):
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
        recsys_ratio=0.2,
        radius=1,
        seed=None,
    ):
        super().__init__(seed=seed)

        # Parameters
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
        self.prev_happy_ratio = None
        self.happy_plateau_counter = 0
        self.plateau_tolerance = 0.01  # 1% change allowed
        self.plateau_required_steps = 5  # Number of stable steps before stopping
        self.step_count = 0

        # Environment
        self.grid = SingleGrid(width, height, torus=True)

        # Trackers
        self.happy = 0
        self.bot_clusters = {}

        # Store all agents (optional)
        self.agent_list = []

        # Agent creation
        for _, pos in self.grid.coord_iter():
            if random.random() < self.density:
                is_ai = random.random() < self.ai_ratio
                ai_subtype = None

                if is_ai:
                    is_recsys = random.random() < self.recsys_ratio
                    ai_subtype = 1 if is_recsys else 0

                preference = random.choice([0, 1, 2])
                engagement = (
                    random.uniform(0.5, 1.0) * ai_engagement if is_ai
                    else random.uniform(0.2, 1.0) * human_engagement
                )

                agent = EchoChamberAgent(
                    model=self,
                    agent_type=1 if is_ai else 0,
                    content_preference=preference,
                    base_homophily=ai_homophily if is_ai else human_homophily,
                    engagement_rate=engagement,
                    ai_subtype=ai_subtype,
                )

                self.grid.place_agent(agent, pos)
                self.agent_list.append(agent)

        # Data Collection
        self.datacollector = DataCollector(
            model_reporters={
                "Happy Agents %": lambda m:(m.happy / len(m.agent_list)) * 100 if m.agent_list else 0,
                "AI Cluster %": lambda m: sum(
                    1 for a in m.agent_list if a.type == 1 and a.ai_subtype == 0 and a.bot_cluster_size > 1
                ) / len(m.agent_list) * 100 if m.agent_list else 0,
                "Echo Chamber Strength": lambda m: sum(
                    a.echo_chamber_strength for a in m.agent_list
                ) / len(m.agent_list) if m.agent_list else 0,
                "Network Influence": lambda m: sum(
                    a.network_influence for a in m.agent_list
                ) / len(m.agent_list) if m.agent_list else 0,
                # RL Reward measures the average reward of the AI agents
                # Rewards come from successful actions like forming clusters, influencing humans, increasing engagement, and amplifying bot power
                "Reinforcement Learning Reward": lambda m: sum(
                    sum(act['reward'] for act in a.action_history) / len(a.action_history)
                    for a in m.agent_list if a.type == 1 and hasattr(a, "action_history") and a.action_history
                ) / max(1, len([a for a in m.agent_list if a.type == 1 and a.action_history])),
                "Total Likes": lambda m: sum(a.likes for a in m.agent_list),
                "Total Comments": lambda m: sum(a.comments for a in m.agent_list),
                "Total Shares": lambda m: sum(a.shares for a in m.agent_list),
            },
            agent_reporters={
                "Type": lambda a: "Human" if a.type == 0 else ("Bot" if a.ai_subtype == 0 else "RecSys"),
                "Preference": "preference",
                "Engagement": "engagement_rate",
                "EchoStrength": "echo_chamber_strength",
                "Amplification": lambda a: getattr(a, "amplification_power", 0),
                "ClusterSize": lambda a: getattr(a, "bot_cluster_size", 0),
                "RecStrength": lambda a: getattr(a, "recommendation_strength", 0),
                "Q-Value Max": lambda a: max(a.q_values.values()) if a.type == 1 else 0,
                "SuccessRate": lambda a: getattr(a, "success_rate", 0),
                "Influenced": lambda a: len(a.interaction_history["influenced_agents"]),
                "Likes": "likes",
                "Comments": "comments",
                "Shares": "shares",
            }
        )

        # Initial data snapshot
        self.datacollector.collect(self)

    def step(self):
        self.happy = 0
        self.agents.shuffle_do("step")
        self.datacollector.collect(self)
        self.step_count += 1

        # Calculate current happy ratio
        happy_ratio = self.happy / len(self.agent_list) if self.agent_list else 0

        # Check for stability (plateau)
        if self.prev_happy_ratio is not None:
            change = abs(happy_ratio - self.prev_happy_ratio)
            if change < self.plateau_tolerance:
                self.happy_plateau_counter += 1
            else:
                self.happy_plateau_counter = 0  # Reset if there's new movement
        self.prev_happy_ratio = happy_ratio

        # Stop condition: sustained happiness plateau
        self.running = self.happy_plateau_counter < self.plateau_required_steps