from mesa import Agent

# type = 0 : user, 1 : AI agent
# AI subtype = 0 : social bot, 1 : recommendation algorithm
# preference = 0 : video games, 1 : sports, 2 : politics

class EchoChamberAgent(Agent):
    """
    Agent class for YouTube echo chamber simulation.
    Types: Human (0), AI Agent (1)
    AI Subtypes: Social Bot (0), Recommendation Algorithm (1)
    Preferences: Video Games (0), Sports (1), Politics (2)
    """

    def __init__(self, model, agent_type: int, content_preference: int, base_homophily: float, 
                 engagement_rate: float = 0.5, ai_subtype: int = 0) -> None:
        """Create a new agent for YouTube simulation.
        Args:
            model: The model instance the agent belongs to
            agent_type: Type of agent (0=human, 1=AI agent)
            content_preference: Content preference (0=games, 1=sports, 2=politics)
            base_homophily: Base homophily level before engagement effects (0-1)
            engagement_rate: Base rate of engagement with content (0-1)
            ai_subtype: For AI agents, specifies bot (0) or recommendation algorithm (1)
        """
        super().__init__(model)
        self.type = agent_type
        self.preference = content_preference
        self.base_homophily = base_homophily
        self.current_homophily = base_homophily
        self.engagement_rate = engagement_rate
        
        # Engagement counters
        self.likes = 0
        self.comments = 0
        self.shares = 0
        
        # Echo chamber strength (affects and is affected by engagement)
        self.echo_chamber_strength = 0.0
        
        # AI-specific attributes
        if self.type == 1:  # AI Agent
            self.ai_subtype = ai_subtype
            self.amplification_power = 1.0
            self.bot_cluster_size = 0
            self.human_influence_radius = 1

            if self.ai_subtype == 1:  # Recommendation Algorithm
                self.recommendation_strength = 1.0
                self.success_rate = 0.0
                self.learning_rate = 0.1
                self.user_profiles = {}
                self.recommendation_radius = 2

        # Network influence attributes
        self.connections = {}  # Dictionary to store connections and their strengths
        self.network_influence = 0.0  # Current influence level in network
        self.influence_radius = 2  # How far influence spreads
        self.connection_threshold = 0.3  # Minimum strength to maintain connection
        
        # Simplified network weights (removed temporal)
        self.network_weights = {
            'direct': 0.7,    # Direct interactions (comments, replies)
            'indirect': 0.3,  # Indirect interactions (shared viewers)
        }

    def step(self) -> None:
        """Determine if agent is happy and move if necessary."""
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, radius=self.model.radius
        )

        if not neighbors:
            similarity_fraction = 0.0
        else:
            # 1. Content Preference Matching (50% of happiness)
            similar_content = len([n for n in neighbors if n.preference == self.preference])
            content_similarity = similar_content / len(neighbors)
            
            # 2. AI/Bot Influence (30% of happiness)
            bot_neighbors = len([n for n in neighbors if n.type == 1])
            bot_similarity = len([n for n in neighbors 
                                if n.type == 1 and n.preference == self.preference])
            
            # Special case: Bot-to-Bot interactions
            if self.type == 1 and self.ai_subtype == 0:  # If this agent is a bot
                # Track bot cluster size
                if bot_neighbors > 0:
                    self._update_bot_cluster(neighbors)
                    
                # Bots with same preference amplify each other
                if bot_similarity > 0:
                    # Bots are more influenced by other bots with same preference
                    bot_influence = (bot_similarity / len(neighbors)) * 0.4  # 40% weight for bots
                else:
                    bot_influence = 0.0
            elif self.type == 0:  # If human user
                # Humans are influenced by bots
                if bot_neighbors > 0:
                    bot_influence = (bot_similarity / bot_neighbors) * 0.3
                    
                    # Apply additional influence from bot clusters
                    cluster_bonus = self._calculate_bot_cluster_influence(neighbors)
                    bot_influence += cluster_bonus
                else:
                    bot_influence = 0.0
            else:
                bot_influence = 0.0
            
            # 3. Engagement-based Modification (20% of happiness)
            engagement_factor = (self.likes * 0.05 + 
                               self.comments * 0.10 + 
                               self.shares * 0.15) / len(neighbors)
            engagement_factor = min(0.2, engagement_factor)  # Cap at 20% influence
            
            # Combine all factors
            similarity_fraction = (content_similarity * 0.5 +  # Content matching (50%)
                                 bot_influence +              # Bot influence (30%)
                                 engagement_factor)           # Engagement (20%)
            
            similarity_fraction = min(1.0, similarity_fraction)  # Cap at 1.0

        if self.type == 1 and self.ai_subtype == 1:  # Recommendation Algorithm
            # Get users in recommendation radius
            users = [n for n in neighbors if n.type == 0]
            
            for user in users:
                # 1. Analyze user preferences
                self._analyze_user_preferences(user)
                
                # 2. Generate and apply recommendation
                recommended_content = self._generate_recommendations(user)
                
                # 3. Check if recommendation was successful
                success = (user.preference == recommended_content and 
                          user.engagement_rate > user.base_homophily)
                
                # 4. Update recommendation model
                self._update_recommendation_model(success)
                
                # 5. Influence user based on recommendation strength
                if success:
                    user.current_homophily = min(1.0, 
                        user.current_homophily + (0.1 * self.recommendation_strength))

        # Add network influence to similarity calculation (after existing similarity calculation)
        if self.connections:
            network_similarity = sum(conn['strength'] for conn in self.connections.values()) / len(self.connections)
            # Add 10% network influence to the agent's overall similarity calculation
            similarity_fraction = (similarity_fraction * 0.9 + network_similarity * 0.1)
        
        # Update engagement and homophily based on local environment
        self._update_engagement_and_homophily(similarity_fraction)

        # Move if unhappy
        if similarity_fraction < self.current_homophily:
            self.model.grid.move_to_empty(self)
        else:
            self.model.happy += 1
            
            # Bots in clusters increase their amplification power
            if self.type == 1 and self.bot_cluster_size > 1:
                self._amplify_bot_power()

        # Update network connections
        self._update_network_connections(neighbors)

    def _update_bot_cluster(self, neighbors):
        """Track the size of bot clusters and update bot metrics."""
        # Find all bots with same preference in neighborhood
        similar_bots = [n for n in neighbors if n.type == 1 and n.preference == self.preference]
        self.bot_cluster_size = len(similar_bots) + 1  # Include self
        
        # Update model's tracking of bot clusters
        if hasattr(self.model, 'bot_clusters'):
            # Add this bot's cluster to the model's tracking
            self.model.bot_clusters[self.preference] = max(
                self.model.bot_clusters.get(self.preference, 0),
                self.bot_cluster_size
            )

    def _calculate_bot_cluster_influence(self, neighbors):
        """Calculate additional influence from bot clusters on human users."""
        # Get all bots in neighborhood
        bots = [n for n in neighbors if n.type == 1]
        
        if not bots:
            return 0.0
            
        # Calculate influence based on bot cluster sizes and amplification power
        total_influence = 0.0
        for bot in bots:
            if bot.preference == self.preference:
                # Bots in clusters with same preference have stronger influence
                cluster_factor = min(0.1, bot.bot_cluster_size * 0.02)  # 2% per bot in cluster, max 10%
                amplification = bot.amplification_power
                total_influence += cluster_factor * amplification
                
        return min(0.15, total_influence)  # Cap at 15% additional influence

    def _amplify_bot_power(self):
        """Increase bot's amplification power based on cluster size and engagement."""
        # Bots in larger clusters with higher engagement have more influence
        cluster_bonus = min(0.5, self.bot_cluster_size * 0.1)  # 10% per bot in cluster, max 50%
        engagement_bonus = min(0.5, (self.likes + self.comments * 2 + self.shares * 3) * 0.01)
        
        # Update amplification power (capped at 3.0)
        self.amplification_power = min(3.0, 1.0 + cluster_bonus + engagement_bonus)
        
        # Larger clusters can influence humans from further away
        self.human_influence_radius = min(3, 1 + (self.bot_cluster_size // 3))

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
        elif self.type == 1 and self.ai_subtype == 0:  # Social bot
            # Bots maintain higher, more consistent engagement
            # Bots in clusters engage even more
            cluster_factor = 1.0 + (self.bot_cluster_size * 0.1)  # 10% boost per bot in cluster
            engage_prob = self.engagement_rate * 1.5 * cluster_factor
        elif self.type == 1 and self.ai_subtype == 1:  # Recommendation Algorithm
            # Recommendations become more effective with higher success rates
            engage_prob = self.engagement_rate * (1.0 + self.success_rate)
        else:
            engage_prob = 0.0
        
        # Add network influence to engagement probability
        if self.connections:
            network_boost = sum(conn['strength'] for conn in self.connections.values()) / len(self.connections)
            engage_prob *= (1 + network_boost * 0.2)  # increase engagement probability up to 20% based on connection strength
        
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
            elif self.type == 1 and self.ai_subtype == 0:  # Social bots
                # Bots in clusters have stronger homophily increases
                cluster_multiplier = 1.0 + (self.bot_cluster_size * 0.1)  # 10% per bot in cluster
                self.current_homophily = min(
                    1.0,
                    self.base_homophily + (boost * 2.0 * cluster_multiplier)
                )

        # Update engagement and homophily based on local environment
        self._update_engagement_and_homophily(similarity_fraction)

        # Move if unhappy
        if similarity_fraction < self.current_homophily:
            self.model.grid.move_to_empty(self)
        else:
            self.model.happy += 1
            
            # Bots in clusters increase their amplification power
            if self.type == 1 and self.bot_cluster_size > 1:
                self._amplify_bot_power()

    def _analyze_user_preferences(self, user):
        """
        Analyze and update user preference profiles.
        Only recommendation algorithm can analyze user preferences
        """ 
        if self.type != 1 or self.ai_subtype != 1:
            return
        
        user_id = user.unique_id
        # Create profile dictionary if it doesn't exist
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                'preference': user.preference,
                'engagement_history': [],
                'content_views': {0: 0, 1: 0, 2: 0}
            }
        
        # Update profile based on user's recent activity
        profile = self.user_profiles[user_id]
        profile['content_views'][user.preference] += 1
        profile['engagement_history'].append({
            'likes': user.likes,
            'comments': user.comments,
            'shares': user.shares
        })

    def _generate_recommendations(self, target_user):
        """
        Generate personalized content recommendations based on user's profile.
        Only recommendation algorithm can generate recommendations
        """
        if self.type != 1 or self.ai_subtype != 1:
            return None
        
        # Get user profile to see viewing and engagement history
        profile = self.user_profiles.get(target_user.unique_id)
        if not profile:
            return target_user.preference  # Default to user's current preference if no history exists
        
        # Find the most viewed content category
        max_views = max(profile['content_views'].values())
        preferred_content = [k for k, v in profile['content_views'].items() 
                            if v == max_views]
        
        # Consider engagement levels in recommendation 
        if profile['engagement_history']:
            recent_engagement = profile['engagement_history'][-1]
            engagement_score = (recent_engagement['likes'] + 
                              recent_engagement['comments'] * 2 + 
                              recent_engagement['shares'] * 3)
        else:
            engagement_score = 0
        
        return preferred_content[0] if preferred_content else target_user.preference

    def _update_recommendation_model(self, success: bool):
        """
        Update recommendation algorithm based on success/failure.
        Only recommendation algorithm can update the recommendation model
        """
        if self.type != 1 or self.ai_subtype != 1:
            return
        
        # Update success rate and recommendation strength based on success/failure
        if success:
            # Update success rate with exponential moving average (EMA)
            # 90% weight to the old success rate, 10% weight to the new success rate
            self.success_rate = (self.success_rate * 0.9) + (0.1 * 1.0)
            # Increase recommendation strength with successful recommendations
            self.recommendation_strength = min(3.0, 
                self.recommendation_strength + (self.learning_rate * self.success_rate))
        else:
            # Decrease success rate with unsuccessful recommendations
            self.success_rate = self.success_rate * 0.9
            # Reduce recommendation strength with unsuccessful recommendations
            self.recommendation_strength = max(0.5, 
                self.recommendation_strength - (self.learning_rate * 0.5))

    def _update_network_connections(self, neighbors):
        """Update network connections based on interactions and similarity."""
        for neighbor in neighbors:
            neighbor_id = neighbor.unique_id
            
            # Calculate connection strength based on direct and indirect interactions
            connection_strength = self._calculate_connection_strength(neighbor)
            
            # Update or create connection if strength is above threshold (0.3)
            if connection_strength > self.connection_threshold:
                if neighbor_id not in self.connections:
                    # Create new connection
                    self.connections[neighbor_id] = {
                        'strength': connection_strength,
                        'last_interaction': self.model.step_count,
                        'shared_preferences': self.preference == neighbor.preference,
                        'interaction_count': 1
                    }
                else:
                    # Update existing connection (80% old strength, 20% new strength)
                    self.connections[neighbor_id]['strength'] = (
                        self.connections[neighbor_id]['strength'] * 0.8 + 
                        connection_strength * 0.2
                    )
                    self.connections[neighbor_id]['last_interaction'] = self.model.step_count
                    self.connections[neighbor_id]['interaction_count'] += 1
            
            # Remove weak connections
            self.connections = {k: v for k, v in self.connections.items() 
                              if v['strength'] > self.connection_threshold}

    def _calculate_connection_strength(self, other_agent):
        """Calculate the strength of connection between two agents."""
        # Direct interaction strength (70% weight)
        direct_strength = self._calculate_direct_strength(other_agent)
        
        # Indirect interaction strength (30% weight)
        indirect_strength = self._calculate_indirect_strength(other_agent)
        
        # Combine factors with simplified weights
        total_strength = (
            direct_strength * self.network_weights['direct'] + #0.7
            indirect_strength * self.network_weights['indirect'] #0.3
        )
        
        return min(1.0, total_strength)

    def _calculate_direct_strength(self, other_agent):
        """
        Calculate strength from direct interactions.
        Same content preferences and Similar engagement patterns (likes, comments, shares)
        """
        # Content preference similarity
        preference_match = 1.0 if self.preference == other_agent.preference else 0.3
        
        # how similar their engagement patterns are
        engagement_similarity = min(1.0, (
            abs(self.likes - other_agent.likes) * 0.3 +
            abs(self.comments - other_agent.comments) * 0.4 +
            abs(self.shares - other_agent.shares) * 0.3
        ) / 10)
        
        return (preference_match + engagement_similarity) / 2

    def _calculate_indirect_strength(self, other_agent):
        """
        Calculate strength from indirect connections.
        Shared connections with other agents
        """
        # Get shared connections
        shared_connections = set(self.connections.keys()) & set(other_agent.connections.keys())
        if not shared_connections:
            return 0.0
        
        # Calculate average strength of shared connections
        total_strength = sum(
            min(self.connections[conn_id]['strength'],
                other_agent.connections[conn_id]['strength'])
            for conn_id in shared_connections
        )
        
        return min(1.0, total_strength / len(shared_connections))
