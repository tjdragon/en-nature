import os
os.environ['TF_USE_LEGACY_KERAS'] = '1'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import tensorflow as tf
import sys
import tensorflow_recommenders as tfrs
import pandas as pd
import numpy as np
from typing import Dict, Text
from pathlib import Path

class RestaurantRecommender(tfrs.Model):
    def __init__(self, user_ids, place_ids, embedding_dimension=32):
        super().__init__()
        
        # Embeddings for users
        self.user_model = tf.keras.Sequential([
            tf.keras.layers.StringLookup(vocabulary=user_ids),
            tf.keras.layers.Embedding(len(user_ids) + 1, embedding_dimension)
        ])
        
        # Embeddings for restaurants
        self.restaurant_model = tf.keras.Sequential([
            tf.keras.layers.StringLookup(vocabulary=place_ids),
            tf.keras.layers.Embedding(len(place_ids) + 1, embedding_dimension)
        ])
        
        # Task definition
        self.task = tfrs.tasks.Retrieval(
            metrics=tfrs.metrics.FactorizedTopK(
                candidates=tf.data.Dataset.from_tensor_slices(place_ids).batch(128).map(self.restaurant_model)
            )
        )

    def compute_loss(self, features: Dict[Text, tf.Tensor], training=False) -> tf.Tensor:
        user_embeddings = self.user_model(features["user_id"])
        restaurant_embeddings = self.restaurant_model(features["place_id"])
        
        return self.task(user_embeddings, restaurant_embeddings)

def load_and_preprocess_data():
    print("Loading and preprocessing data...")
    # Read CSV files
    users_df = pd.read_csv('users.csv')
    restaurants_df = pd.read_csv('restaurants.csv')
    likes_df = pd.read_csv('likes.csv')
    
    # First merge likes with restaurants
    merged_df = likes_df.merge(restaurants_df, on='PLACE_ID', how='left')
    
    # Then merge with users
    merged_df = merged_df.merge(users_df[['USER_ID', 'AVERAGE_SPEND']], on='USER_ID', how='left')
    
    # Calculate user preference features
    user_stats = merged_df.groupby('USER_ID').agg({
        'RATING': 'mean',
        'LIKES': 'mean',
        'AVERAGE_SPEND': 'first'
    }).reset_index()
    
    merged_df = merged_df.merge(user_stats, on='USER_ID', suffixes=('', '_avg'))
    
    # Convert IDs to strings and get unique values
    unique_user_ids = merged_df["USER_ID"].astype(str).unique()
    unique_place_ids = merged_df["PLACE_ID"].astype(str).unique()
    
    # Create tensor slices with available features
    ratings_ds = tf.data.Dataset.from_tensor_slices({
        "user_id": merged_df["USER_ID"].astype(str).values,
        "place_id": merged_df["PLACE_ID"].astype(str).values,
        "likes": merged_df["LIKES"].astype(float).values,
        "rating": merged_df["RATING"].astype(float).values,
    })
    
    return ratings_ds, unique_user_ids, unique_place_ids, restaurants_df

def analyze_user_preferences(user_id, merged_df):
    """Analyze user preferences based on their interaction history"""
    user_data = merged_df[merged_df['USER_ID'] == user_id]
    
    preferences = {
        'total_interactions': len(user_data),
        'average_spend': user_data['AVERAGE_SPEND'].iloc[0] if len(user_data) > 0 else None,
        'likes_ratio': user_data['LIKES'].mean() if len(user_data) > 0 else None,
        'favorite_cuisines': user_data[user_data['LIKES']].groupby('CUISINE')['LIKES'].count().sort_values(ascending=False).head(3)
    }
    
    return preferences



# [Previous RestaurantRecommender class and load_and_preprocess_data function remain the same until the main function]

