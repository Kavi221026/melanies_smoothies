# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests  # <-- moved here

# Write directly to the app
st.title(':cup_with_straw: Customize Your Smoothie! :cup_with_straw:')
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """)

# Name input example
name_on_order = st.text_input('Name for your smoothie order:')
st.write('The name on your Smoothie will be:', name_on_order)

# Snowflake session and data
cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table('smoothies.public.fruit_options').select(col('FRUIT_NAME'),col('SEARCH_ON'))
# st.dataframe(data=my_dataframe,use_container_width=True)
# st.stop()
#convert the snowpark dataframe to a python dataframe so we can use the loc function
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
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + ' Nutrition Information') 
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{fruit_chosen}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    # Submit button
    if st.button('Submit Order'):
        my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders(name_on_order, ingredients)
        VALUES ('{name_on_order}', '{ingredients_string.strip()}')
        """
        session.sql(my_insert_stmt).collect()
        st.success('Your smoothie has been ordered!')
