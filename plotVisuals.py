
import matplotlib
matplotlib.use('Agg')  # Use a non-interactive backend for Flask
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from io import BytesIO
import base64
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk
import plotly
import plotly.graph_objs as go
import json
import seaborn as sns
import pandas as pd
from PIL import Image
import os
import io
# Ensure that NLTK data is downloaded
#nltk.download('punkt_tab')
#nltk.download('stopwords')
#nltk.download('vader_lexicon')
# nltk.download('punkt')
# nltk.download('stopwords')
currentDir = os.path.dirname(os.path.abspath(__file__))
'''
[{'id': '1', 'text': ['If ai speeds up work or even regularly does a single task, that displaces jobs.\n\nReduced workload -> reduced headcount'], 
  'time': [1718039224.0], 'popularity': [463], 
  'source': ['Reddit'], 
  'polarity': ['Negative'], 
  'subjectivity': ['Neutral'],
  'category': ['Technology & IT', 'Consumer Goods & Services', 'Non-Profit & Social Services', 'Manufacturing & Engineering', 'Human Resources & Talent Management'], 
  'date': ['2024-06-10'], '_version_': 1826306439897939968, '_root_': '1'},.....]
'''
def generate_placeholder_image():
    # Close all previous figures before starting a new one
    plt.close('all')
    
    """Creates a placeholder image with a message and returns it as a PIL image."""
    plt.figure(figsize=(10, 5))
    plt.text(0.5, 0.5, "No data available", fontsize=20, ha='center', va='center', color='gray')
    plt.axis("off")
    
    # Save the figure to a BytesIO object instead of a file
    img_buf = io.BytesIO()
    plt.savefig(img_buf, format='png', bbox_inches='tight')
    img_buf.seek(0)  # Rewind the buffer to the beginning
    
    # Convert the buffer to a PIL Image
    placeholder_image = Image.open(img_buf)
    
    # Close the plot to avoid display issues
    plt.close()

    return placeholder_image

def wordCloud(results):
    image_filename = "./static/visual_cache/wordcloud.png"
    image_path = os.path.join(currentDir, image_filename)

    if not results:  # Handle empty results
        # Generate the placeholder image
        placeholder_image = generate_placeholder_image()
        placeholder_image.save(image_path, format='PNG')
        return

    text = ''
    for post in results:
        text += post['text'][0]

    # Tokenize and filter stop words
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token.isalnum() and token not in stop_words]

    # Generate word frequencies
    word_freq = nltk.FreqDist(filtered_tokens)

    # Create the word cloud
    wordcloud = WordCloud(width=800, height=300, background_color='white', colormap='brg').generate_from_frequencies(word_freq)

    # Close all previous figures before starting a new one
    plt.close('all')

    # Create an image to save
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.title("Overall Word Cloud")
    # Save the figure to path
    plt.savefig(image_path, format='png', bbox_inches='tight')


import pandas as pd
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud

