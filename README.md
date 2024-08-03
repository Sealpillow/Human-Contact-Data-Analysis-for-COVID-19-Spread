# Epidemic-Spread-Simulation
Understanding Models and simulate it

Based on the document on https://www.nature.com/articles/s41598-023-32542-3

### Summary:

The document titled "Identify hidden spreaders of pandemic over contact tracing networks" focuses on identifying asymptomatic and presymptomatic spreaders of COVID-19 using contact tracing networks. Here is a summary of the key points:

1. **Context and Challenge**:
   - COVID-19's spread is complicated by asymptomatic and presymptomatic individuals who unknowingly transmit the virus.
   - Current detection methods are resource-intensive and often inefficient.

2. **Proposed Method**:
   - A theoretical framework is introduced, leveraging transition probabilities among different infectious states in a contact network.
   - This method uses a Markovian process to estimate the probability of each node (individual) being infected, based on known infected cases and network topology.

3. **Key Findings**:
   - The framework can identify hidden spreaders with high accuracy, even with incomplete contact tracing data.
   - Empirical validation using data from Singapore shows that the method outperforms several machine learning baselines and random screening approaches.
   - The model remains effective even with partial information, making it suitable for real-world applications where data may be incomplete.

4. **Practical Implications**:
   - This method allows for targeted screening and more efficient isolation of high-risk individuals, potentially improving intervention strategies.
   - It can be applied to any contact tracing network, whether manually constructed or using technological means like Bluetooth or GPS-based systems.

In conclusion, the study presents an efficient and accurate method for identifying asymptomatic and presymptomatic COVID-19 spreaders, which could significantly enhance public health responses to the pandemic.

### Asymptomatic and Presymptomatic
When someone is presymptomatic, it means they've been infected with a pathogen like a virus, but they haven't yet developed any symptoms. This period occurs before the onset of symptoms, during which the individual is infectious and capable of spreading the disease to others. Take, for example, someone who has contracted COVID-19 but has not yet experienced symptoms such as fever, cough, or fatigue. Despite feeling fine, they can unknowingly transmit the virus to others through close contact.

On the other hand, asymptomatic individuals are those who are infected with the pathogen but never develop any symptoms throughout the course of the illness. They may carry and spread the disease without ever feeling unwell themselves. An analogy for asymptomatic carriers is akin to silent carriers of a message—they can transmit the infection without any outward signs.

The challenge with both presymptomatic and asymptomatic cases lies in their potential to contribute significantly to the spread of infectious diseases. Without visible symptoms prompting isolation or testing, these individuals can inadvertently infect others, leading to wider transmission within communities. This aspect has been particularly relevant in managing the spread of COVID-19, where identifying and isolating asymptomatic and presymptomatic cases has been crucial in controlling outbreaks.

In summary, while presymptomatic individuals have been infected but not yet shown symptoms, asymptomatic individuals never display symptoms despite being carriers of the disease. Both play significant roles in the transmission dynamics of infectious diseases, underscoring the importance of testing, contact tracing, and preventive measures to curb their spread.


### SPAIR States
- **S**: Susceptible
- **E**: Exposed (infected but not yet infectious)
- **P**: Presymptomatic (infectious but not yet showing symptoms)
- **A**: Asymptomatic (infectious but not showing symptoms)
- **I**: Infected (symptomatic and infectious)
- **R**: Recovered

### Transition Rules
1. **S → E**: Susceptible individuals become exposed after contact with infectious individuals.
2. **E → P**: Exposed individuals become presymptomatic after the incubation period.
3. **P → A**: Presymptomatic individuals become asymptomatic.
4. **P → I**: Presymptomatic individuals become symptomatic.
5. **A → R**: Asymptomatic individuals recover.
6. **I → R**: Symptomatic individuals recover.

### Transition Probabilities
- S[] : Probability that a susceptible person becomes exposed after contact with an infectious individual.
- E[]: Probability that an exposed person becomes presymptomatic.
- P[]: Probability that a presymptomatic person becomes asymptomatic.
- P[]: Probability that a presymptomatic person becomes symptomatic.
- A[]: Probability that an asymptomatic person recovers.
- S[]: Probability that a symptomatic person recovers.

### Implementation

Here is the updated Python code that includes the presymptomatic state:

