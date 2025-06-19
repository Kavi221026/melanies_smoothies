# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(':cup_with_straw: Customize Your Smoothie! :cup_with_straw:')
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """)

# Name input example (like the movie title example)
name_on_order = st.text_input('Name for your smoothie order:')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake session and data
cnx=st.connection("snowflake")
session=cnx.session()
my_dataframe = session.table('smoothies.public.fruit_options').select(col('FRUIT_NAME'))
# st.dataframe(data=my_dataframe, use_container_width=True)

# Fruit selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# Order processing
if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)
    
    # Display order summary
    st.subheader('Your Order Summary:')
    st.write(f'Name: {name_on_order}')
    st.write(f'Ingredients: {ingredients_string}')
    
    # Submit button
    if st.button('Submit Order'):
        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string}')
        """
        session.sql(my_insert_stmt).collect()
        st.success('Your smoothie has been ordered!')

import requests
smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
# st.text(smoothiefroot_response.json())
sf_df= st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

