import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# Page title
st.title(':cup_with_straw: Customize Your Smoothie! :cup_with_straw:')
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input('Name for your smoothie order:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options from Snowflake
my_dataframe = session.table('smoothies.public.fruit_options').select(
    col('FRUIT_NAME'), col('SEARCH_ON')
)
pd_df = my_dataframe.to_pandas()

# Fruit selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),   # <-- FIXED THIS
    max_selections=5
)

# Show nutrition info for each selected fruit
if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get corresponding SEARCH_ON value
        matching_row = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen]

        if not matching_row.empty:
            search_on = matching_row['SEARCH_ON'].values[0]
            st.subheader(f"{fruit_chosen} Nutrition Information")
            
            # API call using correct search_on
            api_url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
            response = requests.get(api_url)

            if response.status_code == 200:
                sf_df = st.dataframe(data=response.json(), use_container_width=True)
            else:
                st.error("Sorry, that fruit is not in our database.")
        else:
            st.error(f"'{fruit_chosen}' not found in the database.")

    # Submit order
    if st.button('Submit Order'):
        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string.strip()}')
        """
        session.sql(my_insert_stmt).collect()
        st.success('Your smoothie has been ordered!')
