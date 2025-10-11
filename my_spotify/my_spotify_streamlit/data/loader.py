import streamlit as st
import pandas as pd
import utils.constants as c


@st.cache_data
def load_songs() -> pd.DataFrame:
    conn = st.connection("postgresql", type="sql")
    sql_query = c.SQL_QUERY_SONGS
    return conn.query(sql_query, ttl=600)


@st.cache_data
def load_trend_data() -> pd.DataFrame:
    conn = st.connection("postgresql", type="sql")
    sql_query = c.SQL_QUERY_TREND
    return conn.query(sql_query, ttl=600)
