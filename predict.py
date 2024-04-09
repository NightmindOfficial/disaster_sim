from sklearn.preprocessing import PolynomialFeatures
import streamlit as st
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")

supplier_capacity = 120
market_demand = 50
revenue_per_sale = 20
cost_per_item = 10

# Initialize session state for historical data if it doesn't already exist
if 'historical_data' not in st.session_state:
    st.session_state['historical_data'] = pd.DataFrame(columns=[
        'Round', 'MY ORDER', 'C1 Order', 'C2 Order', 'Total Order qty',
        'MY QTY', 'C1 QTY', 'C2 QTY',
        'Sales', 'Revenue', 'Costs', '!!! MY PROFIT',
        'C1 Sales', 'C1 Revenue', 'C1 Costs', '!!! C1 PROFIT',
        'C2 Sales', 'C2 Revenue', 'C2 Costs', '!!! C2 PROFIT'
    ])

# Function to calculate sales, revenue, costs, and profit
def calculate_metrics(supply):
    sales = min(supply, market_demand)  # Assuming fixed demand of 50 units
    revenue = sales * revenue_per_sale  # $20 revenue per unit sold
    costs = supply * cost_per_item  # $10 cost per unit ordered
    profit = revenue - costs
    return sales, revenue, costs, profit

# Function to update or add new round data along with the calculation of additional metrics
def update_add_data(round_number, my_order, competitor1_order, competitor2_order):
    total_order = my_order + competitor1_order + competitor2_order
    # Calculate supply based on total orders and supplier capacity
    my_supply = (my_order / total_order) * supplier_capacity if total_order > supplier_capacity else my_order
    comp1_supply = (competitor1_order / total_order) * supplier_capacity if total_order > supplier_capacity else competitor1_order
    comp2_supply = (competitor2_order / total_order) * supplier_capacity if total_order > supplier_capacity else competitor2_order

    # Calculate metrics for each participant
    my_sales, my_revenue, my_costs, my_profit = calculate_metrics(my_supply)
    comp1_sales, comp1_revenue, comp1_costs, comp1_profit = calculate_metrics(comp1_supply)
    comp2_sales, comp2_revenue, comp2_costs, comp2_profit = calculate_metrics(comp2_supply)

    new_data = {
        'Round': round_number,
        'MY ORDER': my_order,
        'C1 Order': competitor1_order,
        'C2 Order': competitor2_order,
        'Total Order qty': total_order,
        'MY QTY': my_supply,
        'C1 QTY': comp1_supply,
        'C2 QTY': comp2_supply,
        'Sales': my_sales, 'Revenue': my_revenue, 'Costs': my_costs, '!!! MY PROFIT': my_profit,
        'C1 Sales': comp1_sales, 'C1 Revenue': comp1_revenue, 'C1 Costs': comp1_costs, '!!! C1 PROFIT': comp1_profit,
        'C2 Sales': comp2_sales, 'C2 Revenue': comp2_revenue, 'C2 Costs': comp2_costs, '!!! C2 PROFIT': comp2_profit
    }

    if round_number in st.session_state['historical_data']['Round'].values:
        # If the round exists, update it
        st.session_state['historical_data'].loc[st.session_state['historical_data']['Round'] == round_number, list(new_data.keys())] = list(new_data.values())
    else:
        # Otherwise, add as new entry
        st.session_state['historical_data'] = pd.concat([st.session_state['historical_data'], pd.DataFrame([new_data])], ignore_index=True)


def predict_order_quantities(historical_data):
    # Assuming historical_data is a DataFrame with columns for each round's orders
    X = np.array(historical_data.index).reshape(-1, 1)  # Use rounds as the feature
    preds = {}
    for col in ['C1 Order', 'C2 Order']:
        y = historical_data[col].values
        model = LinearRegression().fit(X, y)
        next_round = np.array([[X.max() + 1]])  # Predicting the next round
        preds[col] = model.predict(next_round)[0]
    return preds['C1 Order'], preds['C2 Order']


