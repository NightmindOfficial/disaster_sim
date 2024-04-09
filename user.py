import streamlit as st

# Ensure the data structure is correctly initialized
if 'historical_data' not in st.session_state or not isinstance(st.session_state['historical_data'], list):
    st.session_state['historical_data'] = [
        {
            'Round': 1,
            'Participants': {
                'Me': {'Requested': 50, 'Supplied': 40, 'Sales': 40, 'Revenue': 800, 'Costs': 400, 'Profit': 400},
                'Competitor 1': {'Requested': 60, 'Supplied': 50, 'Sales': 50, 'Revenue': 1000, 'Costs': 500, 'Profit': 500},
                'Competitor 2': {'Requested': 30, 'Supplied': 30, 'Sales': 30, 'Revenue': 600, 'Costs': 300, 'Profit': 300},
            }
        },
        # Add more rounds as needed
    ]

for round_data in st.session_state['historical_data']:
    if 'Round' in round_data and 'Participants' in round_data and isinstance(round_data['Participants'], dict):
        st.markdown(f"### Round {round_data['Round']}")

        participants = round_data['Participants']
        for participant_name, metrics in participants.items():
            if isinstance(metrics, dict):
                with st.container():
                    st.write(f"**{participant_name}**")
                    col1, col2 = st.columns(2)
                    
                    col1.metric("Requested", f"{metrics.get('Requested', 0)} units")
                    col2.metric("Supplied", f"{metrics.get('Supplied', 0)} units", delta=f"{metrics.get('Supplied', 0) - metrics.get('Requested', 0)} units")
                    
                    st.text(f"Sales: {metrics.get('Sales', 0)} units")
                    st.text(f"Revenue: ${metrics.get('Revenue', 0)}")
                    st.text(f"Costs: ${metrics.get('Costs', 0)}")
                    
                    profit = metrics.get('Profit', 0)
                    profit_color = "green" if profit > 0 else "red"
                    st.metric("Profit",f"<span style='color: {profit_color};${profit}</span>",)
                    
                    st.markdown("---")  # Separator for visual clarity
            else:
                st.error("Participant metrics should be a dictionary.")
    else:
        st.error("Each round data should include 'Round' and 'Participants' keys.")
