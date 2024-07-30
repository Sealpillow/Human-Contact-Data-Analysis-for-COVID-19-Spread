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


### SEPAIR States
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
import random

# Parameters
P_SE = 0.3  # Probability that S becomes E after contact with A, P, or I
P_EP = 0.2  # Probability that E becomes P
P_PA = 0.1  # Probability that P becomes A
P_PI = 0.1  # Probability that P becomes I
P_AR = 0.05  # Probability that A recovers
P_IR = 0.05  # Probability that I recovers
days = 100
grid_size = 50  # 50x50 grid for 2500 individuals

# Initialize the grid with majority 'S' and a few 'E'
grid = np.full((grid_size, grid_size), 'S')
initial_exposed = [(random.randint(0, grid_size-1), random.randint(0, grid_size-1)) for _ in range(5)]
for (i, j) in initial_exposed:
    grid[i, j] = 'E'

def get_neighbors(x, y, size):
    neighbors = [(x-1, y), (x+1, y), (x, y-1), (x, y+1)]
    return [(i, j) for i, j in neighbors if 0 <= i < size and 0 <= j < size]

def update_grid(grid, P_SE, P_EP, P_PA, P_PI, P_AR, P_IR, grid_size):
    new_grid = grid.copy()
    for i in range(grid_size):
        for j in range(grid_size):
            if grid[i, j] == 'S':
                infectious_neighbors = sum(1 for ni, nj in get_neighbors(i, j, grid_size) if grid[ni, nj] in ['A', 'P', 'I'])
                if random.random() < 1 - (1 - P_SE) ** infectious_neighbors:
                    new_grid[i, j] = 'E'
            elif grid[i, j] == 'E':
                if random.random() < P_EP:
                    new_grid[i, j] = 'P'
            elif grid[i, j] == 'P':
                if random.random() < P_PA:
                    new_grid[i, j] = 'A'
                elif random.random() < P_PI:
                    new_grid[i, j] = 'I'
            elif grid[i, j] == 'A':
                if random.random() < P_AR:
                    new_grid[i, j] = 'R'
            elif grid[i, j] == 'I':
                if random.random() < P_IR:
                    new_grid[i, j] = 'R'
    return new_grid

# Simulation
susceptible_counts = []
exposed_counts = []
presymptomatic_counts = []
asymptomatic_counts = []
infected_counts = []
recovered_counts = []

for day in range(days):
    grid = update_grid(grid, P_SE, P_EP, P_PA, P_PI, P_AR, P_IR, grid_size)
    susceptible_counts.append(np.sum(grid == 'S'))
    exposed_counts.append(np.sum(grid == 'E'))
    presymptomatic_counts.append(np.sum(grid == 'P'))
    asymptomatic_counts.append(np.sum(grid == 'A'))
    infected_counts.append(np.sum(grid == 'I'))
    recovered_counts.append(np.sum(grid == 'R'))

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
