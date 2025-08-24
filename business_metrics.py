"""
Business Metrics Calculation Module for E-commerce Analytics

This module contains functions to calculate key business metrics including
revenue analysis, customer metrics, product performance, and operational KPIs.
"""

import pandas as pd
import numpy as np
from typing import Dict, Tuple, Optional, List
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


class EcommerceMetrics:
    """
    A class containing methods to calculate various e-commerce business metrics.
    """
    
    @staticmethod
    def calculate_revenue_metrics(current_data: pd.DataFrame, 
                                comparison_data: pd.DataFrame = None,
                                current_period: str = "Current Period",
                                comparison_period: str = "Previous Period") -> Dict[str, float]:
        """
        Calculate revenue metrics for current period and comparison with previous period.
        
        Args:
            current_data (pd.DataFrame): Sales data for current period
            comparison_data (pd.DataFrame, optional): Sales data for comparison period
            current_period (str): Label for current period
            comparison_period (str): Label for comparison period
            
        Returns:
            Dict[str, float]: Dictionary containing revenue metrics
        """
        metrics = {
            f'{current_period}_total_revenue': current_data['price'].sum(),
            f'{current_period}_avg_order_value': current_data.groupby('order_id')['price'].sum().mean(),
            f'{current_period}_total_orders': current_data['order_id'].nunique(),
            f'{current_period}_total_items': len(current_data)
        }
        
        if comparison_data is not None:
            comp_revenue = comparison_data['price'].sum()
            comp_aov = comparison_data.groupby('order_id')['price'].sum().mean()
            comp_orders = comparison_data['order_id'].nunique()
            
            metrics.update({
                f'{comparison_period}_total_revenue': comp_revenue,
                f'{comparison_period}_avg_order_value': comp_aov,
                f'{comparison_period}_total_orders': comp_orders,
                f'{comparison_period}_total_items': len(comparison_data),
                'revenue_growth_rate': ((metrics[f'{current_period}_total_revenue'] - comp_revenue) / comp_revenue) * 100,
                'aov_growth_rate': ((metrics[f'{current_period}_avg_order_value'] - comp_aov) / comp_aov) * 100,
                'order_growth_rate': ((metrics[f'{current_period}_total_orders'] - comp_orders) / comp_orders) * 100
            })
            
        return metrics
    
    @staticmethod
    def calculate_monthly_trends(data: pd.DataFrame, year: int = None) -> pd.DataFrame:
        """
        Calculate monthly revenue trends and growth rates.
        
        Args:
            data (pd.DataFrame): Sales data with time features
            year (int, optional): Specific year to analyze
            
        Returns:
            pd.DataFrame: Monthly trends with growth rates
        """
        if year:
            data = data[data['order_purchase_timestamp_year'] == year]
        
        monthly_revenue = data.groupby('order_purchase_timestamp_month')['price'].sum()
        monthly_orders = data.groupby('order_purchase_timestamp_month')['order_id'].nunique()
        monthly_aov = data.groupby(['order_purchase_timestamp_month', 'order_id'])['price'].sum().groupby('order_purchase_timestamp_month').mean()
        
        trends = pd.DataFrame({
            'month': monthly_revenue.index,
            'revenue': monthly_revenue.values,
            'orders': monthly_orders.values,
            'avg_order_value': monthly_aov.values
        })
        
        # Calculate growth rates
        trends['revenue_growth'] = trends['revenue'].pct_change() * 100
        trends['order_growth'] = trends['orders'].pct_change() * 100
        trends['aov_growth'] = trends['avg_order_value'].pct_change() * 100
        
        return trends
    
    @staticmethod
    def analyze_product_performance(sales_data: pd.DataFrame, 
                                  products_data: pd.DataFrame,
                                  top_n: int = 10) -> Dict[str, pd.DataFrame]:
        """
        Analyze product category and individual product performance.
        
        Args:
            sales_data (pd.DataFrame): Sales transactions data
            products_data (pd.DataFrame): Product master data
            top_n (int): Number of top categories/products to return
            
        Returns:
            Dict[str, pd.DataFrame]: Product analysis results
        """
        # Merge sales with product data
        sales_products = pd.merge(
            sales_data[['product_id', 'price', 'order_id']],
            products_data[['product_id', 'product_category_name']],
            on='product_id',
            how='left'
        )
        
        # Category performance
        category_metrics = sales_products.groupby('product_category_name').agg({
            'price': ['sum', 'mean', 'count'],
            'order_id': 'nunique'
        }).round(2)
        
        category_metrics.columns = ['total_revenue', 'avg_price', 'items_sold', 'unique_orders']
        category_metrics = category_metrics.sort_values('total_revenue', ascending=False).head(top_n)
        
        # Individual product performance
        product_metrics = sales_products.groupby('product_id').agg({
            'price': ['sum', 'count'],
            'order_id': 'nunique'
        }).round(2)
        
        product_metrics.columns = ['total_revenue', 'items_sold', 'unique_orders']
        product_metrics = product_metrics.sort_values('total_revenue', ascending=False).head(top_n)
        
        return {
            'category_performance': category_metrics.reset_index(),
            'product_performance': product_metrics.reset_index()
        }
    
    @staticmethod
    def analyze_geographic_performance(sales_data: pd.DataFrame, 
                                     orders_data: pd.DataFrame,
                                     customers_data: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze sales performance by geographic regions (states).
        
        Args:
            sales_data (pd.DataFrame): Sales transactions data
            orders_data (pd.DataFrame): Orders data
            customers_data (pd.DataFrame): Customer data with geographic info
            
        Returns:
            pd.DataFrame: Geographic performance metrics
        """
        # Link sales to customers through orders
        sales_customers = pd.merge(
            sales_data[['order_id', 'price']],
            orders_data[['order_id', 'customer_id']],
            on='order_id',
            how='left'
        )
        
        # Add customer geographic data
        geo_sales = pd.merge(
            sales_customers,
            customers_data[['customer_id', 'customer_state', 'customer_city']],
            on='customer_id',
            how='left'
        )
        
        # Calculate state-level metrics
        state_metrics = geo_sales.groupby('customer_state').agg({
            'price': ['sum', 'mean', 'count'],
            'customer_id': 'nunique'
        }).round(2)
        
        state_metrics.columns = ['total_revenue', 'avg_order_value', 'total_orders', 'unique_customers']
        state_metrics = state_metrics.sort_values('total_revenue', ascending=False)
        
        return state_metrics.reset_index()
    
    @staticmethod
    def analyze_customer_satisfaction(sales_data: pd.DataFrame, 
                                    reviews_data: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        Analyze customer satisfaction metrics including delivery performance impact.
        
        Args:
            sales_data (pd.DataFrame): Sales data with delivery metrics
            reviews_data (pd.DataFrame): Customer reviews data
            
        Returns:
            Dict[str, pd.DataFrame]: Customer satisfaction analysis
        """
        # Merge sales with reviews
        sales_reviews = pd.merge(
            sales_data[['order_id', 'delivery_speed_days', 'delivery_category']],
            reviews_data[['order_id', 'review_score']],
            on='order_id',
            how='inner'
        ).drop_duplicates(subset=['order_id'])
        
        # Overall satisfaction metrics
        overall_metrics = pd.DataFrame({
            'metric': ['Average Review Score', 'Total Reviews', 'Average Delivery Days'],
            'value': [
                sales_reviews['review_score'].mean(),
                len(sales_reviews),
                sales_reviews['delivery_speed_days'].mean()
            ]
        })
        
        # Satisfaction by delivery speed
        delivery_satisfaction = sales_reviews.groupby('delivery_category').agg({
            'review_score': ['mean', 'count']
        }).round(2)
        
        delivery_satisfaction.columns = ['avg_review_score', 'review_count']
        delivery_satisfaction = delivery_satisfaction.reset_index()
        
        # Review score distribution
        score_distribution = sales_reviews['review_score'].value_counts(normalize=True).sort_index()
        score_dist_df = pd.DataFrame({
            'review_score': score_distribution.index,
            'percentage': (score_distribution.values * 100).round(1)
        })
        
        return {
            'overall_metrics': overall_metrics,
            'delivery_satisfaction': delivery_satisfaction,
            'score_distribution': score_dist_df
        }
    
    @staticmethod
    def calculate_operational_metrics(orders_data: pd.DataFrame, 
                                    target_year: int = None) -> Dict[str, float]:
        """
        Calculate operational KPIs including order status distribution and delivery performance.
        
        Args:
            orders_data (pd.DataFrame): Orders data with status and timing information
            target_year (int, optional): Specific year to analyze
            
        Returns:
            Dict[str, float]: Operational metrics
        """
        if target_year:
            orders_data = orders_data[
                pd.to_datetime(orders_data['order_purchase_timestamp']).dt.year == target_year
            ]
        
        # Order status distribution
        status_dist = orders_data['order_status'].value_counts(normalize=True) * 100
        
        # Delivery performance for delivered orders
        delivered_orders = orders_data[orders_data['order_status'] == 'delivered'].copy()
        
        if not delivered_orders.empty:
            delivered_orders['order_purchase_timestamp'] = pd.to_datetime(delivered_orders['order_purchase_timestamp'])
            delivered_orders['order_delivered_customer_date'] = pd.to_datetime(delivered_orders['order_delivered_customer_date'])
            
            # Calculate delivery time
            delivered_orders['delivery_days'] = (
                delivered_orders['order_delivered_customer_date'] - 
                delivered_orders['order_purchase_timestamp']
            ).dt.days
            
            avg_delivery_time = delivered_orders['delivery_days'].mean()
        else:
            avg_delivery_time = 0
        
        metrics = {
            'total_orders': len(orders_data),
            'delivery_rate_pct': status_dist.get('delivered', 0),
            'cancellation_rate_pct': status_dist.get('canceled', 0),
            'return_rate_pct': status_dist.get('returned', 0),
            'avg_delivery_days': avg_delivery_time
        }
        
        # Add individual status percentages
        for status, pct in status_dist.items():
            metrics[f'{status}_pct'] = pct
            
        return metrics


class MetricsVisualizer:
    """
    A class for creating business-focused visualizations of e-commerce metrics.
    """
    
    def __init__(self, color_palette: str = "Blues_r"):
        """
        Initialize visualizer with consistent color scheme.
        
        Args:
            color_palette (str): Color palette for visualizations
        """
        self.color_palette = color_palette
        plt.style.use('seaborn-v0_8')
        
    def plot_revenue_comparison(self, metrics: Dict[str, float], 
                              current_period: str, comparison_period: str) -> plt.Figure:
        """
        Create revenue comparison visualization.
        
        Args:
            metrics (Dict[str, float]): Revenue metrics dictionary
            current_period (str): Current period label
            comparison_period (str): Comparison period label
            
        Returns:
            plt.Figure: Revenue comparison plot
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Revenue Analysis: {current_period} vs {comparison_period}', fontsize=16, fontweight='bold')
        
        # Revenue comparison
        periods = [comparison_period, current_period]
        revenues = [
            metrics[f'{comparison_period}_total_revenue'],
            metrics[f'{current_period}_total_revenue']
        ]
        
        axes[0,0].bar(periods, revenues, color=['lightcoral', 'steelblue'])
        axes[0,0].set_title('Total Revenue Comparison')
        axes[0,0].set_ylabel('Revenue ($)')
        for i, v in enumerate(revenues):
            axes[0,0].text(i, v + max(revenues)*0.01, f'${v:,.0f}', ha='center', fontweight='bold')
        
        # AOV comparison
        aovs = [
            metrics[f'{comparison_period}_avg_order_value'],
            metrics[f'{current_period}_avg_order_value']
        ]
        
        axes[0,1].bar(periods, aovs, color=['lightcoral', 'steelblue'])
        axes[0,1].set_title('Average Order Value Comparison')
        axes[0,1].set_ylabel('AOV ($)')
        for i, v in enumerate(aovs):
            axes[0,1].text(i, v + max(aovs)*0.01, f'${v:.0f}', ha='center', fontweight='bold')
        
        # Order count comparison
        orders = [
            metrics[f'{comparison_period}_total_orders'],
            metrics[f'{current_period}_total_orders']
        ]
        
        axes[1,0].bar(periods, orders, color=['lightcoral', 'steelblue'])
        axes[1,0].set_title('Total Orders Comparison')
        axes[1,0].set_ylabel('Number of Orders')
        for i, v in enumerate(orders):
            axes[1,0].text(i, v + max(orders)*0.01, f'{v:,}', ha='center', fontweight='bold')
        
        # Growth rates
        growth_metrics = ['revenue_growth_rate', 'aov_growth_rate', 'order_growth_rate']
        growth_values = [metrics.get(metric, 0) for metric in growth_metrics]
        growth_labels = ['Revenue Growth', 'AOV Growth', 'Order Growth']
        
        colors = ['green' if x >= 0 else 'red' for x in growth_values]
        bars = axes[1,1].bar(growth_labels, growth_values, color=colors, alpha=0.7)
        axes[1,1].set_title('Growth Rates (%)')
        axes[1,1].set_ylabel('Growth Rate (%)')
        axes[1,1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        for bar, value in zip(bars, growth_values):
            height = bar.get_height()
            axes[1,1].text(bar.get_x() + bar.get_width()/2., height + (0.5 if height >= 0 else -1),
                          f'{value:.1f}%', ha='center', va='bottom' if height >= 0 else 'top', fontweight='bold')
        
        plt.tight_layout()
        return fig
    
    def plot_monthly_trends(self, trends_data: pd.DataFrame, year: int) -> plt.Figure:
        """
        Create monthly trends visualization.
        
        Args:
            trends_data (pd.DataFrame): Monthly trends data
            year (int): Year for the analysis
            
        Returns:
            plt.Figure: Monthly trends plot
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Monthly Business Trends - {year}', fontsize=16, fontweight='bold')
        
        months = trends_data['month']
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        month_labels = [month_names[m-1] for m in months]
        
        # Revenue trend
        axes[0,0].plot(month_labels, trends_data['revenue'], marker='o', linewidth=2, markersize=6, color='steelblue')
        axes[0,0].set_title('Monthly Revenue Trend')
        axes[0,0].set_ylabel('Revenue ($)')
        axes[0,0].tick_params(axis='x', rotation=45)
        
        # Orders trend
        axes[0,1].plot(month_labels, trends_data['orders'], marker='s', linewidth=2, markersize=6, color='darkorange')
        axes[0,1].set_title('Monthly Orders Trend')
        axes[0,1].set_ylabel('Number of Orders')
        axes[0,1].tick_params(axis='x', rotation=45)
        
        # AOV trend
        axes[1,0].plot(month_labels, trends_data['avg_order_value'], marker='^', linewidth=2, markersize=6, color='green')
        axes[1,0].set_title('Monthly Average Order Value Trend')
        axes[1,0].set_ylabel('AOV ($)')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # Revenue growth rate
        axes[1,1].bar(month_labels[1:], trends_data['revenue_growth'].dropna(), 
                     color=['green' if x >= 0 else 'red' for x in trends_data['revenue_growth'].dropna()],
                     alpha=0.7)
        axes[1,1].set_title('Month-over-Month Revenue Growth (%)')
        axes[1,1].set_ylabel('Growth Rate (%)')
        axes[1,1].axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        axes[1,1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        return fig
    
    def plot_category_performance(self, category_data: pd.DataFrame, title_suffix: str = "") -> plt.Figure:
        """
        Create product category performance visualization.
        
        Args:
            category_data (pd.DataFrame): Category performance data
            title_suffix (str): Additional text for title
            
        Returns:
            plt.Figure: Category performance plot
        """
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        fig.suptitle(f'Product Category Performance {title_suffix}', fontsize=16, fontweight='bold')
        
        # Revenue by category
        categories = category_data['product_category_name'].str.replace('_', ' ').str.title()
        
        axes[0].barh(categories, category_data['total_revenue'], color='steelblue', alpha=0.8)
        axes[0].set_title('Revenue by Category')
        axes[0].set_xlabel('Total Revenue ($)')
        
        # Items sold by category
        axes[1].barh(categories, category_data['items_sold'], color='darkorange', alpha=0.8)
        axes[1].set_title('Items Sold by Category')
        axes[1].set_xlabel('Number of Items Sold')
        
        plt.tight_layout()
        return fig
    
    def create_geographic_map(self, geo_data: pd.DataFrame, title_suffix: str = "") -> go.Figure:
        """
        Create interactive choropleth map for geographic performance.
        
        Args:
            geo_data (pd.DataFrame): Geographic performance data
            title_suffix (str): Additional text for title
            
        Returns:
            go.Figure: Interactive choropleth map
        """
        fig = px.choropleth(
            geo_data,
            locations='customer_state',
            color='total_revenue',
            locationmode='USA-states',
            scope='usa',
            title=f'Revenue by State {title_suffix}',
            color_continuous_scale='Blues',
            labels={'total_revenue': 'Total Revenue ($)'}
        )
        
        fig.update_layout(
            title_font_size=16,
            title_x=0.5,
            geo=dict(bgcolor='rgba(0,0,0,0)')
        )
        
        return fig
    
    def plot_customer_satisfaction(self, satisfaction_data: Dict[str, pd.DataFrame]) -> plt.Figure:
        """
        Create customer satisfaction analysis visualization.
        
        Args:
            satisfaction_data (Dict[str, pd.DataFrame]): Customer satisfaction metrics
            
        Returns:
            plt.Figure: Customer satisfaction plots
        """
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        fig.suptitle('Customer Satisfaction Analysis', fontsize=16, fontweight='bold')
        
        # Review score distribution
        score_dist = satisfaction_data['score_distribution']
        axes[0].bar(score_dist['review_score'], score_dist['percentage'], color='steelblue', alpha=0.8)
        axes[0].set_title('Review Score Distribution')
        axes[0].set_xlabel('Review Score')
        axes[0].set_ylabel('Percentage of Reviews (%)')
        
        # Satisfaction by delivery speed
        delivery_sat = satisfaction_data['delivery_satisfaction']
        axes[1].bar(delivery_sat['delivery_category'], delivery_sat['avg_review_score'], color='darkorange', alpha=0.8)
        axes[1].set_title('Average Rating by Delivery Speed')
        axes[1].set_xlabel('Delivery Category')
        axes[1].set_ylabel('Average Review Score')
        axes[1].set_ylim(0, 5)
        
        # Overall metrics (text display)
        overall = satisfaction_data['overall_metrics']
        axes[2].axis('off')
        axes[2].text(0.1, 0.8, 'Key Metrics:', fontsize=14, fontweight='bold', transform=axes[2].transAxes)
        
        for i, row in overall.iterrows():
            y_pos = 0.6 - (i * 0.15)
            metric_text = f"{row['metric']}: "
            if 'Score' in row['metric']:
                value_text = f"{row['value']:.2f}/5.0"
            elif 'Days' in row['metric']:
                value_text = f"{row['value']:.1f} days"
            else:
                value_text = f"{row['value']:,.0f}"
            
            axes[2].text(0.1, y_pos, metric_text, fontsize=12, fontweight='bold', transform=axes[2].transAxes)
            axes[2].text(0.6, y_pos, value_text, fontsize=12, transform=axes[2].transAxes)
        
        plt.tight_layout()
        return fig


def generate_executive_summary(metrics: Dict[str, float], 
                             current_period: str,
                             comparison_period: str = None) -> str:
    """
    Generate an executive summary of key business metrics.
    
    Args:
        metrics (Dict[str, float]): Business metrics dictionary
        current_period (str): Current period label
        comparison_period (str, optional): Comparison period label
        
    Returns:
        str: Executive summary text
    """
    current_revenue = metrics[f'{current_period}_total_revenue']
    current_orders = metrics[f'{current_period}_total_orders']
    current_aov = metrics[f'{current_period}_avg_order_value']
    
    summary = f"""
EXECUTIVE SUMMARY - {current_period.upper()}

Revenue Performance:
- Total Revenue: ${current_revenue:,.0f}
- Total Orders: {current_orders:,}
- Average Order Value: ${current_aov:.2f}
"""
    
    if comparison_period and 'revenue_growth_rate' in metrics:
        revenue_growth = metrics['revenue_growth_rate']
        order_growth = metrics['order_growth_rate']
        aov_growth = metrics['aov_growth_rate']
        
        summary += f"""
Year-over-Year Growth vs {comparison_period}:
- Revenue Growth: {revenue_growth:+.1f}%
- Order Volume Growth: {order_growth:+.1f}%
- Average Order Value Growth: {aov_growth:+.1f}%

Performance Assessment:
"""
        if revenue_growth >= 0:
            summary += f"- Revenue grew by {revenue_growth:.1f}%, indicating positive business momentum\n"
        else:
            summary += f"- Revenue declined by {abs(revenue_growth):.1f}%, requiring strategic attention\n"
            
        if order_growth >= 0:
            summary += f"- Customer acquisition increased with {order_growth:.1f}% more orders\n"
        else:
            summary += f"- Order volume decreased by {abs(order_growth):.1f}%, indicating customer retention challenges\n"
    
    return summary