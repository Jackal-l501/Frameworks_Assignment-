# cord19_analysis.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from datetime import datetime
import re

# Set style for visualizations
plt.style.use('default')
sns.set_palette("husl")

def load_data(filepath):
    """Load the metadata CSV file into a pandas DataFrame"""
    print("Loading data...")
    df = pd.read_csv(filepath)
    print(f"Data loaded successfully. Shape: {df.shape}")
    return df

def basic_exploration(df):
    """Perform basic data exploration"""
    print("\n=== BASIC DATA EXPLORATION ===")
    
    # DataFrame dimensions
    print(f"DataFrame dimensions: {df.shape[0]} rows, {df.shape[1]} columns")
    
    # Data types
    print("\nData types:")
    print(df.dtypes)
    
    # Check for missing values
    print("\nMissing values in important columns:")
    important_cols = ['title', 'abstract', 'publish_time', 'journal', 'authors']
    missing_data = df[important_cols].isnull().sum()
    print(missing_data)
    
    # Basic statistics for numerical columns
    print("\nBasic statistics:")
    print(df.describe())
    
    return missing_data

def clean_data(df):
    """Clean and prepare the data for analysis"""
    print("\n=== DATA CLEANING AND PREPARATION ===")
    
    # Create a copy to avoid modifying the original
    df_clean = df.copy()
    
    # Handle missing values
    print("Handling missing values...")
    
    # For title, we'll drop rows with missing values
    initial_count = len(df_clean)
    df_clean = df_clean.dropna(subset=['title'])
    print(f"Dropped {initial_count - len(df_clean)} rows with missing titles")
    
    # For abstract, we'll fill with empty string
    df_clean['abstract'] = df_clean['abstract'].fillna('')
    
    # For publish_time, we'll extract what we can and drop the rest
    df_clean = df_clean.dropna(subset=['publish_time'])
    
    # Convert publish_time to datetime and extract year
    print("Converting dates and extracting years...")
    df_clean['publish_time'] = pd.to_datetime(df_clean['publish_time'], errors='coerce')
    df_clean = df_clean.dropna(subset=['publish_time'])
    df_clean['year'] = df_clean['publish_time'].dt.year
    
    # Create abstract word count column
    print("Creating abstract word count...")
    df_clean['abstract_word_count'] = df_clean['abstract'].apply(lambda x: len(str(x).split()))
    
    print(f"Cleaned data shape: {df_clean.shape}")
    return df_clean

def analyze_data(df):
    """Perform data analysis and create visualizations"""
    print("\n=== DATA ANALYSIS ===")
    
    # Count papers by publication year
    yearly_counts = df['year'].value_counts().sort_index()
    
    # Identify top journals
    top_journals = df['journal'].value_counts().head(10)
    
    # Find most frequent words in titles
    all_titles = ' '.join(df['title'].dropna().astype(str))
    words = re.findall(r'\w+', all_titles.lower())
    word_freq = pd.Series(words).value_counts().head(20)
    
    # Remove common stop words
    stop_words = {'the', 'of', 'and', 'in', 'to', 'a', 'for', 'on', 'with', 'by', 'an', 'from', 'as', 'at', 'is', 'that', 'this', 'are', 'be', 'which'}
    word_freq = word_freq[~word_freq.index.isin(stop_words)]
    
    return yearly_counts, top_journals, word_freq

def create_visualizations(df, yearly_counts, top_journals, word_freq, save_path="./visualizations/"):
    """Create and save visualizations"""
    print("\n=== CREATING VISUALIZATIONS ===")
    
    import os
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    
    # Plot number of publications over time
    plt.figure(figsize=(12, 6))
    yearly_counts.plot(kind='bar', color='skyblue')
    plt.title('Number of COVID-19 Publications by Year')
    plt.xlabel('Year')
    plt.ylabel('Number of Publications')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{save_path}publications_by_year.png")
    plt.close()
    
    # Create a bar chart of top publishing journals
    plt.figure(figsize=(12, 8))
    top_journals.plot(kind='barh', color='lightcoral')
    plt.title('Top 10 Journals Publishing COVID-19 Research')
    plt.xlabel('Number of Publications')
    plt.tight_layout()
    plt.savefig(f"{save_path}top_journals.png")
    plt.close()
    
    # Generate a word cloud of paper titles
    all_titles = ' '.join(df['title'].dropna().astype(str))
    wordcloud = WordCloud(width=800, height=400, background_color='white').generate(all_titles)
    
    plt.figure(figsize=(12, 6))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud of Paper Titles')
    plt.tight_layout()
    plt.savefig(f"{save_path}title_wordcloud.png")
    plt.close()
    
    # Plot distribution of paper counts by source (using publishers as proxy)
    sources = df['journal'].value_counts().head(15)
    plt.figure(figsize=(12, 8))
    sources.plot(kind='bar', color='lightgreen')
    plt.title('Distribution of Papers by Journal (Top 15)')
    plt.xlabel('Journal')
    plt.ylabel('Number of Papers')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{save_path}papers_by_journal.png")
    plt.close()
    
    print(f"Visualizations saved to {save_path}")

def main():
    """Main function to run the analysis"""
    try:
        # Load the data
        df = load_data('data/metadata.csv')
        
        # Perform basic exploration
        missing_data = basic_exploration(df)
        
        # Clean and prepare the data
        df_clean = clean_data(df)
        
        # Analyze the data
        yearly_counts, top_journals, word_freq = analyze_data(df_clean)
        
        # Create visualizations
        create_visualizations(df_clean, yearly_counts, top_journals, word_freq)
        
        print("\n=== ANALYSIS COMPLETE ===")
        print("Key findings:")
        print(f"- Data covers publications from {yearly_counts.index.min()} to {yearly_counts.index.max()}")
        print(f"- Peak publication year: {yearly_counts.idxmax()} with {yearly_counts.max()} papers")
        print(f"- Top journal: {top_journals.index[0]} with {top_journals.iloc[0]} papers")
        print(f"- Most common word in titles: '{word_freq.index[0]}' (appears {word_freq.iloc[0]} times)")
        
    except FileNotFoundError:
        print("Error: The data file was not found. Please make sure 'data/metadata.csv' exists.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()