```python
import numpy as np
import matplotlib.pyplot as plt
import os 
import math
import random
from scipy.integrate import quad

def get_data(name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(current_dir, "./data/{}".format(name))
    edge = np.genfromtxt(path, dtype=np.int32)
    connections = {} # connections{} contains connections between person to person?
    # what is the first two column from the file?
    for (i,j) in edge[:,0:2]: # selects the first two columns to be added to connections
        if i in connections:
            connections[i].add(j)
        else:
            connections[i] = set([j])
        if j in connections:
            connections[j].add(i)
        else:
            connections[j] = set([i])
    
    sortedConnections = dict(sorted(connections.items()))
    return sortedConnections, dict(zip(sortedConnections.keys(),['S']*len(sortedConnections))) # return dictionary connections and a status dictionary where each key from connections maps to 'S'


def F(t, j, beta):
    #  from the report
    #  Ci(t)=Pi(t)+Ii(t)+Ai(t)
    #  F(t,j,β) = Cj(t)·β
    return (P[j][t] + I[j][t] + A[j][t]) * beta

# Define the PDFs f_P(t), f_I(t), and f_A(t) , just random formula
def f_P(t):
    return 0.1 * np.exp(-0.1 * t) if t >= 0 else 0  # Example PDF for P state

def f_I(t):
    return 0.2 * np.exp(-0.2 * t) if t >= 0 else 0  # Example PDF for I state

def f_A(t):
    return 0.3 * np.exp(-0.3 * t) if t >= 0 else 0  # Example PDF for A state


# Compute the CDFs F_P(d), F_I(d), and F_A(d)
def F_P(d):
    result, _ = quad(f_P, -np.inf, d)
    return result

def F_I(d):
    result, _ = quad(f_I, -np.inf, d)
    return result

def F_A(d):
    result, _ = quad(f_A, -np.inf, d)
    return result


def Beta():
    # Basic reproduction number
    basicReproNum_r0 = 3.
    # proportion of asymptomatic infected cases =  Number of asymptomatic individuals/Total number of infected individuals   
    p = sum(1 for value in statusDict.values() if value == 'A')/ sum(1 for value in statusDict.values() if value in ['P','I','A'])  
    # average time of the virus carried by infected individuals in state A
    mu_A = 20.0  
    # average time of the virus carried by infected individuals in state P
    mu_P = 1.43  
    # average time of the virus carried by infected individuals in state I
    mu_I = 8.8  
    # standard deviation of the virus carried by infected individuals in state P
    sigma_P = 0.66  
    total_connections = sum(1 for person in connectionsDict for connections in connectionsDict[person])
    avgNumNeighNet_k = total_connections/population
    avgtimesusceptible_lambda = p * mu_A + (1 - p) * (math.exp(mu_P + (sigma_P**2) / 2) + mu_I)
    beta = basicReproNum_r0 / (avgtimesusceptible_lambda * avgNumNeighNet_k)
    return beta


# update probabilities for the next day 
def update_probabilities(t):
    global S,E,P,A,I,R
    d = 2 # not sure how to determine duration length d
    # proportion of asymptomatic infected cases =  Number of asymptomatic individuals/Total number of infected individuals
    # 15%?
    p = sum(1 for value in statusDict.values() if value == 'A')/ sum(1 for value in statusDict.values() if value in ['P','I','A'])  
    for i in range(population):
        personStatus = statusDict[i]
        if personStatus == 'S':  # if person in S state update prob accordingly
            # S->S
            S[i][t+1] = S[i][t] * np.prod([(1 - F(t, j, Beta())) for j in connectionsDict[i]]) 
            infection_prob = 1 - np.prod([(1 - F(t, j, Beta())) for j in connectionsDict[i]])
            # S->P transition from state S at day i to state P at day i+1 
            P[i, t+1] = S[i][t] * (1-p) * infection_prob  
            # S->A
            A[i, t+1] = S[i][t] * p * infection_prob        
        if personStatus == 'P':  # if person in P state update prob accordingly
            P[i][t+1] = P[i][t] * (1 - F_P(d)) / (1 - F_P(d - 1))
            I[i][t+1] = np.sum(P[i][1:]) * (F_P(d) - F_P(d-1)) / (1 - F_P(d-1))
        if personStatus == 'I':  # if person in I state update prob accordingly
            I[i][t+1] = I[i][t] * (1 - F_I(d)) / (1 - F_I(d - 1))
            R[i][t+1] = R[i][t] +  np.sum(A[i][1:]) * (F_A(d) - F_A(d-1)) / (1 - F_A(d-1)) + np.sum(I[i][1:]) * (F_I(d) - F_I(d-1)) / (1 - F_I(d-1))
        if personStatus == 'A':  # if person in A state update prob accordingly
            A[i][t+1] = A[i][t] * (1 - F_A(d)) / (1 - F_A(d - 1))
            R[i][t+1] = R[i][t] +  np.sum(A[i][1:]) * (F_A(d) - F_A(d-1)) / (1 - F_A(d-1)) + np.sum(I[i][1:]) * (F_I(d) - F_I(d-1)) / (1 - F_I(d-1))




def update_status(statusDict, day):
    new_status = statusDict.copy()
    # iterate every single person, each person in each grid[i][j]
    for person,status in statusDict.items():
        rand = random.random()  # rolling probability
        if status == 'S':                                 # Person at Susceptible state 
            if rand <  E[person][day]:                    # Probability that Susceptible becomes Presymptomatic
                new_status[person] = 'E'             
        elif status == 'E':                               # Person at Exposed state 
            if rand < P[person][day]:                     # Probability that Exposed becomes Presymptomatic
                new_status[person] = 'P'            
        elif status == 'P':                               # Person at Presymptomatic state 
            if rand < A[person][day]:                     # Probability that Presymptomatic becomes Asymptomatic
                new_status[person] = 'A'
            elif rand < A[person][day] + I[person][day]:  # Probability that Presymptomatic becomes Infectious
                new_status[person] = 'I'
        elif status == 'A':                               # Person at Asymptomatic state 
            if rand < R[person][day]:                     # Probability that Asymptomatic becomes Recovered
                new_status[person] = 'R'
        elif status == 'I':                               # Person at Infectious state 
            if rand < R[person][day]:                     # Probability that Infectious becomes Recovered
                new_status[person] = 'R'
    return new_status





# connections = {1: {2, 5, 6, 50, 51}, ..., 409: {400, 389}, 410: {400, 387, 404, 389}}
# status = {1: 'S', 2: 'S', 3: 'S', ..., 409: 'S', 410: 'S'}
connectionsDict,statusDict = get_data('infectious')

# Parameters
population = 410
days = 11

# Initialize arrays to store probabilites
# S = [[0. 0. 0. ... 0. 0. 0.], ...,[0. 0. 0. ... 0. 0. 0.]]

# probability of transitioning to that state on that day
S = np.zeros((population,days))  # Susceptible probability of remaining Susceptible the next day 
E = np.zeros((population,days))  # Exposed
P = np.zeros((population,days))  # Presymptomatic
A = np.zeros((population,days))  # Asymptomatic
I = np.zeros((population,days))  # Infectious
R = np.zeros((population,days))  # Recovered


# take note that  S, P, I, A, R, C:  are 2D array consist of individual result 
# S[1][1] is the probability that the 
# and not S[1] which means num of ppl susceptible at day 1

# ramdomize infected people
initial_exposed = [random.randint(0, population-1) for i in range(5)]  # select 5 random exposed person
# Set infected people in the grid
for exposed in initial_exposed:
    statusDict[exposed] = 'E'

# Simulation
susceptible_counts = []
exposed_counts = []
presymptomatic_counts = []
asymptomatic_counts = []
infected_counts = []
recovered_counts = []

for day in range(1, days):
    update_probabilities(day)
    statusDict = update_status(statusDict, day)
    susceptible_counts.append(sum(1 for person in statusDict for status in statusDict[person] if status == 'S'))
    exposed_counts.append(sum(1 for person in statusDict for status in statusDict[person] if status == 'E'))
    presymptomatic_counts.append(sum(1 for person in statusDict for status in statusDict[person] if status == 'P'))
    asymptomatic_counts.append(sum(1 for person in statusDict for status in statusDict[person] if status == 'A'))
    infected_counts.append(sum(1 for person in statusDict for status in statusDict[person] if status == 'I'))
    recovered_counts.append(sum(1 for person in statusDict for status in statusDict[person] if status == 'R'))
    

# Plot results
plt.plot(susceptible_counts, label='Susceptible')
plt.plot(exposed_counts, label='Exposed')
plt.plot(presymptomatic_counts, label='Presymptomatic')
plt.plot(asymptomatic_counts, label='Asymptomatic')
plt.plot(infected_counts, label='Infected')
plt.plot(recovered_counts, label='Recovered')
plt.xlabel('Days')
plt.ylabel('Population')
plt.legend()
plt.show()
```