def main():
    # Load and preprocess data
    ratings_ds, unique_user_ids, unique_place_ids, restaurants_df = load_and_preprocess_data()
    
    # Create a dictionary for fast restaurant lookups
    restaurant_dict = restaurants_df.set_index('PLACE_ID').to_dict('index')
    
    # Split the data into training and testing
    tf.random.set_seed(42)
    shuffled = ratings_ds.shuffle(100_000, seed=42, reshuffle_each_iteration=False)
    
    train_size = int(0.8 * len(list(ratings_ds)))
    train = shuffled.take(train_size)
    test = shuffled.skip(train_size)
    
    cached_train = train.shuffle(10_000).batch(8192).cache()
    cached_test = test.batch(4096).cache()
    
    # Create and train the model
    model = RestaurantRecommender(unique_user_ids, unique_place_ids)
    model.compile(optimizer=tf.keras.optimizers.Adagrad(0.1))
    
    model.fit(cached_train, validation_data=cached_test, epochs=5)
    
    # Create a model for recommendations
    index = tfrs.layers.factorized_top_k.BruteForce(model.user_model)
    index.index_from_dataset(
        tf.data.Dataset.from_tensor_slices(unique_place_ids).batch(100).map(
            lambda place_id: (place_id, model.restaurant_model(place_id)))
    )
    
    # Function to get recommendations for a user
    def get_recommendations(user_id, k=5):
        # Get raw recommendations
        _, titles = index(tf.constant([str(user_id)]))
        recommended_place_ids = titles.numpy()[0, :k]
        
        # Get restaurant details
        recommendations_with_details = []
        for place_id in recommended_place_ids:
            # Convert bytes to string if necessary
            if isinstance(place_id, bytes):
                place_id = place_id.decode('utf-8')
            
            # Get restaurant details from dictionary with fallback values
            restaurant = restaurant_dict.get(place_id, {
                'RESTAURANT_NAME': 'Unknown',
                'CUISINE': 'Unknown',
                'RATING': 0
            })
            
            recommendations_with_details.append({
                'place_id': place_id,
                'name': restaurant['RESTAURANT_NAME'],
                'cuisine': restaurant['CUISINE'],
                'rating': restaurant['RATING']
            })
        
        # Load and merge data for analysis
        users_df = pd.read_csv('users.csv')
        likes_df = pd.read_csv('likes.csv')
        
        # Merge with existing restaurant dictionary
        likes_with_restaurants = []
        for _, row in likes_df.iterrows():
            place_id = row['PLACE_ID']
            restaurant = restaurant_dict.get(place_id, {
                'RESTAURANT_NAME': 'Unknown',
                'CUISINE': 'Unknown',
                'RATING': 0
            })
            likes_with_restaurants.append({
                'USER_ID': row['USER_ID'],
                'PLACE_ID': place_id,
                'LIKES': row['LIKES'],
                'CUISINE': restaurant['CUISINE'],
                'RATING': restaurant['RATING']
            })
        
        merged_df = pd.DataFrame(likes_with_restaurants)
        merged_df = merged_df.merge(users_df[['USER_ID', 'AVERAGE_SPEND']], on='USER_ID')
        
        # Get user preferences
        user_prefs = analyze_user_preferences(user_id, merged_df)
        
        return recommendations_with_details, user_prefs
    
    return model, get_recommendations

if __name__ == "__main__":
    trained_model, recommender = main()
    
    # Example usage
    user_id = "HDLW"  # Replace with actual user ID
    recommendations, user_preferences = recommender(user_id)
    
    print(f"\nUser {user_id} Preferences:")
    print(f"Total interactions: {user_preferences['total_interactions']}")
    print(f"Average spend: ${user_preferences['average_spend']}")
    print(f"Likes ratio: {user_preferences['likes_ratio']:.2f}" if user_preferences['likes_ratio'] is not None else "No likes data")
    print("\nTop favorite cuisines:")
    for cuisine, count in user_preferences['favorite_cuisines'].items():
        print(f"- {cuisine}: {count} likes")
    
    print(f"\nTop 5 restaurant recommendations:")
    for i, rec in enumerate(recommendations, 1):
        print(f"{i}. {rec['name']} ({rec['cuisine']}) - Rating: {rec['rating']}")