"""
Data Loading and Processing Module for E-commerce Analytics

This module handles loading, cleaning, and preprocessing of e-commerce datasets
for business analytics and reporting.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import warnings

# Suppress pandas warnings for cleaner output
warnings.filterwarnings('ignore', category=pd.errors.SettingWithCopyWarning)


class EcommerceDataLoader:
    """
    A class to handle loading and preprocessing of e-commerce datasets.
    
    This class provides methods to load various e-commerce datasets,
    clean the data, and prepare it for analysis.
    """
    
    def __init__(self, data_path: str = "ecommerce_data/"):
        """
        Initialize the data loader with the path to data files.
        
        Args:
            data_path (str): Path to the directory containing CSV files
        """
        self.data_path = data_path
        self.datasets = {}
        
    def load_all_datasets(self) -> Dict[str, pd.DataFrame]:
        """
        Load all e-commerce datasets from CSV files.
        
        Returns:
            Dict[str, pd.DataFrame]: Dictionary containing all loaded datasets
        """
        dataset_files = {
            'orders': 'orders_dataset.csv',
            'order_items': 'order_items_dataset.csv',
            'products': 'products_dataset.csv',
            'customers': 'customers_dataset.csv',
            'reviews': 'order_reviews_dataset.csv',
            'payments': 'order_payments_dataset.csv'
        }
        
        for name, filename in dataset_files.items():
            try:
                self.datasets[name] = pd.read_csv(f"{self.data_path}{filename}")
                print(f"Loaded {name}: {self.datasets[name].shape}")
            except FileNotFoundError:
                print(f"Warning: {filename} not found, skipping...")
                
        return self.datasets
    
    def preprocess_dates(self, df: pd.DataFrame, date_columns: list) -> pd.DataFrame:
        """
        Convert date columns to datetime format.
        
        Args:
            df (pd.DataFrame): Input dataframe
            date_columns (list): List of column names to convert
            
        Returns:
            pd.DataFrame: Dataframe with converted date columns
        """
        df_copy = df.copy()
        for col in date_columns:
            if col in df_copy.columns:
                df_copy[col] = pd.to_datetime(df_copy[col])
        return df_copy
    
    def add_time_features(self, df: pd.DataFrame, date_column: str) -> pd.DataFrame:
        """
        Add time-based features (year, month, quarter) to dataframe.
        
        Args:
            df (pd.DataFrame): Input dataframe
            date_column (str): Name of the datetime column
            
        Returns:
            pd.DataFrame: Dataframe with added time features
        """
        df_copy = df.copy()
        if date_column in df_copy.columns:
            df_copy[f'{date_column}_year'] = df_copy[date_column].dt.year
            df_copy[f'{date_column}_month'] = df_copy[date_column].dt.month
            df_copy[f'{date_column}_quarter'] = df_copy[date_column].dt.quarter
            df_copy[f'{date_column}_day'] = df_copy[date_column].dt.day
        return df_copy
    
    def create_sales_dataset(self) -> pd.DataFrame:
        """
        Create a comprehensive sales dataset by joining order_items and orders.
        
        Returns:
            pd.DataFrame: Combined sales dataset with time features
        """
        if 'order_items' not in self.datasets or 'orders' not in self.datasets:
            raise ValueError("order_items and orders datasets must be loaded first")
        
        # Merge order items with orders
        sales_data = pd.merge(
            left=self.datasets['order_items'][['order_id', 'order_item_id', 'product_id', 'price', 'freight_value']],
            right=self.datasets['orders'][['order_id', 'customer_id', 'order_status', 
                                         'order_purchase_timestamp', 'order_delivered_customer_date']],
            on='order_id',
            how='inner'
        )
        
        # Preprocess dates
        date_columns = ['order_purchase_timestamp', 'order_delivered_customer_date']
        sales_data = self.preprocess_dates(sales_data, date_columns)
        
        # Add time features for purchase timestamp
        sales_data = self.add_time_features(sales_data, 'order_purchase_timestamp')
        
        return sales_data
    
    def filter_delivered_orders(self, sales_data: pd.DataFrame) -> pd.DataFrame:
        """
        Filter sales data to include only delivered orders.
        
        Args:
            sales_data (pd.DataFrame): Input sales dataset
            
        Returns:
            pd.DataFrame: Filtered dataset with only delivered orders
        """
        return sales_data[sales_data['order_status'] == 'delivered'].copy()
    
    def add_delivery_metrics(self, sales_data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate delivery speed and add delivery time categories.
        
        Args:
            sales_data (pd.DataFrame): Sales dataset with delivery dates
            
        Returns:
            pd.DataFrame: Dataset with delivery metrics
        """
        df_copy = sales_data.copy()
        
        # Calculate delivery speed in days
        if 'order_delivered_customer_date' in df_copy.columns and 'order_purchase_timestamp' in df_copy.columns:
            df_copy['delivery_speed_days'] = (
                df_copy['order_delivered_customer_date'] - df_copy['order_purchase_timestamp']
            ).dt.days
            
            # Categorize delivery speed
            df_copy['delivery_category'] = df_copy['delivery_speed_days'].apply(self._categorize_delivery_speed)
        
        return df_copy
    
    @staticmethod
    def _categorize_delivery_speed(days: float) -> str:
        """
        Categorize delivery speed into business-friendly categories.
        
        Args:
            days (float): Number of days for delivery
            
        Returns:
            str: Delivery category
        """
        if pd.isna(days):
            return 'Unknown'
        elif days <= 3:
            return '1-3 days'
        elif days <= 7:
            return '4-7 days'
        else:
            return '8+ days'
    
    def filter_by_date_range(self, df: pd.DataFrame, date_column: str, 
                           start_year: Optional[int] = None, end_year: Optional[int] = None,
                           start_month: Optional[int] = None, end_month: Optional[int] = None) -> pd.DataFrame:
        """
        Filter dataframe by date range.
        
        Args:
            df (pd.DataFrame): Input dataframe
            date_column (str): Name of the date column for filtering
            start_year (int, optional): Start year for filtering
            end_year (int, optional): End year for filtering
            start_month (int, optional): Start month for filtering (1-12)
            end_month (int, optional): End month for filtering (1-12)
            
        Returns:
            pd.DataFrame: Filtered dataframe
        """
        df_filtered = df.copy()
        year_col = f'{date_column}_year'
        month_col = f'{date_column}_month'
        
        if start_year and year_col in df_filtered.columns:
            df_filtered = df_filtered[df_filtered[year_col] >= start_year]
            
        if end_year and year_col in df_filtered.columns:
            df_filtered = df_filtered[df_filtered[year_col] <= end_year]
            
        if start_month and month_col in df_filtered.columns:
            df_filtered = df_filtered[df_filtered[month_col] >= start_month]
            
        if end_month and month_col in df_filtered.columns:
            df_filtered = df_filtered[df_filtered[month_col] <= end_month]
            
        return df_filtered
    
    def get_dataset_summary(self) -> Dict[str, dict]:
        """
        Get summary statistics for all loaded datasets.
        
        Returns:
            Dict[str, dict]: Summary information for each dataset
        """
        summary = {}
        for name, df in self.datasets.items():
            summary[name] = {
                'shape': df.shape,
                'columns': list(df.columns),
                'memory_usage': f"{df.memory_usage(deep=True).sum() / 1024**2:.2f} MB",
                'missing_values': df.isnull().sum().sum()
            }
        return summary