### Explanation:

1. **Initialization**:
   - The grid is initialized with all `S` (susceptible) individuals.
   - A few random individuals are set to `E` (exposed).

2. **Neighbor Function**:
   - The `get_neighbors` function returns the valid neighboring positions for an individual.

3. **Grid Update**:
   - The `update_grid` function iterates through the grid and updates each individual's state based on the transition probabilities and neighbor influence:
     - **Susceptible (S)**: Can become exposed (E) based on contact with asymptomatic (A), presymptomatic (P), or infected (I) neighbors.
     - **Exposed (E)**: Can become presymptomatic (P) based on probability.
     - **Presymptomatic (P)**: Can become asymptomatic (A) or symptomatic (I) based on probabilities.
     - **Asymptomatic (A)**: Can recover (R) based on probability.
     - **Infected (I)**: Can recover (R) based on probability.
     - **Recovered (R)**: Remains recovered.

4. **Simulation**:
   - For each day, the grid is updated and the counts of susceptible, exposed, presymptomatic, asymptomatic, infected, and recovered individuals are recorded.

This approach extends the individual-based SEAIR model to an SEPAIR model, adding the presymptomatic state to capture more detailed disease dynamics.


The use of `random.random()` is to simulate the element of chance or randomness in the transitions between states. It helps to model the stochastic nature of disease spread, where not every susceptible individual will become infected upon exposure, but rather there is a certain probability that this will happen. Here's a bit more detail:

