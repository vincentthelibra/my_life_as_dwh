import streamlit as st
import pandas as pd
import plotly.express as px
import time

st.title("Animated Timelapse Chart")

# Sample data - replace with your actual data
data = {
    "Year": list(range(2015, 2025)) * 3,
    "Category": ["Category A"] * 10 + ["Category B"] * 10 + ["Category C"] * 10,
    "Count": [
        10,
        15,
        23,
        28,
        35,
        42,
        48,
        55,
        62,
        70,  # Category A
        5,
        8,
        12,
        18,
        25,
        30,
        38,
        45,
        50,
        58,  # Category B
        15,
        18,
        20,
        25,
        28,
        32,
        35,
        40,
        45,
        52,
    ],  # Category C
}
df = pd.DataFrame(data)

# Animation controls
animation_speed = 0.01
start_animation = st.button("Start Animation")

if start_animation:
    # Create placeholder for the chart
    chart_placeholder = st.empty()

    years = sorted(df["Year"].unique())

    # Animate through years
    for i in range(1, len(years) + 1):
        # Get data up to current year
        current_data = df[df["Year"] <= years[i - 1]]

        # Create line chart
        fig = px.line(
            current_data,
            x="Year",
            y="Count",
            color="Category",
            markers=True,
            title=f"Category Counts Over Time (Up to {years[i - 1]})",
        )

        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Count",
            xaxis=dict(range=[years[0] - 0.5, years[-1] + 0.5]),
            yaxis=dict(range=[0, df["Count"].max() + 10]),
        )

        # Update the chart
        chart_placeholder.plotly_chart(fig, use_container_width=True)

        # Wait before next frame
        time.sleep(animation_speed)

    st.success("Animation complete!")

# Show full data
if st.checkbox("Show final chart"):
    fig_final = px.line(
        df, x="Year", y="Count", color="Category", markers=True, title="Complete Data"
    )
    st.plotly_chart(fig_final, use_container_width=True)