# Function to plot regression lines for both competitors
def plot_regression_lines(historical_data):
    plt.figure(figsize=(10, 6))

    for col in ['C1 Order', 'C2 Order']:
        X = np.array(historical_data['Round']).reshape(-1, 1)  # Using 'Round' as the feature
        y = historical_data[col].values
        model = LinearRegression().fit(X, y)

        # Generating predictions for the regression line
        X_pred = np.linspace(X.min(), X.max(), 100).reshape(-1, 1)
        y_pred = model.predict(X_pred)

        # Plotting the actual orders and the regression line
        plt.scatter(X, y, label=f'Actual {col}')
        plt.plot(X_pred, y_pred, label=f'Regression Line - {col}', linestyle='--')

    plt.title('Actual Orders vs. Predicted Orders for Competitors')
    plt.xlabel('Round')
    plt.ylabel('Order Quantity')
    plt.legend()

    # Display the plot in Streamlit
    st.sidebar.pyplot(plt)

def calculate_optimal_order(pred_comp1, pred_comp2):
    optimal_quantity = -market_demand * (pred_comp1 + pred_comp2) / (market_demand-supplier_capacity)
    # Adjusting for risk: reduce/increase the order quantity based on prediction confidence
    return optimal_quantity


# Streamlit UI for input
st.sidebar.header("Disaster Simulation Strategizer")

with st.sidebar.form("new_round_data"):
    st.write("Input Data for New Round")
    round_number = st.number_input("Round Number", min_value=1, step=1)
    my_order = st.number_input("My Order", min_value=0)
    competitor1_order = st.number_input("Competitor 1 Order", min_value=0)
    competitor2_order = st.number_input("Competitor 2 Order", min_value=0)
    submit_button = st.form_submit_button("Submit New Round Data")


if submit_button:
    update_add_data(round_number, my_order, competitor1_order, competitor2_order)


# Display historical data transposed
if not st.session_state['historical_data'].empty:


    plot_regression_lines(st.session_state['historical_data'])

    # Automatically update predictions when the script reruns
    pred_comp1, pred_comp2 = predict_order_quantities(st.session_state['historical_data'])
    suggested_order = calculate_optimal_order(pred_comp1, pred_comp2)

    
    # Displaying predictions prominently
    col1, col2, col3 = st.columns(3)
    col1.metric("Predicted Order for Competitor 1", f"{pred_comp1} units")
    col2.metric("Predicted Order for Competitor 2", f"{pred_comp2} units")
    col3.metric("Suggested Order Quantity", f"{suggested_order:.2f} units", delta=f"{suggested_order - 50:.2f} units adjustment")

    sorted_historical_data = st.session_state['historical_data'].sort_values(by='Round', ascending=True)
    cleaned_data = sorted_historical_data.drop(columns=['Sales', 'C1 Sales', 'C2 Sales'])
    final_data = sorted_historical_data.set_index('Round').T


    st.table(data=final_data)



else:
    st.write("No data available. Please input data for at least one round.")


# Function to reset data
def reset_data():
    st.session_state['historical_data'] = pd.DataFrame(columns=[
        'Round', 'MY ORDER', 'C1 Order', 'C2 Order', 'Total Order qty',
        'MY QTY', 'C1 QTY', 'C2 QTY',
        'Sales', 'Revenue', 'Costs', '!!! MY PROFIT',
        'C1 Sales', 'C1 Revenue', 'C1 Costs', '!!! C1 PROFIT',
        'C2 Sales', 'C2 Revenue', 'C2 Costs', '!!! C2 PROFIT'
    ])
    st.experimental_rerun()

# Reset button
if st.sidebar.button("Reset Data"):
    reset_data()

st.info(f"""
**Assumptions:** Market Demand per Participant: {market_demand}, Maximum Supply Capacity: {supplier_capacity}, Cost per Item: {cost_per_item}, Revenue per Sale: {revenue_per_sale}""")

st.info("""
**Note:** This application provides a platform for simulating order quantities and analyzing the outcomes. 
For real-world applications, consider integrating more sophisticated predictive models and optimization algorithms.
""")