def load_and_prepare_data(data_path: str = "ecommerce_data/", 
                         target_year: Optional[int] = None,
                         comparison_year: Optional[int] = None) -> Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]:
    """
    Convenience function to load and prepare all data for analysis.
    
    Args:
        data_path (str): Path to data files
        target_year (int, optional): Primary year for analysis
        comparison_year (int, optional): Comparison year for analysis
        
    Returns:
        Tuple[pd.DataFrame, Dict[str, pd.DataFrame]]: Sales data and all datasets
    """
    loader = EcommerceDataLoader(data_path)
    datasets = loader.load_all_datasets()
    
    # Create comprehensive sales dataset
    sales_data = loader.create_sales_dataset()
    sales_delivered = loader.filter_delivered_orders(sales_data)
    sales_delivered = loader.add_delivery_metrics(sales_delivered)
    
    print(f"\nData Summary:")
    print(f"Total sales records: {len(sales_data):,}")
    print(f"Delivered orders: {len(sales_delivered):,}")
    
    if target_year:
        target_data = loader.filter_by_date_range(sales_delivered, 'order_purchase_timestamp', 
                                                start_year=target_year, end_year=target_year)
        print(f"Records for {target_year}: {len(target_data):,}")
    
    if comparison_year:
        comparison_data = loader.filter_by_date_range(sales_delivered, 'order_purchase_timestamp',
                                                    start_year=comparison_year, end_year=comparison_year)
        print(f"Records for {comparison_year}: {len(comparison_data):,}")
    
    return sales_delivered, datasets


if __name__ == "__main__":
    # Example usage
    sales_data, all_datasets = load_and_prepare_data()
    print("\nDatasets loaded successfully!")