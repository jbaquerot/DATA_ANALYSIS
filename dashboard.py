"""
E-commerce Analytics Dashboard
Professional Streamlit dashboard for comprehensive business intelligence reporting.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import calendar

# Import custom modules
from data_loader import EcommerceDataLoader, load_and_prepare_data
from business_metrics import EcommerceMetrics

# Page configuration
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e9ecef;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    
    .metric-label {
        color: #6c757d;
        font-size: 0.9rem;
        margin: 0;
    }
    
    .trend-positive {
        color: #28a745;
    }
    
    .trend-negative {
        color: #dc3545;
    }
    
    .star-rating {
        color: #ffc107;
        font-size: 1.5rem;
    }
    
    .big-number {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
    }
    
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache data for the dashboard."""
    try:
        sales_data, datasets = load_and_prepare_data("ecommerce_data/")
        return sales_data, datasets
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def format_currency(value):
    """Format currency values for display."""
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:.2f}"

def format_number(value):
    """Format numbers for display."""
    if value >= 1_000_000:
        return f"{value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"{value/1_000:.0f}K"
    else:
        return f"{value:,.0f}"

def get_trend_indicator(current, previous):
    """Get trend indicator with arrow and color."""
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return "", "neutral"
    
    change_pct = ((current - previous) / previous) * 100
    
    if change_pct > 0:
        return f"↗ +{change_pct:.2f}%", "positive"
    elif change_pct < 0:
        return f"↘ {change_pct:.2f}%", "negative"
    else:
        return "→ 0.00%", "neutral"

def create_revenue_trend_chart(target_data, comparison_data, target_year, comparison_year):
    """Create revenue trend line chart."""
    metrics = EcommerceMetrics()
    
    # Calculate monthly trends for both periods
    target_trends = metrics.calculate_monthly_trends(target_data, target_year)
    comparison_trends = metrics.calculate_monthly_trends(comparison_data, comparison_year)
    
    fig = go.Figure()
    
    # Month names for x-axis
    month_names = [calendar.month_abbr[i] for i in range(1, 13)]
    
    # Add target year line (solid)
    fig.add_trace(go.Scatter(
        x=month_names,
        y=target_trends['revenue'],
        mode='lines+markers',
        name=f'{target_year}',
        line=dict(color='#1f77b4', width=3),
        marker=dict(size=6)
    ))
    
    # Add comparison year line (dashed)
    fig.add_trace(go.Scatter(
        x=month_names,
        y=comparison_trends['revenue'],
        mode='lines+markers',
        name=f'{comparison_year}',
        line=dict(color='#ff7f0e', width=3, dash='dash'),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title="Revenue Trends Comparison",
        xaxis_title="Month",
        yaxis_title="Revenue",
        showlegend=True,
        height=400,
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True, tickformat='$,.0s'),
        hovermode='x unified'
    )
    
    return fig