### Purpose of `random.random()`

1. **Simulate Probability**:
   - `random.random()` generates a random floating-point number between 0 and 1.
   - This number is used to simulate whether a probabilistic event (such as infection) occurs.

2. **Compare with Transition Probability**:
   - By comparing the generated random number to a predefined probability, we can decide if the transition should happen.
   - For example, if the probability of infection is 0.3, then there is a 30% chance that a susceptible individual will become infected when exposed to an infectious neighbor.

### How It Works

Let's break down the logic used in the model:

1. **Probability Calculation**:
   - The probability of infection given multiple infectious neighbors is calculated as `1 - (1 - P_SE) ** infectious_neighbors`.
   - This calculation considers the combined risk from all infectious neighbors.

2. **Random Number Generation**:
   - `random.random()` generates a number between 0 and 1.
   - This number represents a random event occurring, uniformly distributed across the probability space.

3. **Decision Making**:
   - By checking if `random.random() < calculated_probability`, we determine if the event (e.g., infection) happens.
   - If the random number is less than the calculated probability, the event occurs (the state changes).

### Example

Assume:
- \( P_{SE} = 0.3 \)
- An individual has 2 infectious neighbors.
- Calculated probability of infection is `1 - (1 - 0.3) ** 2 = 0.51`.

If `random.random()` generates a number less than 0.51, the individual becomes presymptomatic.

### Why Use Randomness?

Using randomness in simulations allows us to:
- Model real-world uncertainty and variability.
- Capture the probabilistic nature of disease spread.
- Perform multiple runs to observe different possible outcomes and understand the range of potential scenarios.

### Complete Code Context

Here is the part of the code using `random.random()`:

```python
def update_status(statusDict, day):
    new_status = statusDict.copy()
    # iterate every single person, each person in each grid[i][j]
    for person,status in statusDict.items():
        rand = random.random()  # rolling probability
        if status == 'S':                                 # Person at Susceptible state 
            if rand <  E[person][day]:                    # Probability that Susceptible becomes Presymptomatic
                new_status[person] = 'E'             
        elif status == 'E':                               # Person at Exposed state 
            if rand < P[person][day]:                     # Probability that Exposed becomes Presymptomatic
                new_status[person] = 'P'            
        elif status == 'P':                               # Person at Presymptomatic state 
            if rand < A[person][day]:                     # Probability that Presymptomatic becomes Asymptomatic
                new_status[person] = 'A'
            elif rand < A[person][day] + I[person][day]:  # Probability that Presymptomatic becomes Infectious
                new_status[person] = 'I'
        elif status == 'A':                               # Person at Asymptomatic state 
            if rand < R[person][day]:                     # Probability that Asymptomatic becomes Recovered
                new_status[person] = 'R'
        elif status == 'I':                               # Person at Infectious state 
            if rand < R[person][day]:                     # Probability that Infectious becomes Recovered
                new_status[person] = 'R'
    return new_status
```

