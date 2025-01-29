# Identifying Hidden Spreaders in COVID-19 Contact Networks  
*A Network-Based Epidemiological Analysis Using a Modified SPAIR Model*  
Based on the document on https://www.nature.com/articles/s41598-023-32542-3
---

## 📌 Overview  
This repository presents a computational framework to identify **hidden spreaders**—asymptomatic, or highly connected individuals driving COVID-19 transmission—by analyzing human contact networks. </br>
The study leverages a modified **SPAIR model** (Susceptible, Presymptomatic, Asymptomatic, Infectious, Recovered) and synthetic contact networks to simulate disease dynamics under diverse scenarios, including:  
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
To identify hidden spreaders, we introduce a **network-based probabilistic approach** that models transitions between infectious states using **transition probabilities** and **network topology**.  

- A **Markovian process** governs state transitions in the **SPAIR model** (Susceptible, Presymptomatic, Asymptomatic, Infectious, Recovered).  
- Each node (individual) has a probability of **changing states** based on infection likelihood, recovery rates, and external interventions (e.g., vaccination, isolation).  
- Using known infected individuals, we estimate **hidden spreaders** by analyzing **indirect transmission pathways** in the network.  

| Parameter       | Description                          | Value/Range      |  
|:---------------:|:----------------------------------:|:------------------:|  
|$R_0$| Basic reproduction number           | 3.5 (baseline)   |  
| $p$          | Asymptomatic fraction               | 15%              |  
| Vaccination rate| Daily immunization coverage         | 1–10% of population |  
| Intervention day| Start day for vaccination/isolation | 15–30 (post-outbreak)|  

#### **1. Transition Supporting Formula**  
$P_i(t)$ - Probability that an individual is in Presymtomatic state </br>
$I_i(t)$ - Probability that an individual is in Infectious state  </br>
$A_i(t)$ - Probability that an individual is in Asymtomatic state </br>

| Description | Formula |
|:------------:|:-------------:|
| Infected Probability | $C_i(t) = P_i(t) + I_i(t) + A_i(t)$ |
| Infection Probability To A Single Neighbou | $F(t, j, \beta) = C_j(t) \cdot \beta$ |
| Probability Of Not Infected By All Neighbour | $\prod\limits_{j \in \partial_i} \left( 1 - F(t, j, \beta) \right)$ |
| Probability Of Infected By Any Neighbour | $1 - \prod\limits_{j \in \partial_i} \left( 1 - F(t, j, \beta) \right)$ |
| Transmission probability | $\beta = \frac{R_0}{\lambda(k)}$ |
| Average time a susceptible person carries the virus | $\lambda = p \cdot \mu_A + (1 - p) \cdot \left( \exp\left( \mu_p + \frac{\sigma_p^2}{2} \right) + \mu_I \right)$ |


#### **2. Transition Probabilities**  
Each infected individual progresses through different states with assigned probabilities:  

| Transition | Description | Probability |
|:------------:|:------------:|:-------------:|
| S → P | Susceptible to Presymptomatic | $P_i(t+1) = S_i(t) \cdot (1 - p) \cdot \left( 1 - \prod\limits_{j \in \partial_i} \left( 1 - F(t, j, \beta) \right) \right)$ |
| S → A | Susceptible to Asymptomatic | $A_i(t+1) = S_i(t) \cdot p \cdot \left( 1 - \prod\limits_{j \in \partial_i} \left( 1 - F(t, j, \beta) \right) \right)$ |
| S → S | Remain Susceptible | $S_i(t+1) = 1 - P_i(t+1)- A_i(t+1)$ |
| P → I | Presymptomatic to Infectious | $I_i(t+1) = \sum\limits_{d=1}^{\infty} P_i \cdot \left( \frac{F_P(d) - F_P(d-1)}{1 - F_P(d-1)} \right)$ |
| P → P | Remain Presymptomatic | $P_i(t+1) = 1 - I_i(t+1)$ |
| I → R | Infectious to Recovered | $R_i(t+1) = R_i(t) + \sum\limits_{d=1}^{\infty} I_i \cdot \left( \frac{F_I(d) - F_I(d-1)}{1 - F_I(d-1)} \right)$ |
| I → I | Remain Infectious | $I_i(t+1) = 1 - R_i(t+1)$ |
| A → R | Infectious to Recovered | $R_i(t+1) = R_i(t) + \sum\limits_{d=1}^{\infty} A_i \cdot \left( \frac{F_A(d) - F_A(d-1)}{1 - F_A(d-1)} \right)$ |
| A → A | Remain Infectious | $A_i(t+1) = 1 - R_i(t+1)$ |

where:  
- k is the average number of neighbors in the contact tracing network
- λ is the average time a susceptible person carries the virus
- FP(d), FI(d), and FA(d) are the cumulative distribution functions of the duration length d for the respective states.
- $∂_i$ represents the set of neighbors of i in the network, and F(t,j,β) is the probability that i is infected by j on day t.
- $\mu_A$, $\exp\left(\mu_p + \frac{\sigma_p^2}{2}\right)$, $\mu_I$ are the average time of the virus carried by infected individuals in A, P, and I states respectively.


#### **3. Vaccination Impact**  
Vaccination modifies an individual’s susceptibility and reduces overall network transmission:  
$R_0 = R_0 \ (1 - \text{Vaccination Effectiveness})$

#### **4. Isolation Effects**  
Isolation removes individuals in infectious state from the network, reducing effective transmission:  

#### **5. Age-Based Connection Network**  
Individual Connections are generated based age group connections </br>
<img src="https://github.com/user-attachments/assets/ed057939-d416-4210-ab01-d399a48c1430" alt="image" width="700"/> </br>

when Age Factor is not considered, connection is assigned using normal distribution of the largest standard deviation/mean Age Group (10-14)


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


## 📂 Repository Structure  
This repository is organized into the following folders and files:  

### **`data/`**  
Contains synthetic contact network datasets used in the simulations. These networks are generated based on real-world demographic data and include:  
- `static_network.csv`: A fixed contact network where connections remain constant throughout the simulation.  
- `dynamic_network.csv`: A dynamic contact network where connections change daily, reflecting real-world variability in human interactions.  
- `age_network.csv`: An age-structured contact network where interactions are clustered by demographic groups (e.g., age 0–25, 25–44, etc.).  

### **`simulations/`**  
Contains the core scripts for running the SPAIR model and generating results:  
- `spair_model.py`: The main script for simulating disease spread using the modified SPAIR model. It includes probabilistic state transitions and supports various network types.  
- `network_generator.py`: A script for generating synthetic contact networks based on user-defined parameters (e.g., population size, age distribution).  
- `intervention.py`: A script for simulating vaccination and isolation interventions, including timing and coverage effects.  

### **`figures/`**  
Stores visualizations and analysis results:  
- `infection_curves/`: Graphs showing the progression of infections over time under different scenarios.  
- `heatmaps/`: Heatmaps visualizing contact frequencies between age groups.  
- `peak_analysis/`: Analysis of infection peaks and their timing under varying intervention strategies.  

### **Other Files**  
- `LICENSE`: The license file for the project (MIT License).  
- `README.md`: Overview of the project, instructions, and repository structure.  


