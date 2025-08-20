import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Test App",
    page_icon="🧪",
    layout="centered"
)

# Header
st.title("🧪 Streamlit Test App")
st.write("This is a simple test to verify Streamlit is working correctly!")

# Test basic functionality
st.header("Basic Tests")

# Test 1: Text input
name = st.text_input("Enter your name:", "World")
st.write(f"Hello, {name}! 👋")

# Test 2: Number input
age = st.number_input("Enter your age:", min_value=0, max_value=120, value=25)
st.write(f"You are {age} years old!")

# Test 3: Selectbox
favorite_color = st.selectbox(
    "What's your favorite color?",
    ["Red", "Blue", "Green", "Yellow", "Purple", "Orange"]
)
st.write(f"Your favorite color is {favorite_color}!")

# Test 4: Slider
temperature = st.slider("How hot is it today?", 0, 50, 20)
st.write(f"Temperature: {temperature}°C")

# Test 5: Button
if st.button("Click me!"):
    st.balloons()
    st.success("🎉 Button clicked successfully!")

# Test 6: Data display
st.header("Data Display Test")

# Create sample data
data = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
    'Age': [25, 30, 35, 28],
    'City': ['New York', 'London', 'Paris', 'Tokyo'],
    'Score': [85, 92, 78, 95]
})

st.write("Sample DataFrame:")
st.dataframe(data)

# Test 7: Chart
st.header("Chart Test")
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['A', 'B', 'C']
)

st.line_chart(chart_data)

# Test 8: File upload
st.header("File Upload Test")
uploaded_file = st.file_uploader("Choose a file", type=['txt', 'csv', 'py'])

if uploaded_file is not None:
    st.write("File uploaded successfully!")
    st.write(f"Filename: {uploaded_file.name}")
    st.write(f"File size: {uploaded_file.size} bytes")

# Test 9: Sidebar
st.sidebar.header("Test Controls")
sidebar_option = st.sidebar.radio(
    "Choose an option:",
    ["Option 1", "Option 2", "Option 3"]
)

st.sidebar.write(f"Selected: {sidebar_option}")

# Test 10: Columns
st.header("Layout Test")
col1, col2 = st.columns(2)

with col1:
    st.write("Left column")
    st.metric("Temperature", "24°C", "2°C")

with col2:
    st.write("Right column")
    st.metric("Humidity", "65%", "-5%")

# Success message
st.success("✅ All tests completed! Streamlit is working correctly!")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit")
