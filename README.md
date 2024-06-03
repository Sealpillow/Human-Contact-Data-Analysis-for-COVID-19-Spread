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


The model described in the document and the traditional SIR (Susceptible-Infectious-Recovered) model both aim to describe the spread of infectious diseases, but there are significant differences between them in terms of complexity, realism, and application. Here are the key differences:

### SIR Model

1. **Compartments**:
   - **Susceptible (S):** Individuals who can contract the disease.
   - **Infectious (I):** Individuals who have contracted the disease and can transmit it to others.
   - **Recovered (R):** Individuals who have recovered from the disease and are assumed to be immune.

2. **Transition Dynamics**:
   - Individuals move from S to I based on the infection rate.
   - Individuals move from I to R based on the recovery rate.

3. **Assumptions**:
   - Homogeneous mixing: Every individual has an equal probability of coming into contact with any other individual.
   - Constant rates of infection and recovery.

4. **Application**:
   - Used for basic epidemiological modeling to understand the general dynamics of an epidemic.
   - Simplified and does not account for variations in contact patterns or asymptomatic transmission.

### Extended Model for COVID-19 (Network-based SEIR-like Model)

1. **Compartments**:
   - **Susceptible (S):** Same as in SIR.
   - **Presymptomatic (P):** Infected individuals who are in the incubation period and can transmit the virus before showing symptoms.
   - **Symptomatic Infectious (I):** Same as I in SIR but specifically for symptomatic individuals.
   - **Asymptomatic Infectious (A):** Infected individuals who do not show symptoms but can still transmit the virus.
   - **Recovered (R):** Same as in SIR.

2. **Transition Dynamics**:
   - More complex transitions including S to P or A, P to I, and transitions between infectious states.
   - Uses a network-based approach to account for individual contact patterns and probabilistic transitions.

3. **Assumptions**:
   - Network heterogeneity: Individuals have varying probabilities of contact based on network structure.
   - Includes asymptomatic and presymptomatic states to reflect real-world COVID-19 transmission dynamics.
   - Probabilistic transitions based on empirical data.

4. **Application**:
   - Specifically designed for diseases like COVID-19, where asymptomatic and presymptomatic transmission is significant.
   - More accurate in real-world scenarios where contact patterns are not homogeneous.
   - Allows for targeted interventions by identifying high-risk individuals in the contact network.

### Summary of Key Differences

1. **Complexity**:
   - The SIR model is simpler with only three compartments and uniform mixing assumptions.
   - The extended model is more complex, incorporating additional states (P and A) and network-based interactions.

2. **Realism**:
   - The SIR model provides a broad, generalized view of epidemic dynamics.
   - The extended model offers a more detailed and realistic representation of COVID-19 spread, considering asymptomatic transmission and contact network structure.

3. **Application**:
   - The SIR model is suitable for basic theoretical studies and initial outbreak predictions.
   - The extended model is better suited for detailed public health interventions and policy-making during pandemics like COVID-19.

In essence, while the SIR model is useful for understanding basic epidemic dynamics, the network-based SEIR-like model described in the document is tailored to capture the complexities of COVID-19 transmission, making it more applicable for practical use in controlling the pandemic.
