import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# Title and description
st.title(':cup_with_straw: Customize Your Smoothie! :cup_with_straw:')
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input('Name for your smoothie order:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake and fetch fruit data
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table('smoothies.public.fruit_options').select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert to Pandas DataFrame for .loc lookup
pd_df = my_dataframe.to_pandas()

# Fruit selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'],
    max_selections=5
)

# Process order
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Correct casing of column name here
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Show nutrition info
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Submit order
    if st.button('Submit Order'):
        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string.strip()}')
        """
        session.sql(my_insert_stmt).collect()
        st.success('Your smoothie has been ordered!')
