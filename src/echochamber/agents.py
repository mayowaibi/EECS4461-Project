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
        
        # AI-specific attributes, including Reinforcement Learning (RL)
        if self.type == 1:  # AI Agent
            self.ai_subtype = ai_subtype
            self.amplification_power = 1.0
            self.bot_cluster_size = 0
            self.human_influence_radius = 1
            
            # Base Reinforcement Learning parameters
            self.learning_rate = 0.1 # How quickly AI adapts to new information
            self.discount_factor = 0.9 # How much future rewards matter (90%)
            self.exploration_rate = 0.2 # 20% chance to try new actions
            self.action_history = [] # Track what actions were taken
            
            if self.ai_subtype == 0:  # Social Bot
                # Bot-specific Q-values - only what's used in _execute_bot_action
                self.q_values = {
                    'cluster': 0.0,     # Value of joining/forming clusters
                    'coordinate': 0.0,  # Value of coordinating with other bots
                    'engage': 0.0,      # Value of engaging with content
                    'amplify': 0.0,     # Value of amplifying content
                }
                # Bot-specific rewards - only what's used in _execute_bot_action
                self.rewards = {
                    'cluster_growth': 0.8,      # Growing bot clusters
                    'cluster_influence': 0.5,    # Cluster successfully influencing
                    'engagement_growth': 0.4,    # Increasing engagement
                    'influence_success': 0.6     # Successfully influencing humans
                }

            elif self.ai_subtype == 1:  # Recommendation Algorithm
                self.recommendation_strength = 1.0
                self.success_rate = 0.0
                self.user_profiles = {}
                self.recommendation_radius = 2
                
                # Recommendation-specific Q-values - only what's used in _execute_recommendation_action
                self.q_values = {
                    'personalize': 0.0,  # Value of personalizing recommendations
                    'explore': 0.0,      # Value of trying new content
                    'exploit': 0.0       # Value of using known preferences
                }
                # Recommendation-specific rewards - only what's used in _execute_recommendation_action
                self.rewards = {
                    'recommendation_success': 0.7,  # Successful recommendations
                    'user_engagement': 0.4,        # Increased user engagement
                    'preference_match': 0.5        # Matching user preferences
                }

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

        # Add interaction tracking attributes
        self.interaction_history = {
            'bot_bot': 0,          # Count of bot-to-bot interactions
            'bot_human': 0,        # Count of bot-to-human interactions
            'recommendation_influence': 0,  # Times recommendations were accepted
            'interaction_success': 0,       # Successful influence attempts
            'last_interaction_type': None,  # Track type of last interaction
            'influenced_agents': set()      # Set of agents successfully influenced
        }

    def step(self):
        """
        Execute one step for the agent in the simulation. This method handles:
        
        1. Network Updates:
           - Updates connections with neighboring agents
        
        2. Similarity Calculation:
           - Content preference matching (50% weight)
           - Bot/AI influence (30% weight)
           - Engagement-based factors (20% weight)
           - Network influence (10% weight applied to total)
        
        3. Movement and Actions:
           For Human Agents (type 0):
           - Move if similarity < homophily threshold
           - Stay and increase happiness if satisfied
           
           For AI Agents (type 1):
           - Execute reinforcement learning actions
           - For social bots: form clusters and amplify influence
           - For recommendation algorithms: analyze users and make recommendations
        
        4. Updates:
           - Update engagement metrics
           - Adjust homophily based on echo chamber strength
        """
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, radius=self.model.radius
        )

        # 1. Update network connections first
        self._update_network_connections(neighbors)

        # 2. Calculate base similarity
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
            
            # Calculate initial similarity
            similarity_fraction = (content_similarity * 0.5 +  
                                 bot_influence +              
                                 engagement_factor)           
            
            # Add network influence (10% weight)
            if self.connections:
                network_similarity = sum(conn['strength'] for conn in self.connections.values()) / len(self.connections)
                similarity_fraction = (similarity_fraction * 0.9 + network_similarity * 0.1)
            
            similarity_fraction = min(1.0, similarity_fraction)

        # 3. Movement and Actions
        if self.type == 0:  # Human Agents
            # Humans move based on similarity
            if similarity_fraction < self.current_homophily:
                self.model.grid.move_to_empty(self)
            else:
                self.model.happy += 1
        
        else:  # AI Agents
            # Choose and execute action using RL
            action = self._choose_action()
            reward = self._execute_action(action, neighbors)
            self._update_q_values(action, reward)
            
            # Social bots can get power boost
            if self.ai_subtype == 0 and self.bot_cluster_size > 1:
                self._amplify_bot_power()

        # 4. Update engagement and homophily
        self._update_engagement_and_homophily(similarity_fraction)

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
            engage_prob *= (1 + network_boost * 0.2)

        # Handle engagement
        if self.model.random.random() < engage_prob:
            self._process_engagement()

    def _process_engagement(self):
        """Handle engagement actions and updates."""
        engagement_weights = {
            'like': 0.05, # 5% boost to homophily
            'comment': 0.10, # 10% boost to homophily
            'share': 0.15 # 15% boost to homophily
        }
        
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
        
        # Update homophily based on agent type
        if self.type == 0:  # Human
            self.current_homophily = min(
                1.0,
                self.base_homophily + (boost * self.echo_chamber_strength)
            )
        elif self.type == 1 and self.ai_subtype == 0:  # Social bot
            cluster_multiplier = 1.0 + (self.bot_cluster_size * 0.1)
            self.current_homophily = min(
                1.0,
                self.base_homophily + (boost * 2.0 * cluster_multiplier)
            )

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

    def _update_recommendation_model(self, success):
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
        
        # Impact of recommendation success on connection strength
        if self.type == 1 and self.ai_subtype == 1 and other_agent.type == 0:
            recommendation_success = 1.0 if self.success_rate > 0.5 else 0.0
            total_strength += recommendation_success * 0.2
        
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

    def _choose_action(self):
        """Choose action based on Q-values and exploration rate."""
        if self.model.random.random() < self.exploration_rate:
            # Explore: choose random action
            return self.model.random.choice(list(self.q_values.keys()))
        else:
            # Exploit: choose best known action
            return max(self.q_values, key=self.q_values.get)

    def _execute_action(self, action, neighbors):
        """Execute chosen action and return reward."""
        reward = 0.0
        
        if self.ai_subtype == 0:  # Social Bot
            reward = self._execute_bot_action(action, neighbors)
        elif self.ai_subtype == 1:  # Recommendation Algorithm
            reward = self._execute_recommendation_action(action, neighbors)
        
        return reward

    def _execute_bot_action(self, action, neighbors):
        """
        Execute actions for social bots (ai_subtype = 0).
        
        Available actions:
        1. 'cluster': Form or join clusters with similar bots
           - Success: Increases bot cluster size
           - Reward: cluster_growth (0.8)
        
        2. 'coordinate': Work with other bots to increase influence
           - Success: Coordinated actions with other bots
           - Reward: coordination_success (0.5)
        
        3. 'engage': Attempt to engage with human users
           - Success: Human's engagement > their homophily
           - Reward: successful_influence (0.6)
        
        4. 'amplify': Boost content visibility through engagement
           - Success: Increased engagement metrics
           - Reward: engagement_growth (0.4)
        """
        reward = 0
        
        if action == 'cluster':
            # Form/join bot clusters
            similar_bots = [n for n in neighbors if n.type == 1 and n.preference == self.preference]
            for bot in similar_bots:
                success = self._update_bot_cluster(neighbors)
                self._track_interaction(bot, 'bot_bot', success)
                if success:
                    reward += self.rewards['cluster_growth']
                    
        elif action == 'coordinate':
            similar_bots = [n for n in neighbors if n.type == 1]
            if similar_bots:
                for bot in similar_bots:
                    self._track_interaction(bot, 'bot_bot', True)
                    reward += self.rewards['coordination_success']
                    
        elif action == 'engage':
            human_neighbors = [n for n in neighbors if n.type == 0]
            for human in human_neighbors:
                success = (human.engagement_rate > human.base_homophily)
                self._track_interaction(human, 'bot_human', success)
                if success:
                    reward += self.rewards['successful_influence']
                    
        elif action == 'amplify':
            # Increase engagement metrics
            self.likes += 1
            self.comments += 1
            self.shares += 1
            reward += self.rewards['engagement_growth']
                    
        return reward

    def _execute_recommendation_action(self, action, neighbors):
        """
        Execute actions for recommendation algorithms (ai_subtype = 1).
        
        Available actions:
        1. 'personalize': Analyze user preferences and update recommendations
           - Success: Better understanding of user preferences
           - Reward: preference_match (0.5)
        
        2. 'explore': Recommend different content to test user interests
           - Success: User engages with new content
           - Reward: user_engagement (0.4)
        
        3. 'exploit': Recommend content matching known preferences
           - Success: User accepts recommendation
           - Reward: recommendation_success (0.7)
        """
        reward = 0
        
        if action == 'personalize':
            # Analyze and update user preferences
            users = [n for n in neighbors if n.type == 0]
            for user in users:
                self._analyze_user_preferences(user)
                success = (user.engagement_rate > user.base_homophily)
                self._track_interaction(user, 'recommendation', success)
                if success:
                    reward += self.rewards['preference_match']
                    
        elif action == 'explore':
            users = [n for n in neighbors if n.type == 0]
            for user in users:
                recommended_content = self._generate_recommendations(user)
                if recommended_content != user.preference:
                    success = (user.engagement_rate > user.base_homophily)
                    self._track_interaction(user, 'recommendation', success)
                    if success:
                        reward += self.rewards['user_engagement']
                    
        elif action == 'exploit':
            users = [n for n in neighbors if n.type == 0]
            for user in users:
                recommended_content = self._generate_recommendations(user)
                success = (recommended_content == user.preference)
                self._track_interaction(user, 'recommendation', success)
                if success:
                    reward += self.rewards['recommendation_success']
                    
        return reward

    def _update_q_values(self, action, reward):
        """Update Q-values using Q-learning formula."""
        # Q(s,a) = Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
        
        # Get maximum future Q-value
        max_future_q = max(self.q_values.values())
        
        # Update Q-value for the taken action
        old_q = self.q_values[action]
        self.q_values[action] = old_q + self.learning_rate * (
            reward + 
            self.discount_factor * max_future_q - 
            old_q
        )
        
        # Record action and result
        self.action_history.append({
            'action': action,
            'reward': reward,
            'q_value': self.q_values[action]
        })

    def _track_interaction(self, other_agent, interaction_type, success=False):
        """
        Track interactions between agents.
        
        Args:
            other_agent: The agent being interacted with
            interaction_type: Type of interaction ('bot_bot', 'bot_human', 'recommendation')
            success: Whether the interaction was successful
        """
        if interaction_type == 'bot_bot' and self.type == 1 and other_agent.type == 1:
            self.interaction_history['bot_bot'] += 1
            if success:
                self.interaction_history['interaction_success'] += 1
                self.interaction_history['influenced_agents'].add(other_agent.unique_id)
                
        elif interaction_type == 'bot_human' and self.type == 1 and other_agent.type == 0:
            self.interaction_history['bot_human'] += 1
            if success:
                self.interaction_history['interaction_success'] += 1
                self.interaction_history['influenced_agents'].add(other_agent.unique_id)
                
        elif interaction_type == 'recommendation' and self.type == 1 and self.ai_subtype == 1:
            if success:
                self.interaction_history['recommendation_influence'] += 1
                self.interaction_history['influenced_agents'].add(other_agent.unique_id)
        
        self.interaction_history['last_interaction_type'] = interaction_type

    def get_interaction_stats(self):
        """
        Return summary statistics of agent's interactions.
        """
        total_interactions = (self.interaction_history['bot_bot'] + 
                            self.interaction_history['bot_human'] + 
                            self.interaction_history['recommendation_influence'])
        
        success_rate = (self.interaction_history['interaction_success'] / 
                       total_interactions if total_interactions > 0 else 0)
        
        return {
            'total_interactions': total_interactions,
            'success_rate': success_rate,
            'unique_influences': len(self.interaction_history['influenced_agents']),
            'bot_bot_interactions': self.interaction_history['bot_bot'],
            'bot_human_interactions': self.interaction_history['bot_human'],
            'recommendation_successes': self.interaction_history['recommendation_influence']
        }
