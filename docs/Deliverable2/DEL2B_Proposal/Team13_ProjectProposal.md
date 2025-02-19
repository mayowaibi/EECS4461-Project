  
Section 1: Phenomena of interest (Revised Version from DEL 1.B)  
Echo chambers are a phenomenon on social media platforms like YouTube, where algorithm-driven recommendations and bot interactions reinforce user’s existing beliefs while also filtering out opposing viewpoints. A key dynamic of this process, as described in Brown et al. (Brookings Report), is the idea of mild ideological echo chambers, where users are gradually exposed to content that aligns more closely with their existing views, subtly narrowing their ideological diversity. Social bots amplify this effect by interacting with each other and with YouTube’s recommendation algorithm, which artificially boosts content through engagement tactics like views, likes, comments, and shares. Since YouTube prioritizes content with high engagement, bots can manipulate this system, making certain narratives disproportionately visible. This leads to a narrowing of content diversity, reinforcing ideological isolation and making it harder for users to encounter alternative viewpoints. This creates reinforcement loops that push users further into selective exposure, making them more susceptible to misinformation and political polarization. By utilizing agent-based modelling, we aim to simulate how bot-driven amplification influences media ecosystems, which provides insight into how digital discourse is shaped and potential strategies to improve recommendation algorithms.

Section 2: Phenomena of interest (Source Summaries & Citations)  
**Source \#1: Echo chambers, rabbit holes, and ideological bias: How YouTube recommends content to real users**  
This article explores how YouTube’s recommendation algorithm influences what people watch and how it can lead them into echo chambers and rabbit holes. The study examines how the platform’s algorithm personalized recommendations based on user interactions, leading to the reinforcement of existing beliefs. The researchers found that while YouTube’s algorithm does not necessarily push most users into extremist rabbit holes, it does create mild ideological echo chambers, where users engaging with certain content are gradually exposed to narrower ideological ranges. However, not everyone falls into deep ideological bubbles; some users still get a mix of different perspectives. This study is directly relevant to our project because it shows how YouTube’s algorithm plays a key role in reinforcing selective exposure, which is a major factor in the echo chamber effect.

**Source \#2: Debating in Echo Chambers: How Culture Shapes Communication in Conspiracy Theory Networks on YouTube**  
This paper looks at how conspiracy theory discussions on YouTube function as echo chambers and whether they are truly closed-off spaces. The researchers analyzed YouTube comment sections using social network analysis and qualitative methods. They found that not all conspiracy communities behave the same way. For example, the QAnon supporters are highly insular and reinforce their own beliefs, while others, such as Flat Earth believers, actually engage in debates and discussions with outsiders. The study also highlights how cultural norms shape the way people interact in these online spaces. This research paper is useful for our project because it provides real-world examples of how echo chambers form on YouTube, particularly when it comes to political and scientific misinformation.

