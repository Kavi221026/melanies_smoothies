# Import python packages
import streamlit as st
import pandas as pd
import requests
from snowflake.snowpark.functions import col

# Title
st.title(':cup_with_straw: Customize Your Smoothie! :cup_with_straw:')
st.write("Choose the fruits you want in your custom Smoothie!")

# Name input
name_on_order = st.text_input('Name for your smoothie order:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Get fruit options from Snowflake with both FRUIT_NAME and SEARCH_ON
fruit_options_df = session.table('smoothies.public.fruit_options') \
                          .select(col('FRUIT_NAME'), col('SEARCH_ON')) \
                          .to_pandas()  # convert to pandas for easier lookup

# Let user select ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    fruit_options_df['FRUIT_NAME'],
    max_selections=5
)

# Order processing
if ingredients_list:
    ingredients_string = ''

    st.subheader('Your Order Summary:')
    st.write(f'Name: {name_on_order}')
    st.write(f'Ingredients: {", ".join(ingredients_list)}')

    # For each selected fruit, get API-friendly name and call API
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get the API name from SEARCH_ON column
        search_on = fruit_options_df.loc[
            fruit_options_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'
        ].iloc[0]

        st.subheader(fruit_chosen + ' Nutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/" + search_on)
        fv_df = st.dataframe(data=fruityvice_response.json(), use_container_width=True)

    # Submit button
    if st.button('Submit Order'):
        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string.strip()}')
        """
        session.sql(my_insert_stmt).collect()
        st.success('Your smoothie has been ordered!')
