import gym
import numpy as np
import math
import matplotlib.pyplot as plt
import seaborn as sns
import random

env = gym.make('CartPole-v0')

n_actions = env.action_space.n
n_states = env.observation_space.shape[0]

print("Action space size: ", n_actions)
print("State space size: ", n_states)

print('states high value:')

print(env.observation_space.high[0])
print(env.observation_space.high[1])
print(env.observation_space.high[2])
print(env.observation_space.high[3])

print('states low value:')

print(env.observation_space.low[0])
print(env.observation_space.low[1])
print(env.observation_space.low[2])
print(env.observation_space.low[3])


# define the number of buckets for each state value (x, x', theta, theta')
buckets = (3, 3, 6, 12)


upper_bounds = [
        env.observation_space.high[0],
        0.5,
        env.observation_space.high[2],
        math.radians(50)
        ]
lower_bounds = [
        env.observation_space.low[0],
        -0.5,
        env.observation_space.low[2],
        -math.radians(50)]


# HYPERPARAMETERS
n_episodes = 500            # Total episodes whuich are trained
n_steps = 200               # Max steps per episode
min_alpha = 0.1             # learning rate
min_epsilon = 0.1           # exploration rate
gamma = 1.0                 # discount factor
ada_divisor = 25            # decay rate

# INITIALISE Q MATRIX
Q = np.zeros(buckets + (n_actions,))
print(np.shape(Q))
print(Q)
def discretize(obs):
    ''' discretise the continuous state into buckets '''
    ratios = [(obs[i] + abs(lower_bounds[i])) / (upper_bounds[i] - lower_bounds[i]) for i in range(len(obs))]
    new_obs = [int(round((buckets[i] - 1) * ratios[i])) for i in range(len(obs))]
    new_obs = [min(buckets[i] - 1, max(0, new_obs[i])) for i in range(len(obs))]
    return tuple(new_obs)

def epsilon_policy(state, epsilon):
    ''' choose an action using the epsilon policy '''
    exploration_exploitation_tradeoff = np.random.random()
    if exploration_exploitation_tradeoff <= epsilon:
        action = env.action_space.sample()
    else:
        action = np.argmax(Q[state])
    return action

def greedy_policy(state):
    ''' choose an action using the greedy policy '''
    return np.argmax(Q[state])

def update_q(current_state, action, reward, new_state, alpha):
    ''' update the Q matrix with the Bellman equation '''
    Q[current_state][action] += alpha * (reward + gamma * np.max(Q[new_state]) - Q[current_state][action])

def get_epsilon(t):
    ''' decrease the exploration rate at each episode '''
    return max(min_epsilon, min(1, 1.0 - math.log10((t + 1) / ada_divisor)))

def get_alpha(t):
    ''' decrease the learning rate at each episode '''
    return max(min_alpha, min(1.0, 1.0 - math.log10((t + 1) / ada_divisor)))

rewards = []

for episode in range(n_episodes):
    current_state = env.reset()
    current_state = discretize(current_state)

    alpha = get_alpha(episode)
    epsilon = get_epsilon(episode)

    episode_rewards = 0

    for t in range(n_steps):

        action = epsilon_policy(current_state, epsilon)
        new_state, reward, done, _ = env.step(action)
        new_state = discretize(new_state)
        update_q(current_state, action, reward, new_state, alpha)
        current_state = new_state
        if done:
            print('Episode:{}/{} finished with a total reward of: {}'.format(episode, n_episodes, episode_rewards))
            break
        episode_rewards += reward

    rewards.append(episode_rewards)

# PLOT RESULTS
x = range(n_episodes)
plt.plot(x, rewards)
plt.xlabel('episode')
plt.ylabel('Training cumulative reward')
plt.savefig('Q_learning_CART.png', dpi=300)
plt.show()
print(Q)


current_state = env.reset()
current_state = discretize(current_state)
print(current_state)
episode_rewards = 0

for t in range(n_steps):
    env.render()
    action = greedy_policy(current_state)
    new_state, reward, done, _ = env.step(action)
    new_state = discretize(new_state)
    update_q(current_state, action, reward, new_state, alpha)
    current_state = new_state
    episode_rewards += reward

    if episode_rewards>=100:
        print(episode_rewards)
        plt.plot(1, episode_rewards)
        plt.xlabel('episode')
        plt.ylabel('Training cumulative reward')
        plt.savefig('Q_learning_CART.png', dpi=300)
        plt.show()
        break

    if done:
        print('total reward : {}'.format(episode_rewards))
        break

env.close()

#Code help from:https://www.learndatasci.com/tutorials/reinforcement-q-learning-scratch-python-openai-gym/ ,
#http://kvfrans.com/simple-algoritms-for-solving-cartpole/
#,Whearas changes have been made accordinlgly