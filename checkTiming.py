#Script to check the variation in timing during stimulus presentation in MEG

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv('extracted_data1.csv')

timing = data['Timing']

# Calculate the mean
mean_timing = timing.mean()

# Calculate the standard deviation
std_deviation = timing.std()
max = timing.max()
min = timing.min()

# Print the results
print(f"Mean Timing: {mean_timing:.2f} s")
print(f"Standard Deviation: {std_deviation:.2f} s")
print(f"Range: {min:.2f} s to {max:.2f} ")


# Set the style for the plots
sns.set(style="whitegrid")

# Create a figure with two subplots
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6))

# Plot a histogram
sns.histplot(timing, kde=True, ax=axes[0])
axes[0].set_title('Histogram of Timing')
axes[0].set_xlabel('Timing (ms)')
axes[0].set_ylabel('Frequency')

# Plot a box plot
sns.boxplot(y=timing, ax=axes[1])
axes[1].set_title('Box Plot of Timing')
axes[1].set_xlabel('Timing (ms)')

# Show the plots
plt.tight_layout()
plt.show()