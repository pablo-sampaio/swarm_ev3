
import numpy as np
#import time

def play_episodes(env, agent, episodes=1, render=False, verbose=True):
    perfs = []
    total_steps = 0
    for i in range(0,episodes):
        if verbose:
            print("Episode", i+1, end="") 
        #time.sleep(2)
        obs = env.reset()
        done = False
        reward = 0.0
        steps = 0
        while not done:
            if render:
                env.render()
            action, _ = agent.choose_action(obs)
            obs, r, done = env.step(action)
            #print(r)
            #print(obs)
            reward += r
            steps += 1
            if steps >= 1000:
                break
        if render:
            env.render()
        total_steps += steps
        if verbose:
            print(" steps:", steps, ", reward:", reward)
            #print(" - last state:", obs)
        perfs.append(reward)

    if verbose:
        print("Total Results: ")
        print("mean reward:", np.mean(perfs), end="")
        print(", episodes:", len(perfs), end="")
        print(", steps:", total_steps)

    return np.mean(perfs), total_steps

print("Teste")