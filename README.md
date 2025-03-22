# Human Contact Data Analysis for COVID-19 Spread  

**A Network-Based Epidemiological Analysis Using a Modified SPAIR Model**  

---

## 📌 Overview  
This repository presents a computational framework to identify **hidden spreaders**—asymptomatic, or highly connected individuals driving COVID-19 transmission—by analyzing human contact networks. 
Building on [previous research](https://www.nature.com/articles/s41598-023-32542-3), the study utilizes a modified SPAIR model (Susceptible, Presymptomatic, Asymptomatic, Infectious, Recovered) along with synthetic contact networks to simulate disease dynamics across various scenarios, including:
- **Network types**: Static (fixed connections), Dynamic (daily-changing interactions), Age-structured (demographic clustering).  
- **Interventions**: Vaccination, isolation, and demographic targeting.  
- **Key parameters**: Age distribution, vaccination rate, isolation timing, and population size.  

## 🔑 Key Features  
1. **SPAIR Model Enhancements**  
   - Probabilistic state transitions (vs. duration-based transitions in traditional models).  
   - Integration of age-specific contact matrices and vaccination/isolation effects.
   - Explicit Consideration of Hidden Spreaders: Predicts the role of presymptomatic (P) and asymptomatic (A) individuals in transmission dynamics.
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
Contains synthetic contact network datasets used in the simulations. These networks are generated based on real-world demographic data and include and Stores visualizations figures and analysis results: 
Sure! Here are some possible descriptions for the remaining files:

- `currPlotAgeGroup.json`: Current simulation to show infection rates throughout the whole period.
- `currPlotAgeGroup.json`: Current simulation to show the distribution of age group in the population in pie chart.
- `currPlotCountConnections.json`: Current simulation histogram to show the distribution of connections within the population.
- `currPlotResult.json`: Current simulation multi line chart to show the progression of infections over time under different scenarios.
- `currStackBar.json`: Current simulation percentage stack bar chart to show the distribution of SPAIR status within the population.
- `factors.csv`: Contain information on vaccination impact factors and contact patterns for different age groups.
- `population-by-five-year-age-group.csv`: A demographic dataset that categorizes the population by five-year age group containing different countries and years.
- `previnfectionRate.json`: Previous simulation to show infection rates throughout the whole period.
- `prevPlotAgeGroup.json`: Previous simulation to show the distribution of age group in the population in pie chart.
- `prevPlotCountConnections.json`: Previous simulation histogram to show the distribution of connections within the population.
- `prevPlotResult.json`: Previous simulation multi line chart to show the progression of infections over time under different scenarios.
- `prevStackBar.json`: Previous simulation percentage stack bar chart to show the distribution of SPAIR status within the population.
- `status.json`: A json file to store value of progress and parameters used current and previously
- `infectious.csv`: A dataset containing connection between two individuals on a specific day, including their respective ages..

Let me know if you'd like any further elaboration or adjustments!


### **`assets/`**
Directory that stores additional files such as images, icons, or custom resources that is used in the dashboards.

- `style.css`: An age-structured contact network where interactions are clustered by demographic groups (e.g., age 0–25, 25–44, etc.).  
 
### **`simulations/`**  
Contains the core scripts for running the SPAIR model and generating results:  
- `countryProportion.py`: A Python script that retrieve proportion of different countries from `population-by-five-year-age-group.csv`, returning distribution of age group using the proportion.
- `DailyNetworks.py`: A Python class representing networks throughout the day.
- `DashApp.py`: A web application built with the Dash framework for creating interactive visualizations and dashboards. 
- `GenerateConnectionsCsv.py`: A Python script that generates a CSV file containing network connections for simulations.  
- `generateTable.py`: A script that generates tables of data that will be displayed on `DashApp.py`.
- `Network.py`: A Python class representing network of a single day.
- `Node.py`: A Python class or module representing nodes within a network.
- `plotGraph.py`: A script for visualizing network data, to plot graphs to be displayed on `DashApp.py`.
- `requirements.txt`: A text file listing the external Python packages and dependencies needed to run the project. It ensures that the correct versions of libraries are installed using pip install -r
- `SPAIR.py`: The main script for simulating disease spread using the modified SPAIR model. It includes probabilistic state transitions and supports various network types.  


## Getting Started

These instructions will help you set up the project on your local machine.

### Prerequisites
- Install [Python](https://www.python.org/downloads/)
- Ensure that an IDE is installed:
  - Visual Studio Code (Recommended): Download [VS Code](https://code.visualstudio.com/Download)  

### Installation
1. Download the Zip File
2. Install dependencies:
   ```python
   pip install -r requirements.txt
   ```
---
## Usage

Step 1: Run DashApp.py
```python
python DashApp.py
```
Step 2: Copy this to browser to access application
```
http://127.0.0.1:8050/
```
Note: You may want to edit the limit or remove the limit in 'DashApp.py'. A limit is added so that this program can be run in the cloud.
```python
dcc.Input(id='population-input', type='number', value=1000, min = 20, max=200, placeholder='Enter population', className='dcc.Input',
```
Step 3: Select desired parameters and click generate </br>
<img src="https://github.com/user-attachments/assets/a1550992-70eb-4bea-9571-8ae3eaff4f3f" alt="image" width="250"/> </br>

Step 4: Wait for the network to be generated </br>
![20250322-0839-27 6510752-ezgif com-crop](https://github.com/user-attachments/assets/e7efd7eb-7718-4173-a423-a8259f80d222)

Step 5: Visualizing the simulation </br>
![Recording2025-01-30003527-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/37026bec-64ea-42c2-a87a-4d7131ca4e2b)

Step 6: Select any individual you want to obeserve e.g Node 1 </br>
![image](https://github.com/user-attachments/assets/a36271e6-6043-4310-9932-9d5aec8e70d1)

Step 7: To focus on the connection of the selected node by clicking 'Remove Non-Selected Node Connections'. and the </br>
![20250322-0844-38 1656715-ezgif com-video-to-gif-converter](https://github.com/user-attachments/assets/6f7e827d-1f54-453b-8221-e9b644283dc8)

Step 8: Click on the node at network exploration to get information of the node e.g probability to change state. </br>
![image](https://github.com/user-attachments/assets/6b9e51f5-02fc-4d93-a77d-98cdb55f16bf) </br>
![image](https://github.com/user-attachments/assets/ff1ae96f-c442-4112-8349-30dd69acc9bb) </br>

Step 9: Scroll futher down and you can see more information on the status of the displayed network to identify potential hidden spreaders (Asymtomatic)</br>
![image](https://github.com/user-attachments/assets/600ff08d-dbb5-4ccc-881f-9eb530a5c605)

Step 10: Observe the SPAIR Infection model Prediction Result </br>
![newplot (17)](https://github.com/user-attachments/assets/bd133f0b-1ec4-412e-aa79-6e0c2641f09b)

Step 11: To Compare Different parameter result. Click the 'Compare Previous' Button. </br>
A Popup window with graph will be open to compare the results </br>
![image](https://github.com/user-attachments/assets/eeaf57ae-2af2-4869-a08d-9a6ad1e03726)

Assuming prior knowledge of hidden spreaders within the model, we can test prediction methods and evaluate their effectiveness, providing a framework that, when applied in real-world scenarios
![newplot (44)](https://github.com/user-attachments/assets/01c04e93-e1f8-47d2-80e6-ebf3c36a5d8f)

- Correct Prediction Hidden Spreader: Node whose infection status matched the prediction of being a hidden spreader.
- Missed Prediction Hidden Spreader: Node incorrectly predicted not to be a hidden spreader but turned out to be one.
- Potential Hidden Spreader: Node that could potentially become a hidden spreader but hasn't yet.
- Hidden Spreader: Node spreading infection without showing symptoms (asymptomatic or presymptomatic).
- Remained Susceptible: Node that never got infected.
- Late Infection: The node became infected after day 10.
- Early Infection: The node became infected before day 10.

