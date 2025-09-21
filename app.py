# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import re
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="CORD-19 Data Explorer",
    page_icon=":microscope:",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; color: #1f77b4; margin-bottom: 1rem;}
    .section-header {font-size: 1.8rem; color: #ff7f0e; margin-top: 2rem; margin-bottom: 1rem;}
    .highlight {background-color: #f0f2f6; padding: 15px; border-radius: 5px; margin: 10px 0;}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the dataset"""
    try:
        df = pd.read_csv('data/metadata.csv')
        
        # Basic cleaning for the app
        df = df.dropna(subset=['title', 'publish_time'])
        df['publish_time'] = pd.to_datetime(df['publish_time'], errors='coerce')
        df = df.dropna(subset=['publish_time'])
        df['year'] = df['publish_time'].dt.year
        df['abstract'] = df['abstract'].fillna('')
        df['abstract_word_count'] = df['abstract'].apply(lambda x: len(str(x).split()))
        
        return df
    except FileNotFoundError:
        st.error("The data file was not found. Please make sure 'data/metadata.csv' exists.")
        return None

def main():
    """Main function for the Streamlit app"""
    st.markdown('<p class="main-header">CORD-19 Data Explorer</p>', unsafe_allow_html=True)
    st.write("Explore COVID-19 research papers from the CORD-19 dataset")
    
    # Load data
    with st.spinner('Loading data...'):
        df = load_data()
    
    if df is None:
        return
    
    # Sidebar with filters
    st.sidebar.title("Filters")
    
    # Year range slider
    min_year = int(df['year'].min())
    max_year = int(df['year'].max())
    year_range = st.sidebar.slider(
        "Select year range",
        min_year, max_year, (min_year, max_year)
    )
    
    # Journal selection
    journals = ['All'] + sorted(df['journal'].dropna().unique().tolist())
    selected_journal = st.sidebar.selectbox("Select journal", journals)
    
    # Apply filters
    filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
    if selected_journal != 'All':
        filtered_df = filtered_df[filtered_df['journal'] == selected_journal]
    
    # Display basic information
    st.markdown('<p class="section-header">Dataset Overview</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Papers", len(df))
    with col2:
        st.metric("Filtered Papers", len(filtered_df))
    with col3:
        st.metric("Time Span", f"{min_year} - {max_year}")
    with col4:
        st.metric("Unique Journals", df['journal'].nunique())
    
    # Visualizations
    st.markdown('<p class="section-header">Publications Over Time</p>', unsafe_allow_html=True)
    
    yearly_counts = filtered_df['year'].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    yearly_counts.plot(kind='bar', ax=ax, color='skyblue')
    ax.set_title('Number of Publications by Year')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Publications')
    plt.xticks(rotation=45)
    st.pyplot(fig)
    
    # Top journals
    st.markdown('<p class="section-header">Top Journals</p>', unsafe_allow_html=True)
    
    top_journals = filtered_df['journal'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(10, 6))
    top_journals.plot(kind='barh', ax=ax, color='lightcoral')
    ax.set_title('Top 10 Journals by Publication Count')
    ax.set_xlabel('Number of Publications')
    st.pyplot(fig)
    
    # Word cloud
    st.markdown('<p class="section-header">Word Cloud of Titles</p>', unsafe_allow_html=True)
    
    all_titles = ' '.join(filtered_df['title'].dropna().astype(str))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_titles)
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis('off')
    ax.set_title('Most Frequent Words in Paper Titles')
    st.pyplot(fig)
    
    # Abstract word count distribution
    st.markdown('<p class="section-header">Abstract Length Distribution</p>', unsafe_allow_html=True)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(filtered_df['abstract_word_count'], bins=50, color='lightgreen', edgecolor='black')
    ax.set_title('Distribution of Abstract Word Count')
    ax.set_xlabel('Word Count')
    ax.set_ylabel('Frequency')
    # Limit x-axis to remove extreme outliers for better visualization
    ax.set_xlim(0, 1000)
    st.pyplot(fig)
    
    # Sample data
    st.markdown('<p class="section-header">Sample Data</p>', unsafe_allow_html=True)
    
    if st.checkbox("Show sample data"):
        num_rows = st.slider("Number of rows to show", 5, 50, 10)
        st.dataframe(filtered_df[['title', 'journal', 'year', 'abstract_word_count']].head(num_rows))
    
    # Data summary
    st.markdown('<p class="section-header">Data Summary</p>', unsafe_allow_html=True)
    
    with st.expander("View data summary statistics"):
        st.write("Summary statistics for numerical columns:")
        st.write(filtered_df[['year', 'abstract_word_count']].describe())
        
        st.write("Missing values in key columns:")
        missing_data = filtered_df[['title', 'abstract', 'journal', 'authors']].isnull().sum()
        st.write(missing_data)

if __name__ == "__main__":
    main()