def create_category_chart(target_data, datasets):
    """Create top 10 categories bar chart."""
    metrics = EcommerceMetrics()
    product_analysis = metrics.analyze_product_performance(
        target_data, datasets['products'], top_n=10
    )
    
    category_data = product_analysis['category_performance'].head(10)
    
    fig = go.Figure(data=[
        go.Bar(
            x=category_data['total_revenue'],
            y=category_data['product_category_name'].str.replace('_', ' ').str.title(),
            orientation='h',
            marker=dict(
                color=category_data['total_revenue'],
                colorscale='Blues',
                colorbar=dict(title="Revenue")
            ),
            text=[format_currency(x) for x in category_data['total_revenue']],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Top 10 Product Categories by Revenue",
        xaxis_title="Revenue",
        yaxis_title="Category",
        height=400,
        xaxis=dict(tickformat='$,.0s'),
        yaxis=dict(autorange="reversed")
    )
    
    return fig

def create_state_map(target_data, datasets):
    """Create US choropleth map for revenue by state."""
    metrics = EcommerceMetrics()
    geo_data = metrics.analyze_geographic_performance(
        target_data, datasets['orders'], datasets['customers']
    )
    
    fig = go.Figure(data=go.Choropleth(
        locations=geo_data['customer_state'],
        z=geo_data['total_revenue'],
        locationmode='USA-states',
        colorscale='Blues',
        text=geo_data['customer_state'],
        hovertemplate='<b>%{text}</b><br>Revenue: %{z:$,.0f}<extra></extra>',
        colorbar_title="Revenue"
    ))
    
    fig.update_layout(
        title="Revenue by State",
        geo=dict(scope='usa'),
        height=400
    )
    
    return fig

def create_satisfaction_delivery_chart(target_data, datasets):
    """Create satisfaction vs delivery time chart."""
    metrics = EcommerceMetrics()
    satisfaction_analysis = metrics.analyze_customer_satisfaction(
        target_data, datasets['reviews']
    )
    
    delivery_sat = satisfaction_analysis['delivery_satisfaction']
    
    fig = go.Figure(data=[
        go.Bar(
            x=delivery_sat['delivery_category'],
            y=delivery_sat['avg_review_score'],
            marker_color=['#1f77b4', '#ff7f0e', '#2ca02c'],
            text=[f"{score:.2f}" for score in delivery_sat['avg_review_score']],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Customer Satisfaction vs Delivery Time",
        xaxis_title="Delivery Time",
        yaxis_title="Average Review Score",
        height=400,
        yaxis=dict(range=[0, 5])
    )
    
    return fig

def main():
    # Load data
    sales_data, datasets = load_data()
    
    if sales_data is None or datasets is None:
        st.error("Failed to load data. Please check your data files.")
        return
    
    # Header with title and date filter
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.title("📊 E-commerce Analytics Dashboard")
    
    with col2:
        # Date range filter
        years_available = sorted(sales_data['order_purchase_timestamp_year'].unique())
        default_index = years_available.index(2023) if 2023 in years_available else len(years_available)-1
        selected_year = st.selectbox("Select Year:", years_available, index=default_index)
        comparison_year = selected_year - 1 if selected_year > min(years_available) else selected_year
    
    with col3:
        # Month filter
        month_options = ["All Months"] + [calendar.month_name[i] for i in range(1, 13)]
        selected_month = st.selectbox("Select Month:", month_options, index=0)
    
    st.markdown("---")
    
    # Filter data based on selection
    loader = EcommerceDataLoader()
    target_data = loader.filter_by_date_range(
        sales_data, 'order_purchase_timestamp',
        start_year=selected_year, end_year=selected_year
    )
    comparison_data = loader.filter_by_date_range(
        sales_data, 'order_purchase_timestamp',
        start_year=comparison_year, end_year=comparison_year
    )
    
    # Apply month filter if specific month is selected
    if selected_month != "All Months":
        selected_month_num = list(calendar.month_name).index(selected_month)
        target_data = target_data[target_data['order_purchase_timestamp_month'] == selected_month_num]
        comparison_data = comparison_data[comparison_data['order_purchase_timestamp_month'] == selected_month_num]
    
    # Calculate metrics
    metrics = EcommerceMetrics()
    revenue_metrics = metrics.calculate_revenue_metrics(
        target_data, comparison_data,
        current_period=str(selected_year),
        comparison_period=str(comparison_year)
    )
    
    # Calculate monthly growth
    monthly_trends = metrics.calculate_monthly_trends(target_data, selected_year)
    avg_monthly_growth = monthly_trends['revenue_growth'].mean()
    
    # KPI Row - 4 cards
    col1, col2, col3, col4 = st.columns(4)
    
    # Total Revenue
    with col1:
        current_revenue = revenue_metrics[f'{selected_year}_total_revenue']
        prev_revenue = revenue_metrics[f'{comparison_year}_total_revenue']
        trend_text, _ = get_trend_indicator(current_revenue, prev_revenue)
        
        st.metric(
            label="Total Revenue",
            value=format_currency(current_revenue),
            delta=trend_text
        )
    
    # Monthly Growth
    with col2:
        st.metric(
            label="Avg Monthly Growth",
            value=f"{avg_monthly_growth:.2f}%" if not pd.isna(avg_monthly_growth) else "N/A",
            delta=None
        )
    
    # Average Order Value
    with col3:
        current_aov = revenue_metrics[f'{selected_year}_avg_order_value']
        prev_aov = revenue_metrics[f'{comparison_year}_avg_order_value']
        trend_text, _ = get_trend_indicator(current_aov, prev_aov)
        
        st.metric(
            label="Average Order Value",
            value=f"${current_aov:.2f}",
            delta=trend_text
        )
    
    # Total Orders
    with col4:
        current_orders = revenue_metrics[f'{selected_year}_total_orders']
        prev_orders = revenue_metrics[f'{comparison_year}_total_orders']
        trend_text, _ = get_trend_indicator(current_orders, prev_orders)
        
        st.metric(
            label="Total Orders",
            value=format_number(current_orders),
            delta=trend_text
        )
    
    st.markdown("---")
    
    # Charts Grid - 2x2 layout
    row1_col1, row1_col2 = st.columns(2)
    row2_col1, row2_col2 = st.columns(2)
    
    # Revenue Trend Chart
    with row1_col1:
        st.plotly_chart(
            create_revenue_trend_chart(target_data, comparison_data, selected_year, comparison_year),
            use_container_width=True
        )
    
    # Top Categories Chart
    with row1_col2:
        st.plotly_chart(
            create_category_chart(target_data, datasets),
            use_container_width=True
        )
    
    # US Map
    with row2_col1:
        st.plotly_chart(
            create_state_map(target_data, datasets),
            use_container_width=True
        )
    
    # Satisfaction vs Delivery Chart
    with row2_col2:
        st.plotly_chart(
            create_satisfaction_delivery_chart(target_data, datasets),
            use_container_width=True
        )
    
    st.markdown("---")
    
    # Bottom Row - 2 cards
    col1, col2 = st.columns(2)
    
    # Average Delivery Time
    with col1:
        operational_metrics = metrics.calculate_operational_metrics(
            datasets['orders'], target_year=selected_year
        )
        avg_delivery_days = operational_metrics.get('avg_delivery_days', 0)
        
        # Calculate previous year delivery time for trend
        prev_operational_metrics = metrics.calculate_operational_metrics(
            datasets['orders'], target_year=comparison_year
        )
        prev_avg_delivery_days = prev_operational_metrics.get('avg_delivery_days', avg_delivery_days)
        
        trend_text, _ = get_trend_indicator(avg_delivery_days, prev_avg_delivery_days)
        
        st.metric(
            label="Average Delivery Time",
            value=f"{avg_delivery_days:.1f} days",
            delta=trend_text
        )
    
    # Review Score
    with col2:
        satisfaction_analysis = metrics.analyze_customer_satisfaction(
            target_data, datasets['reviews']
        )
        
        # Extract average review score
        overall_metrics = satisfaction_analysis['overall_metrics']
        avg_review_score = overall_metrics[overall_metrics['metric'] == 'Average Review Score']['value'].iloc[0]
        
        # Display with stars
        stars = "⭐" * int(round(avg_review_score))
        
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <div class="big-number">{avg_review_score:.2f}</div>
            <div class="star-rating">{stars}</div>
            <div style="color: #6c757d; font-size: 0.9rem;">Average Review Score</div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()