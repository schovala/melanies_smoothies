# Import python packages
import streamlit as st
#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the Fruits you want in your custom Smoothie!.
    """
)

name_on_order = st.text_input("Name on the Smoothie:")
st.write("The Name on your smoothie will be: ", name_on_order)

cnx = st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('search_on'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop()
# convert snowpark dataframe to pandas dataframe
pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingrediants_list = st.multiselect(
    "choose upto 5 ingrediants",
    my_dataframe,
    max_selections = 5
)

if ingrediants_list:
    
    ingrediants_string = ''

    for fruit_chosen in ingrediants_list:
        ingrediants_string += fruit_chosen + ' '
        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + 'Neutrition Information')
        fruityvice_response = requests.get("https://fruityvice.com/api/fruit/"+ fruit_chosen)
        fv_df = st.dataframe (data = fruityvice_response.json(),use_container_width = True)

    #st.write(ingrediants_string)

    my_insert_stmt= """insert into smoothies.public.orders(ingredients,name_on_order) 
                        values ('""" +ingrediants_string+ """','"""+name_on_order+"""')"""
    
    st.write(my_insert_stmt)
    #st.stop()
    
    time_to_insert = st.button ("Submit Order")
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered! {name_on_order}', icon="✅")
