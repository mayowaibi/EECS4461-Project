from mesa import Agent

# type = 0 : user, 1 : social bot
# preference = 0 : video games, 1 : sports, 2 : politics

class SchellingAgent(Agent):
    """
    Agent class for YouTube echo chamber simulation.
    Types: Human (0), Social Bot (1)
    Preferences: Video Games (0), Sports (1), Politics (2)
    """

    def __init__(self, model, agent_type: int, content_preference: int, base_homophily: float, 
                 engagement_rate: float = 0.5) -> None:
        """Create a new agent for YouTube simulation.
        Args:
            model: The model instance the agent belongs to
            agent_type: Type of agent (0=human, 1=social bot)
            content_preference: Content preference (0=games, 1=sports, 2=politics)
            base_homophily: Base homophily level before engagement effects (0-1)
            engagement_rate: Base rate of engagement with content (0-1)
                           Higher rates strengthen echo chambers through increased homophily
        """
        super().__init__(model)
        self.type = agent_type
        self.preference = content_preference
        self.base_homophily = base_homophily
        self.current_homophily = base_homophily  # Will be modified by engagement
        self.engagement_rate = engagement_rate
        
        # Engagement counters
        self.likes = 0
        self.comments = 0
        self.shares = 0
        
        # Echo chamber strength (affects and is affected by engagement)
        self.echo_chamber_strength = 0.0

    def step(self) -> None:
        """Determine if agent is happy and move if necessary."""
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, radius=self.model.radius
        )

        # Count neighbors with same content preference
        similar_neighbors = len([n for n in neighbors if n.preference == self.preference])
        
        # Count social bot neighbors
        bot_neighbors = len([n for n in neighbors if n.type == 1])

        # Calculate the fraction of similar neighbors
        if (valid_neighbors := len(neighbors)) > 0:
            # Basic similarity based on content preference
            similarity_fraction = similar_neighbors / valid_neighbors
            
            # Social bot neighbors amplify the echo chamber effect
            if self.type == 0:  # If human user
                # Increase similarity effect based on social bot presence
                bot_influence = (bot_neighbors / valid_neighbors) * 0.2  # 20% boost from bots
                similarity_fraction = min(1.0, similarity_fraction + bot_influence)
        else:
            similarity_fraction = 0.0

        # Update engagement and homophily based on local environment
        self._update_engagement_and_homophily(similarity_fraction)

        # Move if unhappy (different logic based on agent type)
        if similarity_fraction < self.current_homophily:
            self.model.grid.move_to_empty(self)
        else:
            self.model.happy += 1

    def _update_engagement_and_homophily(self, similarity_fraction: float) -> None:
        """Update agent's engagement and adjust homophily based on echo chamber strength.
        
        Args:
            similarity_fraction: Fraction of neighbors with same preference (0-1)
            0: None of the neighbors have the same preference
            1: All of the neighbors have the same preference
        """
        # Update echo chamber strength
        self.echo_chamber_strength = similarity_fraction
        
        # Calculate engagement probability based on echo chamber strength
        if self.type == 0:  # Human user
            # Users engage more in stronger echo chambers
            engage_prob = self.engagement_rate * (1 + self.echo_chamber_strength)
        else:  # Social bot
            # Bots maintain higher, more consistent engagement
            engage_prob = self.engagement_rate * 1.5
        
        # Different engagement impacts, represents how different types of engagement on Youtube have varying levels of influence 
        engagement_weights = {
            'like': 0.05, # 5% boost to homophily
            'comment': 0.10, # 10% boost to homophily
            'share': 0.15 # 15% boost to homophily
        }
        
        if self.model.random.random() < engage_prob:
            action_type = self.model.random.random()
            if action_type < 0.5:
                self.likes += 1
                boost = engagement_weights['like']
            elif action_type < 0.8:
                self.comments += 1
                boost = engagement_weights['comment']
            else:
                self.shares += 1
                boost = engagement_weights['share']
            
            # Engagement increases homophily with weighted impact
            if self.type == 0:  # Human users
                self.current_homophily = min(
                    1.0,
                    self.base_homophily + (boost * self.echo_chamber_strength)
                )
            else:  # Social bots
                self.current_homophily = min(
                    1.0,
                    self.base_homophily + (boost * 2.0)  # Bots have stronger influence
                )