def word_cloud_polarity(results):
    image_filename = "./static/visual_cache/polarity_cloud.png"
    image_path = os.path.join(currentDir, image_filename)
    
    if not results:  # Handle empty results
        # Generate and save the placeholder image
        placeholder_image = generate_placeholder_image()
        placeholder_image.save(image_path, format='PNG')
        return
    
    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(results)

    # Explode the lists in the 'text' and 'polarity' columns
    df_expanded = df.explode('text')  # Exploding the 'text' column to separate entries if it's a list
    df_expanded['polarity'] = df_expanded['polarity'].explode()  # Exploding 'polarity'

    # Concatenate the text from positive and negative sentiments
    positive_text = " ".join(df_expanded[df_expanded["polarity"] == "Positive"]["text"])
    negative_text = " ".join(df_expanded[df_expanded["polarity"] == "Negative"]["text"])

    # Generate the word cloud for positive text
    if not positive_text:  # Handle no positive text
        wordcloud_positive = generate_placeholder_image()  # Generate placeholder image if no data
    else:
        wordcloud_positive = WordCloud(width=400, height=200, background_color="white", colormap="Greens").generate(positive_text)

    # Generate the word cloud for negative text
    if not negative_text:  # Handle no negative text
        wordcloud_negative = generate_placeholder_image()  # Generate placeholder image if no data
    else:
        wordcloud_negative = WordCloud(width=400, height=200, background_color="white", colormap="Reds").generate(negative_text)

    # Close all previous figures before starting a new one
    plt.close('all')
    # Create a figure to display both word clouds side by side
    plt.figure(figsize=(10, 5))

    # Plot the positive word cloud
    plt.subplot(1, 2, 1)
    plt.imshow(wordcloud_positive, interpolation='bilinear')
    plt.axis("off")
    plt.title("Positive Sentiment Word Cloud")

    # Plot the negative word cloud
    plt.subplot(1, 2, 2)
    plt.imshow(wordcloud_negative, interpolation='bilinear')
    plt.axis("off")
    plt.title("Negative Sentiment Word Cloud")

    # Save the figure to path
    plt.savefig(image_path, format='png', bbox_inches='tight')



def polarityDistribution(results):
    image_filename = "./static/visual_cache/polarity_dist.png"
    image_path = os.path.join(currentDir, image_filename)

    if not results:  # Handle empty results
        # Generate the placeholder image
        placeholder_image = generate_placeholder_image()
        placeholder_image.save(image_path, format='PNG')
        return

    # Count the number of posts for each polarity
    positive = negative = neutral = 0
    for post in results:
        if post['polarity'][0] == 'Positive':
            positive += 1 
        elif post['polarity'][0] == 'Negative':
            negative += 1
        else:  # post['polarity'][0] == 'Neutral'
            neutral += 1

    data = {
        'Positive': positive,
        'Neutral': neutral,
        'Negative': negative
    }

    # Filter out categories with 0 count
    data = {key: value for key, value in data.items() if value > 0}

    # If all categories have 0 counts, return a default empty plot
    if not data:
        return None  # Or you could return a default base64 image of an empty pie chart

    categories = list(data.keys())
    values = list(data.values())

    # Define custom colors for the pie chart (ensure color length matches remaining categories)
    color_mapping = {'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'}
    colors = [color_mapping[category] for category in categories]

    # Define a function to format value and percentage for the label
    def func(pct, allvals):
        absolute = int(pct/100.*sum(allvals))
        return f"{absolute}\n({pct:.1f}%)"

    # Create the pie chart
    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        values, 
        labels=categories, 
        autopct=lambda pct: func(pct, values),  # Custom format for both value and percentage
        startangle=90, 
        colors=colors,  # Apply filtered color list
        textprops={'color': 'black', 'fontsize': 14}
    )

    # Display percentage and value inside the chart
    for autotext in autotexts:
        autotext.set_fontsize(14)

    # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.axis('equal')

    # Title of the plot
    plt.title("Polarity Composition", fontsize=16)

    # Save the figure to path
    plt.savefig(image_path, format='png', bbox_inches='tight')


#NEW ONES 
'''
[{'id': '1', 
 'text': ['If ai speeds up work or even regularly does a single task, that displaces jobs.\n\nReduced workload -> reduced headcount'], 
 'time': [1718039224.0], 'popularity': [463], 'source': ['Reddit'], 'polarity': ['Negative'], 
 'subjectivity': ['Neutral'],
 'category': ['Technology & IT', 'Consumer Goods & Services', 'Non-Profit & Social Services', 'Manufacturing & Engineering', 'Human Resources & Talent Management'], 
 'date': ['10-06-2024'], 
 '_version_': 1827037896758001664, 
 '_root_': '1'},,.....]
'''