**APA Citations:**  
Source \#1:  
Brown, M. A., Nagler, J., Bisbee, J., Lai, A., & Tucker, J. A. (2023, October 26). *Echo chambers, rabbit holes, and ideological bias: How YouTube recommends content to real users.* Brookings Institute. [https://www.brookings.edu/articles/echo-chambers-rabbit-holes-and-ideological-bias-how-youtube-recommends-content-to-real-users/](https://www.brookings.edu/articles/echo-chambers-rabbit-holes-and-ideological-bias-how-youtube-recommends-content-to-real-users/)

Source \#2:  
Grusauskaite, K., Carbone, L., Harambam, J., & Aupers, S. (2024). *Debating (in) echo chambers: How culture shapes communication in conspiracy theory networks on YouTube. New Media & Society, 26(12), 7037–7057.* [https://doi.org/10.1177/14614448231162585](https://doi.org/10.1177/14614448231162585)

Section 3: Describe the Core Components of the Simulation  
Our simulation will use agent-based modelling (using the python Mesa library) to analyze how YouTube’s recommendation system and social bots contribute to echo chamber formation. The closest Mesa example would be Schelling’s Segregation Model. This is relevant to our project as it focuses on how individuals move toward like-minded neighbours, similar to how our phenomenon models how users cluster into ideological content bubbles based on YouTube’s recommendation system.

**3.1 Entities:**  
Human Users:

* Roles:   
  * Represent real users who consume and engage with or create content  
  * The algorithm influences what content they are exposed to, which reinforces selective exposure  
* Behaviours:  
  * Act based on preferences, engaging with content that aligns with their beliefs  
  * Engage by watching, liking, commenting and sharing videos  
* Goals:  
  * To maximise personal satisfaction by reducing cognitive dissonance  
    

Social Bots:

* Roles:  
  * Fake users that artificially boost engagement by mimicking human behaviour  
* Behaviours:  
  * Influence the recommendation system by increasing engagement metrics (e.g likes, comments, shares) on certain videos  
* Goals:  
  * To promote specific agendas or drive polarization (dividing users into distinct groups)  
    

YouTube Algorithm:

* Roles:  
  * Prioritize high-engagement content  
* Behaviours:  
  * Suggest videos based on watch history, engagement levels, and bot interactions  
* Goals:  
  * Maximise user engagement and watch time

In the Schelling Segregation Model, agents prefer similar neighbors, leading to segregation. Similarly, human users are naturally segregated as a result of the YouTube algorithm.

**3.2 Affordances:**  
On YouTube, the main affordances that drive echo chambers are engagement metrics:

* Likes/Dislikes: allow users to express preferences, informing the recommendation algorithm what videos to recommend/not recommend  
* Subscriptions: allow users to follow their favourite creators, informing the recommendation algorithm what type of channels to recommend/not recommend to the user  
* Comments: allow for discussions between users, often reinforces groupthink  
* Shares: allow for content to spread between like-minded individuals


As social bots engage with content in these ways, they can manipulate YouTube's recommendation algorithm, creating echo chambers for human users.

As human users engage with content in these ways, they are more likely to be recommended similar content, reinforcing any pre-existing echo chambers.

Agents in the Schelling Segregation Model relocate to neighborhoods where they feel more “comfortable” leading to segregation groups that are all like minded. Similarly on Youtube, users “relocate” to content clusters that align with their content preferences through these affordances, acting as the mechanisms that drive users into “neighborhoods” of similar content and viewpoints. Therefore, these echo chambers created on Youtube mirror the segregated neighborhoods in the Schelling Model.

**3.3 Algorithms:**

* YouTube’s recommendation algorithm  
  * YouTube's recommendation algorithm decides what content is deemed relevant based on user behaviour; personalised suggestions based on user history  
  * The autoplay feature on YouTube allows videos to automatically play after a video is watched. The next video played is based on the YouTube recommendation algorithm and can gradually lead users deeper into content echo chambers  
  * The search results on YouTube are influenced by the recommendation algorithm as results are ranked by engagement, watch time and a user's viewing history. This prioritizes content similar to what users have already engaged with  
  * YouTube’s algorithm also amplifies viral content, meaning that videos that quickly gain popularity through high engagement are pushed to more users, increasing the visibility of the content which reinforces existing biases at a large scale  
      
* Bot amplification algorithm  
  * Used to artificially inflate engagement metrics by mimicking certain user behaviours  
  * The YouTube algorithm is tricked into thinking that the engagement is organic which leads to the content being recommended more often and an increase in engagement  
  * Reinforces echo chambers by repeatedly exposing users to manipulated content which reduces exposure to more diverse viewpoints/content

Section 4: Simulation Anticipated Outcomes  
**Diagram using Mesa’s “Schelling Segregation Model” as an analogy**

Description of components with echo chambers:

* coloured circles: represents the agents on Youtube  
  * Each agent will have two attributes:  
    * Content preference  
    * If human or not  
  * AI agents (recommendation algorithms, social bots, etc) will be represented as a “marked” (different types of “marks” for each AI type, e.g. mark “r” represents recommendation algorithms) node and will have a content preference of either, for the sake of this example, orange or blue  
  * User agents (viewers on Youtube) will be represented as “unmarked” nodes and will have a content preference of either, for the sake of this example, orange or blue  
* agent density: controls how many users are displayed on the graph  
* fraction minority: controls the balance between the users, 0.2 has 20% blue agents and 80% orange agents  
  * In our simulation we would need two sliders to control the fraction minority of AI and user agents  
* homophily: how similar user’s neighbors must be to make them “happy”, 0.4 needs 40% of neighbors to have the same content preference (orange or blue)  
  * This is the AI recommender tolerance, basically describes how flexible Youtube’s recommendation algorithm is in recommending content outside of the user’s usual preference  
  * Low homophily means that the AI recommender is highly tolerant and recommends diverse content while high homophily means that the AI recommender is intolerant and sticks to recommending content the user already likes.  
  * In our simulation we would also need homophily for AI agents separate from user agents  
* user agent engagement percentage (through affordances): how often user agents engage with content (by liking, sharing and commenting) in their echo chamber  
  * A high percentage means that users engage often with content and are more likely to remain in their content echo chamber  
  * directly correlates with homophily, higher engagement results in higher homophily (as agents would be “happier” in a larger cluster)  
* social bot engagement percentage (through affordances): how often social bots engage with content (by liking, sharing, commenting and recommending)  
  * A high percentage means that social bots engage often with content and the content is more likely to be recommended to user agents  
  * directly correlates with homophily, higher engagement results in higher homophily (as agents would be “happier” in a larger cluster)

In a successful simulation of echo chambers occuring on Youtube, we would observe several key patterns:

* Clustering Pattern: We would see a clear formation of groups where users of the same content preference (blue or orange) are grouped together. There would be a few “hybrid” users remaining between different content groups that either have no general preference or has a wide variety of preferences  
  * To show that AI to AI interactions amplifies the echo chamber effect, we can model a mechanism where AI agents that cluster together and become “happy” are more likely to attract human users with the same content preference, forming larger echo chamber clusters when compared to clusters without AI to AI interactions  
* Happy Users: There would be a high percentage of “happy” users, in this case if they are beside three or more users with the same interest as them (same colour)  
* Less interactions: On the step graph we would initially see a huge spike in the number of happy users when they are first arranged, but after it stay relatively the same as there are less cross-group interactions over time and more stable large groups

These patterns describe the echo chamber phenomena in the real world because it shows:

* that users only see content similar to what they already like/watch (clustering)  
  * larger cluster form due to AI to AI interactions amplifying the echo chamber effect  
* Youtube algorithm continuously recommends the same content type the same group of people (less interactions)  
  * The continuous recommendation is also amplified through AI to AI interactions  
* that users become isolated from different viewpoints as Youtube’s algorithms prioritises making the user “happy” and not showing them new content (happy users)

