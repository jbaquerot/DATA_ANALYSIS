# E-commerce Business Analytics Framework

**Professional-grade e-commerce analytics solution for comprehensive business intelligence reporting**

## Overview

This refactored analytics framework provides a robust, configurable solution for analyzing e-commerce business performance. The solution transforms raw e-commerce data into actionable business insights through automated metrics calculation and professional visualizations.

## Features

- **Configurable Analysis**: Easy-to-modify parameters for different time periods and business questions
- **Comprehensive Metrics**: Revenue analysis, product performance, geographic insights, and customer satisfaction
- **Professional Visualizations**: Business-ready charts and interactive dashboards
- **Reusable Code Architecture**: Modular design for easy maintenance and extension
- **Executive Reporting**: Auto-generated summaries and key findings

## Quick Start

### Prerequisites

- Python 3.8+
- Jupyter Notebook/Lab
- Required packages (see requirements.txt)

### Installation

1. Clone or download the project files
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Ensure your data files are in the `ecommerce_data/` directory:
   - orders_dataset.csv
   - order_items_dataset.csv
   - products_dataset.csv
   - customers_dataset.csv
   - order_reviews_dataset.csv

### Usage

**Option 1: Run the Complete Analysis Notebook**

Open and run `EDA_Refactored.ipynb` in Jupyter:

```bash
jupyter notebook EDA_Refactored.ipynb
```

**Configuration**: Modify these variables at the top of the notebook:
```python
TARGET_YEAR = 2023        # Primary analysis year
COMPARISON_YEAR = 2022    # Comparison year for growth analysis
TARGET_START_MONTH = None # Optional: specific month range
TARGET_END_MONTH = None   # Optional: specific month range
```

**Option 2: Use Individual Modules**

```python
from data_loader import load_and_prepare_data
from business_metrics import EcommerceMetrics, MetricsVisualizer

# Load data
sales_data, datasets = load_and_prepare_data("ecommerce_data/", 
                                           target_year=2023, 
                                           comparison_year=2022)

# Calculate metrics
metrics = EcommerceMetrics()
revenue_metrics = metrics.calculate_revenue_metrics(target_data, comparison_data)

# Create visualizations
visualizer = MetricsVisualizer()
fig = visualizer.plot_revenue_comparison(revenue_metrics, "2023", "2022")
```

## Project Structure

```
├── EDA_Refactored.ipynb     # Main analysis notebook
├── data_loader.py           # Data loading and preprocessing
├── business_metrics.py      # Business metric calculations and visualizations
├── requirements.txt         # Python dependencies
├── ecommerce_data/         # Data directory
│   ├── orders_dataset.csv
│   ├── order_items_dataset.csv
│   ├── products_dataset.csv
│   ├── customers_dataset.csv
│   └── order_reviews_dataset.csv
└── README.md              # This file
```

## Key Metrics Analyzed

### Revenue Analysis
- Total revenue and year-over-year growth
- Average order value trends
- Monthly revenue patterns and growth rates

### Product Performance
- Revenue by product category
- Top-performing products and categories
- Product mix analysis

### Geographic Analysis  
- Sales performance by state/region
- Geographic distribution of customers
- Regional market opportunities

### Customer Experience
- Customer satisfaction scores
- Delivery performance impact on ratings
- Review score distribution analysis

### Operational Metrics
- Order fulfillment rates
- Delivery performance
- Order status distribution

## Customization Guide

### Adding New Metrics

1. **Extend the EcommerceMetrics class** in `business_metrics.py`:
```python
@staticmethod
def your_new_metric(data: pd.DataFrame) -> Dict[str, float]:
    # Your calculation logic here
    return {"metric_name": calculated_value}
```

2. **Add visualization methods** to the MetricsVisualizer class:
```python
def plot_your_metric(self, data: pd.DataFrame) -> plt.Figure:
    # Your visualization logic here
    return fig
```

3. **Update the notebook** to include your new analysis section.

### Modifying Time Periods

Change the configuration variables in the notebook:
```python
# Analyze specific quarters
TARGET_START_MONTH = 1    # January
TARGET_END_MONTH = 3      # March

# Or analyze specific years
TARGET_YEAR = 2024
COMPARISON_YEAR = 2023
```

### Adding New Data Sources

1. **Extend the data loader** to handle new CSV files
2. **Update the schema** in the EcommerceDataLoader class
3. **Add new join logic** in the create_sales_dataset method

## Best Practices

1. **Data Quality**: Always validate data integrity before analysis
2. **Performance**: Use the filtering methods for large datasets
3. **Reproducibility**: Keep configuration at the top of notebooks
4. **Documentation**: Update docstrings when modifying functions
5. **Version Control**: Track changes to both code and analysis parameters

## Troubleshooting

**Common Issues:**

1. **Missing Data Files**: Ensure all CSV files are in the `ecommerce_data/` directory
2. **Import Errors**: Verify all required packages are installed via `pip install -r requirements.txt`
3. **Memory Issues**: Use date filtering for large datasets
4. **Visualization Issues**: Ensure plotly and matplotlib are properly configured

**Performance Optimization:**

- Filter data by date range before analysis for large datasets
- Use the built-in data loader filtering methods
- Consider sampling for exploratory analysis of very large datasets

## Support and Maintenance

This framework is designed for easy maintenance and extension:

- **Modular Design**: Each component can be updated independently
- **Clear Documentation**: All functions include comprehensive docstrings
- **Consistent Patterns**: Following established coding patterns makes extension straightforward
- **Error Handling**: Built-in validation and error reporting

For technical support or feature requests, refer to the inline documentation and function docstrings.