def sentiment_distribution_by_industry(results):
    image_filename = "./static/visual_cache/industry_sentiment.png"
    image_path = os.path.join(currentDir, image_filename)

    if not results:  # Handle empty results
        # Generate the placeholder image
        placeholder_image = generate_placeholder_image()
        placeholder_image.save(image_path, format='PNG')
        return

    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(results)

    # Explode the 'category' field into multiple rows
    df_expanded = df.explode('category')

    # Extract polarity (assuming it's a list, so taking the first element if it's a list)
    df_expanded['polarity'] = df_expanded['polarity'].apply(lambda x: x[0] if isinstance(x, list) else x)

    # Close all previous figures before starting a new one
    plt.close('all')
    # Plotting the sentiment distribution by industry
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df_expanded, x="category", hue="polarity", 
                  palette={"Positive": "green", "Neutral": "yellow", "Negative": "red"})
    plt.xticks(rotation=45, ha="right")
    plt.title("Sentiment Distribution by Industry")
    plt.xlabel("Industry")
    plt.ylabel("Count of Opinions")
    plt.legend(title="Sentiment")

    # Save the figure to path
    plt.savefig(image_path, format='png', bbox_inches='tight')




def industry_sentiment_heatmap(results):
    image_filename = "./static/visual_cache/heatmap.png"
    image_path = os.path.join(currentDir, image_filename)

    if not results:  # Handle empty results
        # Generate the placeholder image
        placeholder_image = generate_placeholder_image()
        placeholder_image.save(image_path, format='PNG')
        return
    
    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(results)

    # Exploding the 'category' field into separate rows if it's a list
    df_expanded = df.explode('category')

    # Extract polarity (assuming it's a list, so taking the first element if it's a list)
    df_expanded['polarity'] = df_expanded['polarity'].apply(lambda x: x[0] if isinstance(x, list) else x)

    # Create a pivot table to count the occurrences of each polarity for each industry
    heatmap_data = df_expanded.pivot_table(index="category", columns="polarity", aggfunc="size", fill_value=0)
    
    # Close all previous figures before starting a new one
    plt.close('all')

    # Plotting the heatmap
    plt.figure(figsize=(8, 6))
    sns.heatmap(heatmap_data, cmap="RdYlGn", annot=True, fmt="d")
    plt.title("Industry Sentiment Heatmap")
    plt.xlabel("Sentiment")
    plt.ylabel("Industry")

    # Save the figure to path
    plt.savefig(image_path, format='png', bbox_inches='tight')



def ai_sentiment_trends_across_sectors(results):
    image_filename = "./static/visual_cache/sector_trends.png"
    image_path = os.path.join(currentDir, image_filename)

    if not results:  # Handle empty results
        # Generate the placeholder image
        placeholder_image = generate_placeholder_image()
        placeholder_image.save(image_path, format='PNG')
        return
    
    # Convert the list of dictionaries into a DataFrame
    df = pd.DataFrame(results)

    # Explode the 'category' field into separate rows if it's a list
    df_expanded = df.explode('category')

    # Ensure the 'date' field is extracted properly from the list (if it's in a list)
    df_expanded['date'] = df_expanded['date'].apply(lambda x: x[0] if isinstance(x, list) else x)

    # Convert 'date' to datetime format
    df_expanded['date'] = pd.to_datetime(df_expanded['date'], format='%d-%m-%Y', errors='coerce')

    # Drop rows where 'date' could not be converted
    df_expanded = df_expanded.dropna(subset=['date'])

    # Group by 'date' and 'category', count occurrences, and unstack to get trends
    df_trend = df_expanded.groupby(["date", "category"]).size().unstack(fill_value=0)

    # Close all previous figures before starting a new one
    plt.close('all')
    # Plotting the trends across sectors
    plt.figure(figsize=(12, 6))
    for industry in df_trend.columns:
        plt.plot(df_trend.index, df_trend[industry], label=industry)

    plt.legend(title="Industry", bbox_to_anchor=(1.05, 1), loc="upper left")
    plt.xlabel("Date")
    plt.ylabel("Number of Opinions")
    plt.title("AI Sentiment Trends Across Different Job Sectors")
    plt.xticks(rotation=45)

    # Save the figure to path
    plt.savefig(image_path, format='png', bbox_inches='tight')

