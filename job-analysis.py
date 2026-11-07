# =============================
# import libraries
# =============================
import pandas as pd;
import matplotlib.pyplot as plt
import numpy as np

# =============================
# load data
# =============================
data = pd.read_csv('data/usa-job-info.csv')

# =============================
#calculate salary vs cost of living for each state
# =============================
#calculate average salary for all software engineers
average_salary = data['Mean Software Developer Salary (unadjusted)'].mean()
print(f"The average salary for all software engineers is: ${average_salary:.2f}")

#calculate the difference between the average salary in a city and the average living cost in the same city
#get the state from the city column
data['State'] = data['City'].apply(lambda x: x.split(',')[-1].strip())
#calculate the average salary for each state
state_averages = data.groupby('State')['Mean Software Developer Salary (unadjusted)'].mean().reset_index()
#print(state_averages.round(2))

# =============================
#identify outliers in the data and correct them
# =============================
#calculate IQR limits
Q1 = data['Cost of Living Plus Rent avg'].quantile(0.25)
Q3 = data['Cost of Living Plus Rent avg'].quantile(0.75)
IQR = Q3 - Q1

upper_limit = Q3 + 1.5 * IQR
lower_limit = Q1 - 1.5 * IQR

#calculate replacement living costs
replacement_cost_of_living = (
    data['Cost of Living avg'] + data['Rent avg']
)

#replacing any outliers with the replacement living costs for a more accurate representation of the data
data['Corrected living cost'] = data['Cost of Living Plus Rent avg'].where(
    data['Cost of Living Plus Rent avg'].between(lower_limit, upper_limit), 
    replacement_cost_of_living
)

#calculate the average living cost for each state
state_living_costs = data.groupby('State')['Corrected living cost'].mean().reset_index()
#print(state_living_costs.round(2))

#merge the two dataframes on the state column
state_merge = pd.merge(
        state_averages, 
        state_living_costs,
        on='State', 
        how='inner'
)

#change the living cost to a total yearly cost
state_merge['Corrected living cost'] = state_merge['Corrected living cost'] * 12

#calculate the difference between the average salary and the average living cost for each state
state_merge['Salary vs Living Cost'] = state_merge['Mean Software Developer Salary (unadjusted)'] - state_merge['Corrected living cost']
#print(state_merge.round(2))

# =============================
#calculate the bottom and top states to live in and work in
# =============================
#find the top 3 states and bottom 3 states to live in and work in software
top_states = state_merge.sort_values(by='Salary vs Living Cost', ascending=False).head(3)
bottom_states = state_merge.sort_values(by='Salary vs Living Cost', ascending=True).head(3)
print("The top 3 states to live in and work in software are:")
print(top_states[['State', 'Salary vs Living Cost']].round(2))
print("The bottom 3 states to live in and work in software are:")
print(bottom_states[['State', 'Salary vs Living Cost']].round(2))

# =============================
#create graphs to represent the data
# =============================
#create a data frame for the graph
graph_data = state_merge[[
    'State',
    'Mean Software Developer Salary (unadjusted)',
    'Salary vs Living Cost'
]]

#print(graph_data.head().round(2))

#order the data for the graph 
graph_data = graph_data.sort_values(
    by='Salary vs Living Cost', 
    ascending=False
).reset_index(drop=True)

#count how many states there are for positions on the graph
x = np.arange(len(graph_data['State']))

#create the bars
bar_width = 0.25

#create first bar (average salary) 
plt.figure(figsize=(15, 7))
plt.bar(
    x - bar_width,
    graph_data['Mean Software Developer Salary (unadjusted)'],
    width=bar_width,
    label='Average Salary',
    color='blue'
)

#create third bar (difference between average salary and average living cost)
plt.bar(
    x + bar_width,
    graph_data['Salary vs Living Cost'],
    width=bar_width,
    label='Salary Remaining',
    color='purple'
)

#name the axis, graph title, and labels
plt.xticks(x, graph_data['State'], rotation=45)
plt.title('Software Developer Salary vs Cost of living in the USA')
plt.xlabel('State')
plt.ylabel('Salary ($) ')

#add a legend to the graph
plt.legend()

#finish the graph
plt.tight_layout()
plt.savefig('graphs/salary-comparison.png', dpi=300, bbox_inches='tight')
plt.show()

# =============================
#cretae a graph to represent top 3 states to live in and work in software
# =============================
# graph size
plt.figure(figsize=(10, 5))

plt.barh(
    top_states['State'], 
    top_states['Salary vs Living Cost'], 
    color='green'
)

plt.title('Top 3 States to Live in and Work in Software')
plt.xlabel('Salary Remaining ($)')
plt.ylabel('State')

plt.tight_layout()
plt.savefig('graphs/top-states.png', dpi=300, bbox_inches='tight')
plt.show()