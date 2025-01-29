# Epidemic-Spread-Simulation
Understanding Models and simulate it

Based on the document on https://www.nature.com/articles/s41598-023-32542-3

# Identifying Hidden Spreaders in COVID-19 Contact Networks  
*A Network-Based Epidemiological Analysis Using a Modified SPAIR Model*  

![Contact Network Visualization](https://via.placeholder.com/800x400.png?text=Contact+Network+Heatmap)  
*Example of an age-structured contact network heatmap used in simulations.*

---

## 📌 Overview  
This repository presents a computational framework to identify **hidden spreaders**—asymptomatic, presymptomatic, or highly connected individuals driving COVID-19 transmission—by analyzing human contact networks. The study leverages a modified **SPAIR model** (Susceptible, Presymptomatic, Asymptomatic, Infectious, Recovered) and synthetic contact networks to simulate disease dynamics under diverse scenarios, including:  
- **Network types**: Static (fixed connections), Dynamic (daily-changing interactions), Age-structured (demographic clustering).  
- **Interventions**: Vaccination, isolation, and demographic targeting.  
- **Key parameters**: Age distribution, vaccination rate, isolation timing, and population size.  

## 🔑 Key Features  
1. **SPAIR Model Enhancements**  
   - Probabilistic state transitions (vs. duration-based transitions in traditional models).  
   - Integration of age-specific contact matrices and vaccination/isolation effects.  
2. **Synthetic Network Generation**  
   - Configurable networks based on real-world demographic data (e.g., [Mossong et al. 2008](https://doi.org/10.1371/journal.pmed.0050074)).  
   - Supports static, dynamic, and fully connected networks.  
3. **Intervention Analysis**  
   - Evaluates how timing (early vs. delayed) and coverage (1–10% daily vaccination) impact outbreak trajectories.  

---

## 🧬 Model Dynamics  
### Key Equations & Parameters  
- **Infection Probability**:  
  \[
  F(t,j,\beta) = C_j(t) \cdot \beta \quad \text{(Transmission probability from neighbor \( j \))}
  \]  
- **Vaccination Impact**:  
  Adjusted reproduction number (\( R_0 \)) based on vaccination rate and efficacy.  
- **Isolation**: Reduces transmission probability for infected individuals.  

| Parameter       | Description                          | Value/Range      |  
|-----------------|--------------------------------------|------------------|  
| \( R_0 \)       | Basic reproduction number           | 3.5 (baseline)   |  
| \( p \)         | Asymptomatic fraction               | 15%              |  
| Vaccination rate| Daily immunization coverage         | 1–10% of population |  
| Intervention day| Start day for vaccination/isolation | 15–30 (post-outbreak)|  

---

## 📊 Key Findings  
1. **Network Structure Matters**  
   - **Static networks**: Early peak (Day 25), rapid decline.  
   - **Dynamic networks**: Prolonged transmission with shifting spreaders.  
   - **Age-structured networks**: Localized outbreaks in high-connectivity cohorts (e.g., young adults).  
2. **Intervention Timing**  
   - Early vaccination (Day 15) reduces infections by **31%** vs. no intervention.  
   - Isolation post-peak (Day 25) still truncates outbreak duration by 22%.  
3. **Demographic Targeting**  
   - Prioritizing high-connectivity groups (e.g., age 25–44) disrupts superspreading hubs.  

---

## 🎯 Implications for Public Health  
- **Actionable Strategies**:  
  - Combine age-targeted vaccination with workplace/school isolation protocols.  
  - Deploy adaptive surveillance for dynamic networks (e.g., real-time contact tracing).  
- **Policy Design**:  
  - Balance urgency (early interventions) and precision (demographic focus) to protect vulnerable populations.  

---


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