##  to be added to html
def source_distribution(results):
    image_filename = "./static/visual_cache/source_dist.png"
    image_path = os.path.join(currentDir, image_filename)

    if not results:  # Handle empty results
        # Generate the placeholder image
        placeholder_image = generate_placeholder_image()
        placeholder_image.save(image_path, format='PNG')
        return
    
    df = pd.DataFrame(results)
    df['source'] = df['source'].apply(lambda x: x[0] if isinstance(x, list) else x)
    # Close all previous figures before starting a new one
    plt.close('all')
    plt.figure(figsize=(10, 6))
    sns.countplot(data=df, x='source', hue='source', palette='viridis', legend=False)
    plt.title("Distribution of Opinions by Source")
    plt.xlabel("Source")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    
    # Save the figure to path
    plt.savefig(image_path, format='png', bbox_inches='tight')

def sentiment_by_source(results):
    image_filename = "./static/visual_cache/sentiment_source.png"
    image_path = os.path.join(currentDir, image_filename)

    if not results:  # Handle empty results
        # Generate the placeholder image
        placeholder_image = generate_placeholder_image()
        placeholder_image.save(image_path, format='PNG')
        return
    
    df = pd.DataFrame(results)
    df['source'] = df['source'].apply(lambda x: x[0] if isinstance(x, list) else x)
    df['polarity'] = df['polarity'].apply(lambda x: x[0] if isinstance(x, list) else x)
    
    # Create a cross-tabulation 
    cross_tab = pd.crosstab(df['source'], df['polarity'])

    # Sort the cross_tab by the total count of sentiments per source (sum of the rows)
    cross_tab = cross_tab.loc[cross_tab.sum(axis=1).sort_values(ascending=False).index]

    # Define colors for the sentiment categories
    sentiment_colors = {
        'Positive': 'green',
        'Neutral': 'gray',
        'Negative': 'red'
    }

    # Ensure the columns appear in the expected order
    expected_order = ['Positive', 'Neutral', 'Negative']
    cross_tab = cross_tab.reindex(columns=expected_order, fill_value=0)

    # Close all previous figures before starting a new one
    plt.close('all')

    # Plot the bar chart with the correct colors
    plt.figure(figsize=(10, 6))
    cross_tab.plot(kind='bar', stacked=True, color=[sentiment_colors[col] for col in expected_order])

    plt.title("Sentiment Distribution by Source")
    plt.xlabel("Source")
    plt.ylabel("Count")
    plt.xticks(rotation=45)
    plt.legend(title="Sentiment")
    
    # Save the figure to path
    plt.savefig(image_path, format='png', bbox_inches='tight')


def popularity_vs_sentiment(results):
    image_filename = "./static/visual_cache/pop_sentiment.png"
    image_path = os.path.join(currentDir, image_filename)

    if not results:  # Handle empty results
        # Generate the placeholder image
        placeholder_image = generate_placeholder_image()
        placeholder_image.save(image_path, format='PNG')
        return
    
    df = pd.DataFrame(results)
    df['popularity'] = df['popularity'].apply(lambda x: x[0] if isinstance(x, list) else x)
    df['polarity'] = df['polarity'].apply(lambda x: x[0] if isinstance(x, list) else x)
    # Close all previous figures before starting a new one 
    plt.close('all')
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='popularity', y='polarity', hue='polarity', palette={'Positive': 'green', 'Neutral': 'gray', 'Negative': 'red'})
    plt.title("Popularity vs. Sentiment")
    plt.xlabel("Popularity (Upvotes/Likes)")
    plt.ylabel("Sentiment")
    
    # Save the figure to path
    plt.savefig(image_path, format='png', bbox_inches='tight')


