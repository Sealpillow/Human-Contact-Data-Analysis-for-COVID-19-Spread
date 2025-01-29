# Epidemic-Spread-Simulation
Understanding Models and simulate it

Based on the document on https://www.nature.com/articles/s41598-023-32542-3

# Identifying Hidden Spreaders in COVID-19 Contact Networks  
*A Network-Based Epidemiological Analysis Using a Modified SPAIR Model*  
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

Here’s the refined **Model Dynamics** section with transition probabilities explicitly included:  

---

2. **Proposed Method**:
   - A theoretical framework is introduced, leveraging transition probabilities among different infectious states in a contact network.
   - This method uses a Markovian process to estimate the probability of each node (individual) being infected, based on known infected cases and network topology.

## 🧬 Model Dynamics  
### Key Equations & Parameters  
To identify hidden spreaders, we introduce a **network-based probabilistic approach** that models transitions between infectious states using **transition probabilities** and **network topology**.  

- A **Markovian process** governs state transitions in the **SPAIR model** (Susceptible, Presymptomatic, Asymptomatic, Infectious, Recovered).  
- Each node (individual) has a probability of **changing states** based on infection likelihood, recovery rates, and external interventions (e.g., vaccination, isolation).  
- Using known infected individuals, we estimate **hidden spreaders** by analyzing **indirect transmission pathways** in the network.  

#### **1. Transition Supporting Formula**  
$P_i(t)$ - Probability that an individual is in Presymtomatic state </br>
$I_i(t)$ - Probability that an individual is in Infectious state  </br>
$A_i(t)$ - Probability that an individual is in Asymtomatic state </br>

| Description | Formula |
|------------|-------------|
| Infected Probability | $C_i(t) = P_i(t) + I_i(t) + A_i(t)$ |
| Infection Probability To A Single Neighbou | $F(t, j, \beta) = C_j(t) \cdot \beta$ |
| Probability Of Not Infected By All Neighbour | $\prod\limits_{j \in \partial_i} \left( 1 - F(t, j, \beta) \right)$ |
| Probability Of Infected By Any Neighbour | $1 - \prod\limits_{j \in \partial_i} \left( 1 - F(t, j, \beta) \right)$   |
| Transmission probability | $\beta = \frac{R_0}{\lambda(k)}$ |
| Average time a susceptible person carries the virus | $\lambda = p \cdot \mu_A + (1 - p) \cdot \left( \exp\left( \mu_p + \frac{\sigma_p^2}{2} \right) + \mu_I \right)$ |


#### **2. Transition Probabilities**  
Each infected individual progresses through different states with assigned probabilities:  

| Transition | Description | Probability |
|------------|------------|-------------|
| \( S \to P \) | Presymptomatic to Infectious | $P^1_i(t+1) = S_i(t) \cdot (1 - p) \cdot \left( 1 - \prod\limits_{j \in \partial_i} \left( 1 - F(t, j, \beta) \right) \right)$ |
| \( P \to A \) | Presymptomatic to Asymptomatic | \( P_A = 0.15 \) |
| \( I \to R \) | Infectious to Recovered | \( P_R = 1 - e^{-\gamma} \) |
| \( A \to R \) | Asymptomatic to Recovered | \( P_{AR} = 1 - e^{-\gamma_A} \) |

where:  
- \( P_{PI} + P_A = 1 \) (infected individuals either develop symptoms or remain asymptomatic).  
- \( \gamma, \gamma_A \) = Recovery rates for symptomatic and asymptomatic individuals, respectively.  


#### **3. Vaccination Impact**  
Vaccination modifies an individual’s susceptibility and reduces overall network transmission:  
\[
R_0^{\text{eff}} = R_0 (1 - v e)
\]  
where:  
- \( v \) = Fraction of vaccinated individuals.  
- \( e \) = Vaccine efficacy.  

#### **4. Isolation Effects**  
Isolation removes infected individuals from the network, reducing effective transmission:  
\[
P_{\text{transmit, isolated}} = (1 - \delta) P_{\text{transmit, active}}
\]  
where \( \delta \) represents isolation effectiveness.  

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





