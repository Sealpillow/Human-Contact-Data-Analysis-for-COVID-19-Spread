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


In this function:
- The state of each individual is updated based on their current state and the calculated probabilities.
- Random numbers decide if a state transition happens, effectively simulating the randomness of real-life disease transmission.




