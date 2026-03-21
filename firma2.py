import streamlit as st
import numpy as np

st.title('Firm Equilibrium Simulation')

# Input parameters
price = st.slider('Price', 0.0, 100.0, 50.0)
quantity = st.slider('Quantity', 0, 100, 50)

# Calculate profit
cost_per_unit = st.number_input('Cost per Unit', min_value=0.0, value=20.0)
# Profit = (Price - Cost) * Quantity
profit = (price - cost_per_unit) * quantity

# Display results
st.write(f'Profit: ${profit}')

if profit > 0:
    st.success('The firm is making a profit!')
else:
    st.warning('The firm is not making a profit.')