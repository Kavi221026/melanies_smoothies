import streamlit as stMore actions
from snowflake.snowpark.functions import col
import requests

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
my_dataframe = session.table('smoothies.public.fruit_options').select(col('FRUIT_NAME'),col('SEARCH_ON'))
# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

pd_df=my_dataframe.to_pandas()
st.dataframe(pd_df)
st.stop()

# Fruit selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe,
    max_selections=5
)

# Order processing
if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/"+fruit_chosen)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Submit button
    if st.button('Submit Order'):
        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string}')
        """
        session.sql(my_insert_stmt).collect()
        st.success('Your smoothie has been ordered!')

