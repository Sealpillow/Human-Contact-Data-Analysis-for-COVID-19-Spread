# this is used to extract the hiddenspreader.txt 
# Load the content of the uploaded file and extract unique combinations of the first two columns
import pandas as pd
file_path = './data/infectious.txt'

# Read and process the file to extract the first two columns
unique_combinations = set()

with open(file_path, 'r') as file:
    for line in file:
        columns = line.strip().split()
        if len(columns) >= 2:  # Ensure there are at least two columns
            pair = (columns[0], columns[1])
            unique_combinations.add(pair)

# Sort the unique combinations for better readability
sorted_combinations = sorted(unique_combinations)
sorted_combinations[:10]  # Display the first 10 unique combinations for brevity
print(sorted_combinations)

output_file_path = './data/unique_combinations.txt'

with open(output_file_path, 'w') as output_file:
    for pair in sorted_combinations:
        output_file.write(f"{pair[0]} {pair[1]}\n")

data = pd.read_csv('./data/unique_combinations.txt', sep=" ", header=None)
data.columns = ["person1", "person2"]
data = data.sort_values(by='person1', ascending=True)
data.to_csv('./data/hiddenspreaders.csv',index=False)        