In this function:
- The state of each individual is updated based on their current state and the calculated probabilities.
- Random numbers decide if a state transition happens, effectively simulating the randomness of real-life disease transmission.


Yes, in the given code snippet, `P_PA` (the probability that a presymptomatic individual becomes asymptomatic) indeed has higher priority than `P_PI` (the probability that a presymptomatic individual becomes symptomatic). This is because the `elif` condition for `P_PI` is only evaluated if the `if` condition for `P_PA` is not met.

Let's break it down:

```python
elif grid[i, j] == 'P':
    if random.random() < P_PA:
        new_grid[i, j] = 'A'
    elif random.random() < P_PI:
        new_grid[i, j] = 'I'
```

### How it works:
1. **If `grid[i, j] == 'P'`**:
   - Check the first condition: `if random.random() < P_PA`.
   - If this condition is true, the individual transitions from presymptomatic to asymptomatic (`new_grid[i, j] = 'A'`).
   - If the first condition is false, then check the second condition: `elif random.random() < P_PI`.
   - If the second condition is true, the individual transitions from presymptomatic to symptomatic (`new_grid[i, j] = 'I'`).

### Priority and Probabilities:
- **Priority**:
  - The first condition (`if random.random() < P_PA`) is always checked first.
  - The second condition (`elif random.random() < P_PI`) is only checked if the first condition fails.
- **Effect of this Priority**:
  - Even if `random.random() < P_PI` might be true, it will not be evaluated if `random.random() < P_PA` is already true.
  - This means `P_PA` has a higher priority in determining the state transition.

### Correcting the Priority Issue:
To ensure both transitions are checked independently, you should generate the random number once and use it for both checks. This way, each probability is evaluated without one taking priority over the other. Here’s how you can do it:

```python
elif grid[i, j] == 'P':
    rand = random.random()
    if rand < P_PA:
        new_grid[i, j] = 'A'
    elif rand < P_PA + P_PI:  # Ensure this doesn't overlap with the first condition
        new_grid[i, j] = 'I'
```

In this corrected version:
- A single random number `rand` is generated.
- If `rand` is less than `P_PA`, the individual becomes asymptomatic.
- If `rand` is between `P_PA` and `P_PA + P_PI`, the individual becomes symptomatic.

This ensures the probabilities are evaluated in a non-prioritized manner. Note that the sum of `P_PA` and `P_PI` should be less than or equal to 1 to avoid overlaps.

Example:

- **rand = 0.5**
- **P_PA = 0.2**
- **P_PI = 0.4**

### Conditions:

1. **First Condition**:
   ```python
   if rand < P_PA:
   ```
   - `rand < 0.2`
   - For `rand = 0.5`, this condition is **not** satisfied because 0.5 is not less than 0.2.
   - This means the transition to `A` (asymptomatic) does not occur.

2. **Second Condition**:
   ```python
   elif rand < P_PA + P_PI:
   ```
   - `rand < 0.2 + 0.4`
   - `rand < 0.6`
   - For `rand = 0.5`, this condition **is** satisfied because 0.5 is less than 0.6.
   - This means the transition to `I` (symptomatic) occurs.

### Conclusion:

- If `rand` falls between 0 and 0.2 (the range defined by `P_PA`), the presymptomatic individual becomes asymptomatic.
- If `rand` falls between 0.2 and 0.6 (the range defined by `P_PI`), the presymptomatic individual becomes symptomatic.
- This ensures that the probabilities are checked correctly without giving one priority over the other.

### Important Note:
Make sure that the sum of `P_PA` and `P_PI` does not exceed 1 to ensure the probabilities are valid and do not overlap improperly. If there are any other states or transitions, their probabilities should be adjusted accordingly.

