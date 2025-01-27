import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import glob
from datetime import datetime
from plotly.subplots import make_subplots
import numpy as np

# Custom color palette
COLORS = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#23CE6B', '#6761A8', '#009B72', '#E63946', '#457B9D']
BACKGROUND_COLOR = '#F8F9FA'
GRID_COLOR = '#EEEEEE'

st.set_page_config(page_title="Grocery Store Analysis", layout="wide")

# Add custom CSS
st.markdown("""
    <style>
        .stMetric {
            background-color: #ffffff;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .stMetric:hover {
            transform: translateY(-5px);
            transition: transform 0.3s ease;
        }
    </style>
""", unsafe_allow_html=True)

def load_data():
    """Load and combine all CSV files from the output directory"""
    all_files = glob.glob("output/grocery_transactions_*.csv")
    df_list = []
    for file in all_files:
        df = pd.read_csv(file)
        df_list.append(df)
    
    df = pd.concat(df_list, ignore_index=True)
    df['transaction_datetime'] = pd.to_datetime(df['transaction_datetime'])
    return df

def create_time_series(df):
    """Create enhanced daily sales time series"""
    # Aggregate by date and calculate statistics
    daily_stats = df.groupby(df['transaction_datetime'].dt.date).agg({
        'total_price': ['sum', 'mean', 'count']
    }).reset_index()
    daily_stats.columns = ['date', 'total_sales', 'avg_sale', 'num_transactions']
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add sales line
    fig.add_trace(
        go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['total_sales'],
            name='Total Sales',
            line=dict(color=COLORS[0], width=3),
            fill='tozeroy',
            fillcolor=f'rgba({int(COLORS[0][1:3], 16)}, {int(COLORS[0][3:5], 16)}, {int(COLORS[0][5:7], 16)}, 0.1)'
        )
    )
    
    # Add number of transactions line
    fig.add_trace(
        go.Scatter(
            x=daily_stats['date'],
            y=daily_stats['num_transactions'],
            name='Number of Transactions',
            yaxis='y2',
            line=dict(color=COLORS[1], width=2, dash='dot')
        )
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Daily Sales and Transaction Volume',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        hovermode='x unified',
        yaxis=dict(
            title='Total Sales ($)',
            gridcolor=GRID_COLOR,
            showgrid=True
        ),
        yaxis2=dict(
            title='Number of Transactions',
            overlaying='y',
            side='right',
            gridcolor=GRID_COLOR
        ),
        xaxis=dict(
            gridcolor=GRID_COLOR,
            showgrid=True
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    return fig

def create_category_sales(df):
    """Create enhanced product category sales breakdown"""
    category_stats = df.groupby('product_category').agg({
        'total_price': 'sum',
        'quantity': 'sum',
        'transaction_id': 'nunique'
    }).reset_index()
    
    # Calculate average price per item
    category_stats['avg_price_per_item'] = category_stats['total_price'] / category_stats['quantity']
    
    # Sort by total sales
    category_stats = category_stats.sort_values('total_price', ascending=True)
    
    fig = go.Figure()
    
    # Add horizontal bar for total sales
    fig.add_trace(
        go.Bar(
            y=category_stats['product_category'],
            x=category_stats['total_price'],
            orientation='h',
            name='Total Sales',
            marker_color=COLORS[0],
            text=category_stats['total_price'].apply(lambda x: f'${x:,.0f}'),
            textposition='auto',
        )
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Sales Performance by Product Category',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        xaxis=dict(
            title='Total Sales ($)',
            gridcolor=GRID_COLOR,
            showgrid=True
        ),
        yaxis=dict(
            title='',
            gridcolor=GRID_COLOR,
            showgrid=False
        ),
        showlegend=False,
        height=600
    )
    
    return fig

def create_store_performance(df):
    """Create enhanced store location performance comparison"""
    store_stats = df.groupby('store_location').agg({
        'total_price': 'sum',
        'transaction_id': 'nunique',
        'customer_id': 'nunique'
    }).reset_index()
    
    # Calculate average transaction value
    store_stats['avg_transaction'] = store_stats['total_price'] / store_stats['transaction_id']
    
    fig = go.Figure()
    
    # Add pie chart with improved styling
    fig.add_trace(
        go.Pie(
            labels=store_stats['store_location'],
            values=store_stats['total_price'],
            hole=0.4,
            marker=dict(colors=COLORS),
            textinfo='label+percent',
            textposition='outside',
            texttemplate='%{label}<br>%{percent:.1%}',
            pull=[0.1 if x == store_stats['total_price'].max() else 0 for x in store_stats['total_price']]
        )
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Store Location Sales Distribution',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        annotations=[
            dict(
                text=f'Total Sales<br>${store_stats["total_price"].sum():,.0f}',
                x=0.5,
                y=0.5,
                font_size=20,
                showarrow=False
            )
        ]
    )
    
    return fig

def create_payment_distribution(df):
    """Create enhanced payment method distribution"""
    payment_stats = df.groupby('payment_method').agg({
        'transaction_id': 'nunique',
        'total_price': 'sum'
    }).reset_index()
    
    # Calculate percentage
    payment_stats['percentage'] = payment_stats['transaction_id'] / payment_stats['transaction_id'].sum() * 100
    
    fig = go.Figure()
    
    # Add donut chart
    fig.add_trace(
        go.Pie(
            labels=payment_stats['payment_method'],
            values=payment_stats['transaction_id'],
            hole=0.6,
            marker=dict(colors=COLORS),
            textinfo='label+percent',
            textposition='outside',
            texttemplate='%{label}<br>%{percent:.1%}',
            pull=[0.1 if x == payment_stats['transaction_id'].max() else 0 for x in payment_stats['transaction_id']]
        )
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Payment Method Distribution',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        annotations=[
            dict(
                text=f'{payment_stats["transaction_id"].sum():,}<br>Transactions',
                x=0.5,
                y=0.5,
                font_size=20,
                showarrow=False
            )
        ]
    )
    
    return fig

def create_hourly_pattern(df):
    """Create enhanced hourly sales pattern"""
    hourly_stats = df.groupby(df['transaction_datetime'].dt.hour).agg({
        'total_price': ['sum', 'mean', 'count']
    }).reset_index()
    hourly_stats.columns = ['hour', 'total_sales', 'avg_sale', 'num_transactions']
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add area chart for total sales
    fig.add_trace(
        go.Scatter(
            x=hourly_stats['hour'],
            y=hourly_stats['total_sales'],
            name='Total Sales',
            fill='tozeroy',
            line=dict(color=COLORS[0], width=3),
            fillcolor=f'rgba({int(COLORS[0][1:3], 16)}, {int(COLORS[0][3:5], 16)}, {int(COLORS[0][5:7], 16)}, 0.1)'
        )
    )
    
    # Add line for number of transactions
    fig.add_trace(
        go.Scatter(
            x=hourly_stats['hour'],
            y=hourly_stats['num_transactions'],
            name='Number of Transactions',
            yaxis='y2',
            line=dict(color=COLORS[1], width=2, dash='dot')
        )
    )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Sales Pattern by Hour of Day',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        xaxis=dict(
            title='Hour of Day',
            tickmode='array',
            ticktext=[f'{i:02d}:00' for i in range(24)],
            tickvals=list(range(24)),
            gridcolor=GRID_COLOR
        ),
        yaxis=dict(
            title='Total Sales ($)',
            gridcolor=GRID_COLOR
        ),
        yaxis2=dict(
            title='Number of Transactions',
            overlaying='y',
            side='right',
            gridcolor=GRID_COLOR
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )
    
    return fig

def create_customer_loyalty_analysis(df):
    """Analyze loyalty member behavior and trends"""
    loyalty_stats = df.groupby('loyalty_member').agg({
        'total_price': ['sum', 'mean'],
        'transaction_id': 'nunique',
        'customer_id': 'nunique'
    }).reset_index()
    loyalty_stats.columns = ['loyalty_member', 'total_sales', 'avg_sale', 'num_transactions', 'num_customers']
    
    # Calculate average transaction per customer
    loyalty_stats['avg_trans_per_customer'] = loyalty_stats['num_transactions'] / loyalty_stats['num_customers']
    
    fig = go.Figure()
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "box"}]],
        subplot_titles=('Average Transaction Value', 'Transactions per Customer')
    )
    
    # Add average transaction value bars
    fig.add_trace(
        go.Bar(
            x=['Non-Loyalty', 'Loyalty'],
            y=loyalty_stats['avg_sale'],
            name='Avg Transaction',
            marker_color=[COLORS[0], COLORS[1]],
            text=loyalty_stats['avg_sale'].apply(lambda x: f'${x:.2f}'),
            textposition='auto',
        ),
        row=1, col=1
    )
    
    # Add transactions per customer bars
    fig.add_trace(
        go.Bar(
            x=['Non-Loyalty', 'Loyalty'],
            y=loyalty_stats['avg_trans_per_customer'],
            name='Transactions/Customer',
            marker_color=[COLORS[0], COLORS[1]],
            text=loyalty_stats['avg_trans_per_customer'].apply(lambda x: f'{x:.1f}'),
            textposition='auto',
        ),
        row=1, col=2
    )
    
    fig.update_layout(
        title_text="Loyalty Program Impact Analysis",
        showlegend=False,
        height=400,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR
    )
    
    return fig

def create_weekly_trends(df):
    """Analyze weekly sales patterns and trends"""
    df['week'] = df['transaction_datetime'].dt.isocalendar().week
    df['weekday'] = df['transaction_datetime'].dt.day_name()
    
    weekly_stats = df.groupby(['week', 'weekday']).agg({
        'total_price': 'sum',
        'transaction_id': 'nunique'
    }).reset_index()
    
    # Calculate average daily sales by weekday
    weekday_avg = df.groupby('weekday').agg({
        'total_price': 'mean',
        'transaction_id': 'nunique'
    }).reset_index()
    
    # Sort weekdays properly
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_avg['weekday'] = pd.Categorical(weekday_avg['weekday'], categories=weekday_order, ordered=True)
    weekday_avg = weekday_avg.sort_values('weekday')
    
    fig = go.Figure()
    
    # Add average daily sales
    fig.add_trace(
        go.Bar(
            x=weekday_avg['weekday'],
            y=weekday_avg['total_price'],
            name='Avg Daily Sales',
            marker_color=COLORS[0],
            text=weekday_avg['total_price'].apply(lambda x: f'${x:,.0f}'),
            textposition='auto',
        )
    )
    
    # Add trend line
    fig.add_trace(
        go.Scatter(
            x=weekday_avg['weekday'],
            y=weekday_avg['transaction_id'],
            name='Avg Transactions',
            yaxis='y2',
            line=dict(color=COLORS[1], width=2),
            mode='lines+markers'
        )
    )
    
    fig.update_layout(
        title={
            'text': 'Weekly Sales Patterns',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        yaxis=dict(title='Average Daily Sales ($)', gridcolor=GRID_COLOR),
        yaxis2=dict(
            title='Average Number of Transactions',
            overlaying='y',
            side='right',
            gridcolor=GRID_COLOR
        ),
        xaxis=dict(title='', gridcolor=GRID_COLOR),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )
    
    return fig

def create_basket_analysis(df):
    """Analyze shopping basket patterns"""
    # Calculate items per transaction
    basket_stats = df.groupby('transaction_id').agg({
        'product_id': 'count',
        'total_price': 'sum'
    }).reset_index()
    
    # Create histogram of basket sizes
    fig = go.Figure()
    
    fig.add_trace(
        go.Histogram(
            x=basket_stats['product_id'],
            nbinsx=20,
            name='Basket Size Distribution',
            marker_color=COLORS[0],
            opacity=0.7
        )
    )
    
    # Add average line
    avg_basket_size = basket_stats['product_id'].mean()
    fig.add_vline(
        x=avg_basket_size,
        line_dash="dash",
        line_color=COLORS[1],
        annotation_text=f"Average: {avg_basket_size:.1f} items",
        annotation_position="top right"
    )
    
    fig.update_layout(
        title={
            'text': 'Shopping Basket Size Distribution',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        xaxis=dict(title='Number of Items in Basket', gridcolor=GRID_COLOR),
        yaxis=dict(title='Number of Transactions', gridcolor=GRID_COLOR),
        showlegend=False
    )
    
    return fig

def create_seasonality_analysis(df):
    """Analyze seasonal patterns in sales"""
    # Create monthly analysis
    df['month'] = df['transaction_datetime'].dt.month
    df['season'] = pd.cut(df['transaction_datetime'].dt.month, 
                         bins=[0, 3, 6, 9, 12], 
                         labels=['Winter', 'Spring', 'Summer', 'Fall'])
    
    # Monthly stats
    monthly_stats = df.groupby('month').agg({
        'total_price': 'sum',
        'transaction_id': 'nunique',
        'quantity': 'sum'
    }).reset_index()
    
    # Seasonal stats
    seasonal_stats = df.groupby(['season', 'product_category']).agg({
        'total_price': 'sum'
    }).reset_index()
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Monthly Sales Trends', 'Seasonal Category Performance'),
        vertical_spacing=0.22,
        specs=[[{"type": "scatter"}],
               [{"type": "bar"}]]
    )
    
    # Add monthly sales line
    fig.add_trace(
        go.Scatter(
            x=monthly_stats['month'],
            y=monthly_stats['total_price'],
            name='Monthly Sales',
            line=dict(color=COLORS[0], width=3),
            fill='tozeroy',
            fillcolor=f'rgba({int(COLORS[0][1:3], 16)}, {int(COLORS[0][3:5], 16)}, {int(COLORS[0][5:7], 16)}, 0.1)'
        ),
        row=1, col=1
    )
    
    # Add transaction volume
    fig.add_trace(
        go.Scatter(
            x=monthly_stats['month'],
            y=monthly_stats['transaction_id'],
            name='Transactions',
            yaxis='y2',
            line=dict(color=COLORS[1], width=2, dash='dot')
        ),
        row=1, col=1
    )
    
    # Add seasonal category performance
    for season in seasonal_stats['season'].unique():
        season_data = seasonal_stats[seasonal_stats['season'] == season]
        fig.add_trace(
            go.Bar(
                x=season_data['product_category'],
                y=season_data['total_price'],
                name=season,
                marker_color=COLORS[list(seasonal_stats['season'].unique()).index(season)],
            ),
            row=2, col=1
        )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="Seasonal Sales Analysis",
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        hovermode='x unified'
    )
    
    # Update axes
    fig.update_xaxes(title_text="Month", row=1, col=1, 
                     ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
                     tickvals=list(range(1, 13)),
                     gridcolor=GRID_COLOR)
    fig.update_xaxes(title_text="Product Category", row=2, col=1, 
                     tickangle=45,
                     gridcolor=GRID_COLOR)
    
    fig.update_yaxes(title_text="Total Sales ($)", row=1, col=1, gridcolor=GRID_COLOR)
    fig.update_yaxes(title_text="Number of Transactions", row=1, col=1, 
                     secondary_y=True, gridcolor=GRID_COLOR)
    fig.update_yaxes(title_text="Total Sales ($)", row=2, col=1, gridcolor=GRID_COLOR)
    
    return fig

def create_product_seasonality(df):
    """Analyze product seasonality patterns"""
    # Add month column first
    df_with_month = df.copy()
    df_with_month['month'] = df_with_month['transaction_datetime'].dt.month
    
    # Calculate monthly sales by category
    monthly_category = df_with_month.groupby([
        'month',
        'product_category'
    ])['total_price'].sum().reset_index()
    
    # Calculate percentage of sales for each category by month
    monthly_total = monthly_category.groupby('month')['total_price'].transform('sum')
    monthly_category['sales_percentage'] = monthly_category['total_price'] / monthly_total * 100
    
    fig = go.Figure()
    
    # Create stacked area chart
    for category in df_with_month['product_category'].unique():
        category_data = monthly_category[monthly_category['product_category'] == category]
        fig.add_trace(
            go.Scatter(
                x=category_data['month'],
                y=category_data['sales_percentage'],
                name=category,
                stackgroup='one',
                mode='lines',
                line=dict(width=0.5),
                hovertemplate="%{y:.1f}%<extra></extra>"
            )
        )
    
    # Update layout
    fig.update_layout(
        title={
            'text': 'Product Category Mix by Month',
            'y':0.95,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top',
            'font': dict(size=24)
        },
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        xaxis=dict(
            title='Month',
            ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                     'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
            tickvals=list(range(1, 13)),
            gridcolor=GRID_COLOR
        ),
        yaxis=dict(
            title='Percentage of Total Sales',
            gridcolor=GRID_COLOR,
            ticksuffix='%'
        ),
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

def create_sales_performance_dashboard(df):
    """Create comprehensive sales performance analysis"""
    # Create daily, weekly, and monthly aggregations
    df['date'] = df['transaction_datetime'].dt.date
    df['week'] = df['transaction_datetime'].dt.isocalendar().week
    df['month'] = df['transaction_datetime'].dt.month
    df['is_weekend'] = df['transaction_datetime'].dt.weekday >= 5
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Daily Revenue Pattern', 'Weekly Performance', 
                       'Category Performance', 'Top 10 Products'),
        specs=[[{"type": "scatter"}, {"type": "bar"}],
               [{"type": "pie"}, {"type": "bar"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 1. Daily Revenue Pattern
    daily_sales = df.groupby('date').agg({
        'total_price': 'sum',
        'transaction_id': 'nunique'
    }).reset_index()
    
    fig.add_trace(
        go.Scatter(
            x=daily_sales['date'],
            y=daily_sales['total_price'],
            name='Daily Sales',
            line=dict(color=COLORS[0], width=2),
            fill='tozeroy',
            fillcolor=f'rgba({int(COLORS[0][1:3], 16)}, {int(COLORS[0][3:5], 16)}, {int(COLORS[0][5:7], 16)}, 0.1)'
        ),
        row=1, col=1
    )
    
    # 2. Weekly Performance
    weekly_sales = df.groupby('week')['total_price'].sum().reset_index()
    fig.add_trace(
        go.Bar(
            x=weekly_sales['week'],
            y=weekly_sales['total_price'],
            name='Weekly Sales',
            marker_color=COLORS[1]
        ),
        row=1, col=2
    )
    
    # 3. Category Performance
    category_sales = df.groupby('product_category')['total_price'].sum().reset_index()
    fig.add_trace(
        go.Pie(
            labels=category_sales['product_category'],
            values=category_sales['total_price'],
            hole=0.4,
            marker=dict(colors=COLORS),
            textinfo='label+percent',
            textposition='outside'
        ),
        row=2, col=1
    )
    
    # 4. Top 10 Products
    product_sales = df.groupby(['product_id', 'product_name'])['total_price'].sum().reset_index()
    top_products = product_sales.nlargest(10, 'total_price')
    
    fig.add_trace(
        go.Bar(
            x=top_products['total_price'],
            y=top_products['product_name'],
            orientation='h',
            marker_color=COLORS[2],
            text=top_products['total_price'].apply(lambda x: f'${x:,.0f}'),
            textposition='auto',
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="Sales Performance Analysis",
        showlegend=False,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR
    )
    
    # Update axes
    fig.update_xaxes(gridcolor=GRID_COLOR, showgrid=True)
    fig.update_yaxes(gridcolor=GRID_COLOR, showgrid=True)
    
    return fig

def create_product_performance_analysis(df):
    """Analyze product performance and demand patterns"""
    # Calculate product metrics
    product_metrics = df.groupby(['product_id', 'product_name', 'product_category']).agg({
        'transaction_id': 'nunique',
        'total_price': 'sum',
        'quantity': 'sum'
    }).reset_index()
    
    # Calculate transaction frequency
    total_transactions = df['transaction_id'].nunique()
    product_metrics['transaction_frequency'] = (product_metrics['transaction_id'] / total_transactions * 100)
    
    # Identify high-demand products (30% threshold)
    high_demand = product_metrics[product_metrics['transaction_frequency'] >= 30]
    
    # Create visualization
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('High-Demand Products', 'Sales by Category',
                       'Product Transaction Frequency', 'Low-Performing Products'),
        specs=[[{"type": "bar"}, {"type": "pie"}],
               [{"type": "histogram"}, {"type": "bar"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 1. High-Demand Products
    fig.add_trace(
        go.Bar(
            x=high_demand['product_name'],
            y=high_demand['transaction_frequency'],
            marker_color=COLORS[0],
            text=high_demand['transaction_frequency'].apply(lambda x: f'{x:.1f}%'),
            textposition='auto',
        ),
        row=1, col=1
    )
    
    # 2. Category Distribution
    category_sales = df.groupby('product_category')['total_price'].sum().reset_index()
    fig.add_trace(
        go.Pie(
            labels=category_sales['product_category'],
            values=category_sales['total_price'],
            marker=dict(colors=COLORS),
            textinfo='label+percent',
            hole=0.4
        ),
        row=1, col=2
    )
    
    # 3. Transaction Frequency Distribution
    fig.add_trace(
        go.Histogram(
            x=product_metrics['transaction_frequency'],
            nbinsx=20,
            marker_color=COLORS[2],
            name='Frequency Distribution'
        ),
        row=2, col=1
    )
    
    # 4. Low-Performing Products
    low_performing = product_metrics.nsmallest(10, 'total_price')
    fig.add_trace(
        go.Bar(
            x=low_performing['product_name'],
            y=low_performing['total_price'],
            marker_color=COLORS[3],
            text=low_performing['total_price'].apply(lambda x: f'${x:.2f}'),
            textposition='auto',
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="Product Performance Analysis",
        showlegend=False,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR
    )
    
    return fig

def create_customer_behavior_analysis(df):
    """Analyze customer behavior patterns and segmentation"""
    # Calculate customer metrics
    customer_metrics = df.groupby('customer_id').agg({
        'transaction_id': 'nunique',
        'total_price': 'sum',
        'loyalty_member': 'first'
    }).reset_index()
    
    # Create customer segments based on purchase frequency
    customer_metrics['frequency_segment'] = pd.qcut(
        customer_metrics['transaction_id'], 
        q=3, 
        labels=['Occasional', 'Regular', 'Frequent']
    )
    
    # Create spend segments
    customer_metrics['spend_segment'] = pd.qcut(
        customer_metrics['total_price'], 
        q=3, 
        labels=['Low Spender', 'Medium Spender', 'High Spender']
    )
    
    # Calculate CLV (simplified as average monthly spend * 12)
    months_in_data = (df['transaction_datetime'].max() - df['transaction_datetime'].min()).days / 30
    customer_metrics['monthly_spend'] = customer_metrics['total_price'] / months_in_data
    customer_metrics['projected_annual_value'] = customer_metrics['monthly_spend'] * 12
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Customer Segmentation by Spend',
            'Purchase Frequency Distribution',
            'Loyalty vs Non-Loyalty Comparison',
            'Customer Lifetime Value Distribution'
        ),
        specs=[[{"type": "pie"}, {"type": "histogram"}],
               [{"type": "bar"}, {"type": "box"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 1. Customer Segmentation Pie Chart
    segment_dist = customer_metrics['spend_segment'].value_counts()
    fig.add_trace(
        go.Pie(
            labels=segment_dist.index,
            values=segment_dist.values,
            hole=0.4,
            marker=dict(colors=COLORS[:3]),
            textinfo='label+percent',
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # 2. Purchase Frequency Distribution
    fig.add_trace(
        go.Histogram(
            x=customer_metrics['transaction_id'],
            nbinsx=30,
            name='Frequency Distribution',
            marker_color=COLORS[1]
        ),
        row=1, col=2
    )
    
    # 3. Loyalty vs Non-Loyalty Comparison
    loyalty_comparison = df.groupby('loyalty_member').agg({
        'total_price': 'mean',
        'transaction_id': 'nunique',
        'customer_id': 'nunique'
    }).reset_index()
    
    loyalty_comparison['avg_transactions_per_customer'] = (
        loyalty_comparison['transaction_id'] / loyalty_comparison['customer_id']
    )
    
    fig.add_trace(
        go.Bar(
            x=['Non-Loyalty', 'Loyalty'],
            y=loyalty_comparison['avg_transactions_per_customer'],
            marker_color=[COLORS[2], COLORS[3]],
            text=loyalty_comparison['avg_transactions_per_customer'].apply(lambda x: f'{x:.1f}'),
            textposition='auto',
        ),
        row=2, col=1
    )
    
    # 4. Customer Lifetime Value Distribution
    fig.add_trace(
        go.Box(
            x=customer_metrics['loyalty_member'],
            y=customer_metrics['projected_annual_value'],
            marker_color=COLORS[4],
            boxpoints='outliers',
            name='CLV Distribution'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="Customer Behavior Analysis",
        showlegend=False,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR
    )
    
    # Update axes
    fig.update_xaxes(gridcolor=GRID_COLOR, showgrid=True)
    fig.update_yaxes(gridcolor=GRID_COLOR, showgrid=True)
    
    # Update specific axes labels
    fig.update_xaxes(title_text="Number of Transactions", row=1, col=2)
    fig.update_yaxes(title_text="Number of Customers", row=1, col=2)
    
    fig.update_xaxes(title_text="Customer Type", row=2, col=1)
    fig.update_yaxes(title_text="Avg Transactions per Customer", row=2, col=1)
    
    fig.update_xaxes(title_text="Loyalty Status", row=2, col=2)
    fig.update_yaxes(title_text="Projected Annual Value ($)", row=2, col=2)
    
    return fig

def create_customer_product_preferences(df):
    """Analyze customer product preferences by segment"""
    # Calculate customer-product preferences
    customer_prefs = df.groupby(['customer_id', 'loyalty_member', 'product_category']).agg({
        'total_price': 'sum',
        'quantity': 'sum'
    }).reset_index()
    
    # Calculate percentage of spend by category for each customer
    customer_total = customer_prefs.groupby('customer_id')['total_price'].transform('sum')
    customer_prefs['category_percentage'] = customer_prefs['total_price'] / customer_total * 100
    
    # Create visualization
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            'Category Preferences by Loyalty Status',
            'Average Basket Size by Customer Type'
        ),
        specs=[[{"type": "bar"}, {"type": "box"}]]
    )
    
    # 1. Category Preferences by Loyalty Status
    loyalty_prefs = customer_prefs.groupby(['loyalty_member', 'product_category'])['category_percentage'].mean().reset_index()
    
    for loyalty_status in [False, True]:
        mask = loyalty_prefs['loyalty_member'] == loyalty_status
        fig.add_trace(
            go.Bar(
                name='Loyalty' if loyalty_status else 'Non-Loyalty',
                x=loyalty_prefs[mask]['product_category'],
                y=loyalty_prefs[mask]['category_percentage'],
                marker_color=COLORS[0] if loyalty_status else COLORS[1]
            ),
            row=1, col=1
        )
    
    # 2. Basket Size Distribution
    basket_sizes = df.groupby(['transaction_id', 'loyalty_member'])['quantity'].sum().reset_index()
    
    fig.add_trace(
        go.Box(
            x=basket_sizes['loyalty_member'],
            y=basket_sizes['quantity'],
            marker_color=COLORS[2],
            boxpoints='outliers',
            name='Basket Size'
        ),
        row=1, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=500,
        title_text="Customer Product Preferences Analysis",
        showlegend=True,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        barmode='group'
    )
    
    # Update axes
    fig.update_xaxes(title_text="Product Category", row=1, col=1, tickangle=45)
    fig.update_yaxes(title_text="Percentage of Spend", row=1, col=1)
    
    fig.update_xaxes(title_text="Loyalty Status", row=1, col=2)
    fig.update_yaxes(title_text="Items per Transaction", row=1, col=2)
    
    return fig

def create_inventory_analytics(df):
    """Analyze inventory patterns and supply chain metrics"""
    # Calculate product movement metrics
    product_movement = df.groupby(['product_id', 'product_name', 'product_category']).agg({
        'quantity': 'sum',
        'transaction_id': 'nunique',
        'total_price': 'sum'
    }).reset_index()
    
    # Calculate daily sales rate
    days_in_data = (df['transaction_datetime'].max() - df['transaction_datetime'].min()).days
    product_movement['daily_sales_rate'] = product_movement['quantity'] / days_in_data
    
    # Calculate turnover rate (assumed monthly inventory levels)
    product_movement['monthly_turnover'] = product_movement['daily_sales_rate'] * 30
    
    # Create visualization
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Fast-Moving Products',
            'Category Turnover Rates',
            'Daily Sales Rate Distribution',
            'Slow-Moving Products'
        ),
        specs=[[{"type": "bar"}, {"type": "pie"}],
               [{"type": "histogram"}, {"type": "bar"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 1. Fast-Moving Products
    top_moving = product_movement.nlargest(10, 'daily_sales_rate')
    fig.add_trace(
        go.Bar(
            x=top_moving['product_name'],
            y=top_moving['daily_sales_rate'],
            marker_color=COLORS[0],
            text=top_moving['daily_sales_rate'].apply(lambda x: f'{x:.1f}/day'),
            textposition='auto',
        ),
        row=1, col=1
    )
    
    # 2. Category Turnover
    category_turnover = df.groupby('product_category').agg({
        'quantity': 'sum'
    }).reset_index()
    category_turnover['turnover_rate'] = category_turnover['quantity'] / days_in_data * 30
    
    fig.add_trace(
        go.Pie(
            labels=category_turnover['product_category'],
            values=category_turnover['turnover_rate'],
            hole=0.4,
            marker=dict(colors=COLORS),
            textinfo='label+percent',
            textposition='outside'
        ),
        row=1, col=2
    )
    
    # 3. Sales Rate Distribution
    fig.add_trace(
        go.Histogram(
            x=product_movement['daily_sales_rate'],
            nbinsx=30,
            marker_color=COLORS[2],
            name='Sales Rate Distribution'
        ),
        row=2, col=1
    )
    
    # 4. Slow-Moving Products
    slow_moving = product_movement.nsmallest(10, 'daily_sales_rate')
    fig.add_trace(
        go.Bar(
            x=slow_moving['product_name'],
            y=slow_moving['daily_sales_rate'],
            marker_color=COLORS[3],
            text=slow_moving['daily_sales_rate'].apply(lambda x: f'{x:.2f}/day'),
            textposition='auto',
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="Inventory Movement Analysis",
        showlegend=False,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR
    )
    
    return fig

def create_demand_forecast(df):
    """Create demand forecasting visualization"""
    # Aggregate daily sales
    daily_sales = df.groupby(df['transaction_datetime'].dt.date).agg({
        'quantity': 'sum',
        'total_price': 'sum'
    }).reset_index()
    
    # Calculate moving averages
    daily_sales['7_day_ma'] = daily_sales['quantity'].rolling(window=7).mean()
    daily_sales['30_day_ma'] = daily_sales['quantity'].rolling(window=30).mean()
    
    # Create visualization
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=(
            'Daily Sales Volume with Trends',
            'Category-wise Daily Demand Pattern'
        ),
        vertical_spacing=0.15
    )
    
    # 1. Daily Sales with Moving Averages
    fig.add_trace(
        go.Scatter(
            x=daily_sales['transaction_datetime'],
            y=daily_sales['quantity'],
            name='Daily Sales',
            mode='lines',
            line=dict(color=COLORS[0], width=1),
            opacity=0.7
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=daily_sales['transaction_datetime'],
            y=daily_sales['7_day_ma'],
            name='7-day Moving Average',
            line=dict(color=COLORS[1], width=2)
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=daily_sales['transaction_datetime'],
            y=daily_sales['30_day_ma'],
            name='30-day Moving Average',
            line=dict(color=COLORS[2], width=2)
        ),
        row=1, col=1
    )
    
    # 2. Category-wise Daily Pattern
    category_daily = df.groupby([
        df['transaction_datetime'].dt.date,
        'product_category'
    ])['quantity'].sum().reset_index()
    
    for category in df['product_category'].unique():
        cat_data = category_daily[category_daily['product_category'] == category]
        fig.add_trace(
            go.Scatter(
                x=cat_data['transaction_datetime'],
                y=cat_data['quantity'],
                name=category,
                mode='lines',
                opacity=0.7
            ),
            row=2, col=1
        )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="Demand Patterns and Forecasting",
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update axes
    fig.update_xaxes(gridcolor=GRID_COLOR, showgrid=True)
    fig.update_yaxes(gridcolor=GRID_COLOR, showgrid=True)
    
    return fig

def create_operational_efficiency_analysis(df):
    """Analyze operational efficiency metrics"""
    # Calculate hourly patterns by store
    df['hour'] = df['transaction_datetime'].dt.hour
    df['weekday'] = df['transaction_datetime'].dt.day_name()
    df['is_weekend'] = df['transaction_datetime'].dt.weekday >= 5
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Peak Transaction Hours by Day',
            'Store Performance Comparison',
            'Regional Product Preferences',
            'Payment Method Efficiency'
        ),
        specs=[[{"type": "heatmap"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "box"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 1. Peak Transaction Hours Heatmap
    hourly_pattern = df.groupby(['weekday', 'hour'])['transaction_id'].nunique().reset_index()
    hourly_pivot = hourly_pattern.pivot(
        index='weekday',
        columns='hour',
        values='transaction_id'
    )
    
    # Sort weekdays properly
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    hourly_pivot = hourly_pivot.reindex(weekday_order)
    
    fig.add_trace(
        go.Heatmap(
            z=hourly_pivot.values,
            x=[f"{hour:02d}:00" for hour in hourly_pivot.columns],
            y=hourly_pivot.index,
            colorscale='Viridis',
            name='Transaction Volume'
        ),
        row=1, col=1
    )
    
    # 2. Store Performance
    store_performance = df.groupby('store_location').agg({
        'total_price': 'sum',
        'transaction_id': 'nunique',
        'customer_id': 'nunique'
    }).reset_index()
    
    store_performance['avg_transaction_value'] = (
        store_performance['total_price'] / store_performance['transaction_id']
    )
    
    fig.add_trace(
        go.Bar(
            x=store_performance['store_location'],
            y=store_performance['total_price'],
            name='Total Sales',
            marker_color=COLORS[0],
            text=store_performance['total_price'].apply(lambda x: f'${x:,.0f}'),
            textposition='auto',
        ),
        row=1, col=2
    )
    
    # 3. Regional Product Preferences
    regional_prefs = df.groupby(['store_location', 'product_category'])['quantity'].sum().reset_index()
    location_totals = regional_prefs.groupby('store_location')['quantity'].transform('sum')
    regional_prefs['percentage'] = regional_prefs['quantity'] / location_totals * 100
    
    # Get top categories for each location
    for location in df['store_location'].unique():
        location_data = regional_prefs[regional_prefs['store_location'] == location]
        top_categories = location_data.nlargest(3, 'percentage')
        
        fig.add_trace(
            go.Bar(
                name=location,
                x=top_categories['product_category'],
                y=top_categories['percentage'],
                text=top_categories['percentage'].apply(lambda x: f'{x:.1f}%'),
                textposition='auto',
            ),
            row=2, col=1
        )
    
    # 4. Payment Method Efficiency
    # Calculate time between transactions as a proxy for checkout speed
    df_sorted = df.sort_values(['store_location', 'transaction_datetime'])
    df_sorted['time_between_transactions'] = df_sorted.groupby('store_location')['transaction_datetime'].diff().dt.total_seconds()
    
    fig.add_trace(
        go.Box(
            x=df_sorted['payment_method'],
            y=df_sorted['time_between_transactions'],
            name='Checkout Time',
            marker_color=COLORS[3],
            boxpoints='outliers'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="Operational Efficiency Analysis",
        showlegend=True,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update axes
    fig.update_xaxes(gridcolor=GRID_COLOR, showgrid=True)
    fig.update_yaxes(gridcolor=GRID_COLOR, showgrid=True)
    
    # Update specific axes labels
    fig.update_xaxes(title_text="Hour of Day", row=1, col=1)
    fig.update_yaxes(title_text="Day of Week", row=1, col=1)
    
    fig.update_xaxes(title_text="Store Location", row=1, col=2)
    fig.update_yaxes(title_text="Total Sales ($)", row=1, col=2)
    
    fig.update_xaxes(title_text="Product Category", row=2, col=1, tickangle=45)
    fig.update_yaxes(title_text="Percentage of Store Sales", row=2, col=1)
    
    fig.update_xaxes(title_text="Payment Method", row=2, col=2, tickangle=45)
    fig.update_yaxes(title_text="Seconds Between Transactions", row=2, col=2)
    
    return fig

def create_marketing_analysis(df):
    """Analyze marketing effectiveness and promotion patterns"""
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Discount Impact on Sales',
            'Customer Segment Response to Discounts',
            'Product Bundle Analysis',
            'Holiday Promotion Performance'
        ),
        specs=[[{"type": "bar"}, {"type": "scatter"}],
               [{"type": "heatmap"}, {"type": "bar"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 1. Discount Impact Analysis
    discount_impact = df.groupby('discount_applied').agg({
        'total_price': 'sum',
        'transaction_id': 'nunique',
        'customer_id': 'nunique'
    }).reset_index()
    
    discount_impact['avg_transaction_value'] = (
        discount_impact['total_price'] / discount_impact['transaction_id']
    )
    
    fig.add_trace(
        go.Bar(
            x=discount_impact['discount_applied'].apply(lambda x: f"{x*100:.0f}%"),
            y=discount_impact['total_price'],
            name='Total Sales',
            marker_color=COLORS[0],
            text=discount_impact['total_price'].apply(lambda x: f'${x:,.0f}'),
            textposition='auto',
        ),
        row=1, col=1
    )
    
    # 2. Customer Segment Response
    segment_response = df.groupby(['loyalty_member', 'discount_applied']).agg({
        'total_price': 'sum',
        'customer_id': 'nunique'
    }).reset_index()
    
    for loyalty in [True, False]:
        mask = segment_response['loyalty_member'] == loyalty
        fig.add_trace(
            go.Scatter(
                x=segment_response[mask]['discount_applied'].apply(lambda x: f"{x*100:.0f}%"),
                y=segment_response[mask]['total_price'],
                name=f"{'Loyalty' if loyalty else 'Non-Loyalty'} Members",
                mode='lines+markers',
                marker=dict(size=8)
            ),
            row=1, col=2
        )
    
    # 3. Product Bundle Analysis
    # Create product pairs within transactions
    transaction_products = df.groupby(['transaction_id', 'product_category'])['quantity'].sum().unstack().fillna(0)
    correlation_matrix = transaction_products.corr()
    
    fig.add_trace(
        go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='Viridis',
            text=correlation_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10},
            name='Product Correlations'
        ),
        row=2, col=1
    )
    
    # 4. Holiday Performance
    # Define holiday periods
    df['is_holiday'] = df['transaction_datetime'].dt.strftime('%m-%d').isin([
        '12-25',  # Christmas
        '11-23',  # Thanksgiving
        '07-04',  # Independence Day
        '01-01'   # New Year
    ])
    
    holiday_performance = df.groupby('is_holiday').agg({
        'total_price': ['sum', 'mean'],
        'transaction_id': 'nunique'
    }).reset_index()
    holiday_performance.columns = ['is_holiday', 'total_sales', 'avg_sale', 'num_transactions']
    
    fig.add_trace(
        go.Bar(
            x=['Regular Days', 'Holiday Period'],
            y=holiday_performance['avg_sale'],
            name='Average Sale Value',
            marker_color=COLORS[3],
            text=holiday_performance['avg_sale'].apply(lambda x: f'${x:.2f}'),
            textposition='auto',
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="Marketing & Promotions Analysis",
        showlegend=True,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update axes
    fig.update_xaxes(gridcolor=GRID_COLOR, showgrid=True)
    fig.update_yaxes(gridcolor=GRID_COLOR, showgrid=True)
    
    # Update specific axes labels
    fig.update_xaxes(title_text="Discount Level", row=1, col=1)
    fig.update_yaxes(title_text="Total Sales ($)", row=1, col=1)
    
    fig.update_xaxes(title_text="Discount Level", row=1, col=2)
    fig.update_yaxes(title_text="Total Sales ($)", row=1, col=2)
    
    fig.update_xaxes(title_text="Product Category", row=2, col=1, tickangle=45)
    fig.update_yaxes(title_text="Product Category", row=2, col=1)
    
    fig.update_xaxes(title_text="Period Type", row=2, col=2)
    fig.update_yaxes(title_text="Average Sale Value ($)", row=2, col=2)
    
    return fig

def create_promotion_effectiveness(df):
    """Analyze promotion effectiveness across different dimensions"""
    # Calculate promotion metrics
    promo_metrics = df.groupby('discount_applied').agg({
        'total_price': ['sum', 'mean'],
        'transaction_id': 'nunique',
        'customer_id': 'nunique'
    }).reset_index()
    promo_metrics.columns = ['discount', 'total_sales', 'avg_sale', 'transactions', 'customers']
    
    # Create visualization
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=(
            'Discount Level Impact',
            'Customer Retention by Discount'
        ),
        specs=[[{"type": "bar"}, {"type": "scatter"}]]
    )
    
    # 1. Discount Level Impact
    fig.add_trace(
        go.Bar(
            x=promo_metrics['discount'].apply(lambda x: f"{x*100:.0f}%"),
            y=promo_metrics['avg_sale'],
            name='Average Sale',
            marker_color=COLORS[0],
            text=promo_metrics['avg_sale'].apply(lambda x: f'${x:.2f}'),
            textposition='auto',
        ),
        row=1, col=1
    )
    
    # 2. Customer Retention Analysis
    customer_frequency = df.groupby(['customer_id', 'discount_applied'])['transaction_id'].nunique().reset_index()
    retention_stats = customer_frequency.groupby('discount_applied')['transaction_id'].mean().reset_index()
    
    fig.add_trace(
        go.Scatter(
            x=retention_stats['discount_applied'].apply(lambda x: f"{x*100:.0f}%"),
            y=retention_stats['transaction_id'],
            name='Repeat Visits',
            mode='lines+markers',
            marker=dict(size=10),
            line=dict(width=3),
            text=retention_stats['transaction_id'].apply(lambda x: f'{x:.1f} visits'),
            textposition='top center'
        ),
        row=1, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=400,
        title_text="Promotion Effectiveness Analysis",
        showlegend=True,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update axes
    fig.update_xaxes(title_text="Discount Level", row=1, col=1)
    fig.update_yaxes(title_text="Average Sale Value ($)", row=1, col=1)
    
    fig.update_xaxes(title_text="Discount Level", row=1, col=2)
    fig.update_yaxes(title_text="Average Visits per Customer", row=1, col=2)
    
    return fig

def create_anomaly_detection(df):
    """Analyze and visualize transaction anomalies and potential fraud patterns"""
    # Calculate product-level statistics
    product_stats = df.groupby(['product_id', 'product_name', 'product_category']).agg({
        'quantity': ['mean', 'std', 'max'],
        'unit_price': ['mean', 'std', 'max'],
        'total_price': ['mean', 'std', 'max']
    }).reset_index()
    
    # Flatten column names
    product_stats.columns = ['product_id', 'product_name', 'product_category', 
                           'avg_quantity', 'qty_std', 'max_quantity',
                           'avg_price', 'price_std', 'max_price',
                           'avg_total', 'total_std', 'max_total']
    
    # Calculate z-scores for anomaly detection
    df_anomaly = df.merge(product_stats[['product_id', 'avg_quantity', 'qty_std', 'avg_price', 'price_std']], 
                         on='product_id')
    df_anomaly['quantity_zscore'] = (df_anomaly['quantity'] - df_anomaly['avg_quantity']) / df_anomaly['qty_std']
    df_anomaly['price_zscore'] = (df_anomaly['unit_price'] - df_anomaly['avg_price']) / df_anomaly['price_std']
    
    # Create visualization
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Quantity Anomalies by Category',
            'Price Anomalies Distribution',
            'High-Value Transaction Pattern',
            'Category-wise Price Variations'
        ),
        specs=[[{"type": "box"}, {"type": "histogram"}],
               [{"type": "scatter"}, {"type": "heatmap"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 1. Quantity Anomalies by Category
    fig.add_trace(
        go.Box(
            x=df_anomaly['product_category'],
            y=df_anomaly['quantity_zscore'],
            name='Quantity Z-Score',
            marker_color=COLORS[0],
            boxpoints='outliers'
        ),
        row=1, col=1
    )
    
    # 2. Price Anomalies Distribution
    fig.add_trace(
        go.Histogram(
            x=df_anomaly['price_zscore'],
            nbinsx=50,
            name='Price Z-Score Distribution',
            marker_color=COLORS[1]
        ),
        row=1, col=2
    )
    
    # 3. High-Value Transaction Pattern
    high_value_pattern = df.groupby(['transaction_datetime', 'store_location'])['total_price'].sum().reset_index()
    
    fig.add_trace(
        go.Scatter(
            x=high_value_pattern['transaction_datetime'],
            y=high_value_pattern['total_price'],
            mode='markers',
            marker=dict(
                size=8,
                color=high_value_pattern['total_price'],
                colorscale='Viridis',
                showscale=True
            ),
            name='Transaction Value'
        ),
        row=2, col=1
    )
    
    # 4. Category-wise Price Variations
    price_variation = df.groupby(['product_category', 'store_location'])['unit_price'].agg(['mean', 'std']).reset_index()
    price_variation['cv'] = price_variation['std'] / price_variation['mean'] * 100
    
    # Create pivot table for heatmap
    price_pivot = price_variation.pivot(
        index='product_category',
        columns='store_location',
        values='cv'
    )
    
    fig.add_trace(
        go.Heatmap(
            z=price_pivot.values,
            x=price_pivot.columns,
            y=price_pivot.index,
            colorscale='RdYlBu_r',
            text=np.round(price_pivot.values, 1),
            texttemplate='%{text}%',
            textfont={"size": 10},
            name='Price Variation'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="Anomaly Detection Analysis",
        showlegend=False,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR
    )
    
    # Update axes
    fig.update_xaxes(gridcolor=GRID_COLOR, showgrid=True)
    fig.update_yaxes(gridcolor=GRID_COLOR, showgrid=True)
    
    # Update specific axes labels
    fig.update_xaxes(title_text="Product Category", row=1, col=1, tickangle=45)
    fig.update_yaxes(title_text="Quantity Z-Score", row=1, col=1)
    
    fig.update_xaxes(title_text="Price Z-Score", row=1, col=2)
    fig.update_yaxes(title_text="Frequency", row=1, col=2)
    
    fig.update_xaxes(title_text="Transaction DateTime", row=2, col=1)
    fig.update_yaxes(title_text="Transaction Value ($)", row=2, col=1)
    
    fig.update_xaxes(title_text="Store Location", row=2, col=2, tickangle=45)
    fig.update_yaxes(title_text="Product Category", row=2, col=2)
    
    return fig

def get_anomaly_metrics(df):
    """Calculate anomaly detection metrics"""
    # Calculate z-scores for quantities and prices
    product_stats = df.groupby('product_id').agg({
        'quantity': ['mean', 'std'],
        'unit_price': ['mean', 'std']
    }).reset_index()
    
    product_stats.columns = ['product_id', 'qty_mean', 'qty_std', 'price_mean', 'price_std']
    
    df_metrics = df.merge(product_stats, on='product_id')
    
    # Handle zero standard deviations
    df_metrics['qty_std'] = df_metrics['qty_std'].replace(0, 1)
    df_metrics['price_std'] = df_metrics['price_std'].replace(0, 1)
    
    df_metrics['quantity_zscore'] = (df_metrics['quantity'] - df_metrics['qty_mean']) / df_metrics['qty_std']
    df_metrics['price_zscore'] = (df_metrics['unit_price'] - df_metrics['price_mean']) / df_metrics['price_std']
    
    # Calculate anomaly metrics
    quantity_anomalies = (abs(df_metrics['quantity_zscore']) > 3).mean() * 100
    price_anomalies = (abs(df_metrics['price_zscore']) > 3).mean() * 100
    high_value_transactions = (df_metrics['total_price'] > df_metrics.groupby('product_category')['total_price'].transform('mean') * 3).mean() * 100
    
    return quantity_anomalies, price_anomalies, high_value_transactions

def create_geographic_analysis(df):
    """Analyze geographic patterns and regional preferences"""
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Regional Product Preferences',
            'Transaction Patterns by Location',
            'Payment Methods by Region',
            'Customer Behavior by Location'
        ),
        specs=[[{"type": "bar"}, {"type": "box"}],
               [{"type": "pie"}, {"type": "bar"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 1. Regional Product Preferences
    regional_prefs = df.groupby(['store_location', 'product_category'])['quantity'].sum().reset_index()
    location_totals = regional_prefs.groupby('store_location')['quantity'].transform('sum')
    regional_prefs['percentage'] = regional_prefs['quantity'] / location_totals * 100
    
    # Get top categories for each location
    for location in df['store_location'].unique():
        location_data = regional_prefs[regional_prefs['store_location'] == location]
        top_categories = location_data.nlargest(3, 'percentage')
        
        fig.add_trace(
            go.Bar(
                name=location,
                x=top_categories['product_category'],
                y=top_categories['percentage'],
                text=top_categories['percentage'].apply(lambda x: f'{x:.1f}%'),
                textposition='auto',
            ),
            row=1, col=1
        )
    
    # 2. Transaction Size by Location
    fig.add_trace(
        go.Box(
            x=df['store_location'],
            y=df.groupby('transaction_id')['total_price'].sum(),
            name='Transaction Value',
            marker_color=COLORS[1],
            boxpoints='outliers'
        ),
        row=1, col=2
    )
    
    # 3. Payment Methods by Region
    payment_by_region = df.groupby(['store_location', 'payment_method'])['transaction_id'].nunique().reset_index()
    
    for location in df['store_location'].unique():
        location_data = payment_by_region[payment_by_region['store_location'] == location]
        total_transactions = location_data['transaction_id'].sum()
        location_data['percentage'] = location_data['transaction_id'] / total_transactions * 100
        
        fig.add_trace(
            go.Pie(
                labels=location_data['payment_method'],
                values=location_data['percentage'],
                name=location,
                title=location,
                domain={'row': 1, 'column': 0},
                showlegend=True
            ),
            row=2, col=1
        )
    
    # 4. Urban vs Suburban Analysis
    # Classify locations
    urban_locations = ['Downtown']
    suburban_locations = ['Suburb North', 'Suburb South']
    
    df['location_type'] = df['store_location'].apply(
        lambda x: 'Urban' if x in urban_locations else 'Suburban' if x in suburban_locations else 'Other'
    )
    
    location_metrics = df.groupby('location_type').agg({
        'total_price': 'mean',
        'quantity': 'mean',
        'loyalty_member': 'mean',
        'transaction_id': 'nunique'
    }).reset_index()
    
    fig.add_trace(
        go.Bar(
            x=location_metrics['location_type'],
            y=location_metrics['total_price'],
            name='Avg Transaction Value',
            text=location_metrics['total_price'].apply(lambda x: f'${x:.2f}'),
            textposition='auto',
            marker_color=COLORS[3]
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="Geographic Analysis",
        showlegend=True,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update axes
    fig.update_xaxes(gridcolor=GRID_COLOR, showgrid=True)
    fig.update_yaxes(gridcolor=GRID_COLOR, showgrid=True)
    
    # Update specific axes labels
    fig.update_xaxes(title_text="Product Category", row=1, col=1, tickangle=45)
    fig.update_yaxes(title_text="Percentage of Sales", row=1, col=1)
    
    fig.update_xaxes(title_text="Store Location", row=1, col=2)
    fig.update_yaxes(title_text="Transaction Value ($)", row=1, col=2)
    
    fig.update_xaxes(title_text="Location Type", row=2, col=2)
    fig.update_yaxes(title_text="Average Transaction Value ($)", row=2, col=2)
    
    return fig

def get_geographic_metrics(df):
    """Calculate key geographic metrics"""
    # Calculate urban vs suburban metrics
    urban_locations = ['Downtown']
    suburban_locations = ['Suburb North', 'Suburb South']
    
    df['location_type'] = df['store_location'].apply(
        lambda x: 'Urban' if x in urban_locations else 'Suburban' if x in suburban_locations else 'Other'
    )
    
    # Calculate metrics by location type
    urban_avg_transaction = df[df['location_type'] == 'Urban']['total_price'].mean()
    suburban_avg_transaction = df[df['location_type'] == 'Suburban']['total_price'].mean()
    urban_loyalty_rate = df[df['location_type'] == 'Urban']['loyalty_member'].mean() * 100
    
    return urban_avg_transaction, suburban_avg_transaction, urban_loyalty_rate

def create_financial_analysis(df):
    """Analyze financial performance and profitability metrics"""
    # Add margin calculations
    df_finance = df.copy()
    
    # Assume different margin percentages for different categories
    category_margins = {
        'Organic': 0.45,  # 45% margin
        'Meat': 0.35,
        'Dairy': 0.30,
        'Produce': 0.25,
        'Bakery': 0.40,
        'Frozen Foods': 0.35,
        'Snacks': 0.50,
        'Beverages': 0.45,
        'Pantry': 0.40,
        'Personal Care': 0.55
    }
    
    # Calculate cost and margins
    df_finance['margin_percentage'] = df_finance['product_category'].map(category_margins)
    df_finance['unit_cost'] = df_finance['unit_price'] * (1 - df_finance['margin_percentage'])
    df_finance['margin'] = df_finance['total_price'] - (df_finance['unit_cost'] * df_finance['quantity'])
    
    # Create visualization
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Profit Margins by Category',
            'Discount Impact on Margins',
            'Margin vs Volume Analysis',
            'Daily Profit Trends'
        ),
        specs=[[{"type": "bar"}, {"type": "scatter"}],
               [{"type": "scatter"}, {"type": "scatter"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 1. Category Margins
    category_profits = df_finance.groupby('product_category').agg({
        'total_price': 'sum',
        'margin': 'sum'
    }).reset_index()
    
    category_profits['margin_percent'] = category_profits['margin'] / category_profits['total_price'] * 100
    category_profits = category_profits.sort_values('margin_percent', ascending=True)
    
    fig.add_trace(
        go.Bar(
            y=category_profits['product_category'],
            x=category_profits['margin_percent'],
            orientation='h',
            marker_color=COLORS[0],
            text=category_profits['margin_percent'].apply(lambda x: f'{x:.1f}%'),
            textposition='auto',
        ),
        row=1, col=1
    )
    
    # 2. Discount Impact
    discount_impact = df_finance.groupby('discount_applied').agg({
        'total_price': 'sum',
        'margin': 'sum',
        'quantity': 'sum'
    }).reset_index()
    
    fig.add_trace(
        go.Scatter(
            x=discount_impact['discount_applied'].apply(lambda x: f"{x*100:.0f}%"),
            y=discount_impact['margin'],
            name='Total Margin',
            mode='lines+markers',
            marker=dict(size=10),
            line=dict(color=COLORS[1], width=3)
        ),
        row=1, col=2
    )
    
    fig.add_trace(
        go.Scatter(
            x=discount_impact['discount_applied'].apply(lambda x: f"{x*100:.0f}%"),
            y=discount_impact['quantity'],
            name='Units Sold',
            mode='lines+markers',
            marker=dict(size=10),
            line=dict(color=COLORS[2], width=3),
            yaxis='y2'
        ),
        row=1, col=2
    )
    
    # 3. Margin vs Volume
    product_metrics = df_finance.groupby('product_name').agg({
        'quantity': 'sum',
        'margin': 'sum'
    }).reset_index()
    
    fig.add_trace(
        go.Scatter(
            x=product_metrics['quantity'],
            y=product_metrics['margin'],
            mode='markers',
            marker=dict(
                size=8,
                color=COLORS[3],
                opacity=0.6
            ),
            text=product_metrics['product_name'],
            hovertemplate="<b>%{text}</b><br>" +
                         "Quantity: %{x}<br>" +
                         "Margin: $%{y:.2f}<extra></extra>"
        ),
        row=2, col=1
    )
    
    # 4. Daily Profit Trends
    daily_profits = df_finance.groupby(df_finance['transaction_datetime'].dt.date).agg({
        'margin': 'sum',
        'total_price': 'sum'
    }).reset_index()
    
    daily_profits['margin_percent'] = daily_profits['margin'] / daily_profits['total_price'] * 100
    
    fig.add_trace(
        go.Scatter(
            x=daily_profits['transaction_datetime'],
            y=daily_profits['margin'],
            name='Daily Margin',
            line=dict(color=COLORS[0], width=2)
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="Financial Performance Analysis",
        showlegend=True,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Update axes
    fig.update_xaxes(gridcolor=GRID_COLOR, showgrid=True)
    fig.update_yaxes(gridcolor=GRID_COLOR, showgrid=True)
    
    # Update specific axes labels
    fig.update_xaxes(title_text="Margin Percentage", row=1, col=1)
    fig.update_yaxes(title_text="Product Category", row=1, col=1)
    
    fig.update_xaxes(title_text="Discount Level", row=1, col=2)
    fig.update_yaxes(title_text="Total Margin ($)", row=1, col=2)
    fig.update_yaxes(title_text="Units Sold", secondary_y=True, row=1, col=2)
    
    fig.update_xaxes(title_text="Date", row=2, col=1)
    fig.update_yaxes(title_text="Daily Margin ($)", row=2, col=1)
    
    return fig

def get_financial_metrics(df):
    """Calculate key financial metrics"""
    # Add margin calculations
    category_margins = {
        'Organic': 0.45,
        'Meat': 0.35,
        'Dairy': 0.30,
        'Produce': 0.25,
        'Bakery': 0.40,
        'Frozen Foods': 0.35,
        'Snacks': 0.50,
        'Beverages': 0.45,
        'Pantry': 0.40,
        'Personal Care': 0.55
    }
    
    df_finance = df.copy()
    df_finance['margin_percentage'] = df_finance['product_category'].map(category_margins)
    df_finance['unit_cost'] = df_finance['unit_price'] * (1 - df_finance['margin_percentage'])
    df_finance['margin'] = df_finance['total_price'] - (df_finance['unit_cost'] * df_finance['quantity'])
    
    # Calculate metrics
    overall_margin = (df_finance['margin'].sum() / df_finance['total_price'].sum()) * 100
    
    # Fix the line continuation
    discount_margin = (df_finance[df_finance['discount_applied'] > 0]['margin'].sum() / 
                      df_finance[df_finance['discount_applied'] > 0]['total_price'].sum() * 100)
    
    highest_margin_category = df_finance.groupby('product_category').agg({
        'margin': 'sum',
        'total_price': 'sum'
    }).assign(
        margin_percent=lambda x: x['margin'] / x['total_price'] * 100
    )['margin_percent'].idxmax()
    
    return overall_margin, discount_margin, highest_margin_category

def get_retention_metrics(df):
    """Calculate key retention metrics"""
    # Calculate repeat purchase rate
    total_customers = df['customer_id'].nunique()
    repeat_customers = df.groupby('customer_id')['transaction_id'].nunique()
    repeat_rate = (repeat_customers > 1).mean() * 100
    
    # Calculate average purchase frequency (monthly)
    date_range = (df['transaction_datetime'].max() - df['transaction_datetime'].min()).days / 30
    avg_monthly_frequency = repeat_customers.mean() / date_range
    
    # Calculate churn risk
    last_purchase_date = df['transaction_datetime'].max()
    customer_last_purchase = df.groupby('customer_id')['transaction_datetime'].max()
    days_since_purchase = (last_purchase_date - customer_last_purchase).dt.days
    churn_risk = (days_since_purchase > 90).mean() * 100
    
    return repeat_rate, avg_monthly_frequency, churn_risk

def create_retention_analysis(df):
    """Analyze customer retention and churn patterns"""
    # Calculate days between purchases for each customer
    customer_purchases = df.groupby(['customer_id', 'transaction_datetime']).size().reset_index()
    customer_purchases = customer_purchases.sort_values(['customer_id', 'transaction_datetime'])
    
    # Calculate days between purchases
    customer_purchases['days_between_purchases'] = customer_purchases.groupby('customer_id')['transaction_datetime'].diff().dt.days
    
    # Calculate last purchase date for each customer
    last_purchase_date = df['transaction_datetime'].max()
    customer_last_purchase = df.groupby('customer_id').agg({
        'transaction_datetime': 'max',
        'loyalty_member': 'first'
    }).reset_index()
    
    customer_last_purchase['days_since_purchase'] = (last_purchase_date - customer_last_purchase['transaction_datetime']).dt.days
    
    # Create visualization
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Purchase Frequency Distribution',
            'Customer Recency Analysis',
            'Retention by Customer Segment',
            'Churn Risk Analysis'
        ),
        specs=[[{"type": "histogram"}, {"type": "box"}],
               [{"type": "bar"}, {"type": "scatter"}]],
        vertical_spacing=0.15,
        horizontal_spacing=0.1
    )
    
    # 1. Purchase Frequency Distribution
    fig.add_trace(
        go.Histogram(
            x=customer_purchases['days_between_purchases'],
            nbinsx=30,
            name='Days Between Purchases',
            marker_color=COLORS[0]
        ),
        row=1, col=1
    )
    
    # 2. Customer Recency Analysis
    fig.add_trace(
        go.Box(
            x=customer_last_purchase['loyalty_member'],
            y=customer_last_purchase['days_since_purchase'],
            name='Days Since Last Purchase',
            marker_color=COLORS[1],
            boxpoints='outliers'
        ),
        row=1, col=2
    )
    
    # 3. Retention by Customer Segment
    # Calculate purchase frequency segments
    purchase_frequency = df.groupby('customer_id')['transaction_id'].nunique()
    frequency_segments = pd.qcut(purchase_frequency, q=3, labels=['Low', 'Medium', 'High'])
    retention_by_segment = frequency_segments.value_counts()
    
    fig.add_trace(
        go.Bar(
            x=retention_by_segment.index,
            y=retention_by_segment.values,
            marker_color=COLORS[2],
            text=retention_by_segment.values,
            textposition='auto',
        ),
        row=2, col=1
    )
    
    # 4. Churn Risk Analysis
    # Define churn risk based on days since last purchase
    risk_thresholds = [0, 30, 60, 90, float('inf')]
    risk_labels = ['Low', 'Medium', 'High', 'Very High']
    customer_last_purchase['churn_risk'] = pd.cut(
        customer_last_purchase['days_since_purchase'],
        bins=risk_thresholds,
        labels=risk_labels
    )
    
    churn_risk_counts = customer_last_purchase['churn_risk'].value_counts()
    
    fig.add_trace(
        go.Scatter(
            x=churn_risk_counts.index,
            y=churn_risk_counts.values,
            mode='lines+markers',
            line=dict(color=COLORS[3], width=3),
            marker=dict(size=10),
            text=churn_risk_counts.values,
            textposition='top center'
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        height=800,
        title_text="Customer Retention Analysis",
        showlegend=False,
        paper_bgcolor=BACKGROUND_COLOR,
        plot_bgcolor=BACKGROUND_COLOR
    )
    
    # Update axes
    fig.update_xaxes(gridcolor=GRID_COLOR, showgrid=True)
    fig.update_yaxes(gridcolor=GRID_COLOR, showgrid=True)
    
    # Update specific axes labels
    fig.update_xaxes(title_text="Days Between Purchases", row=1, col=1)
    fig.update_yaxes(title_text="Number of Customers", row=1, col=1)
    
    fig.update_xaxes(title_text="Loyalty Status", row=1, col=2)
    fig.update_yaxes(title_text="Days Since Last Purchase", row=1, col=2)
    
    fig.update_xaxes(title_text="Purchase Frequency Segment", row=2, col=1)
    fig.update_yaxes(title_text="Number of Customers", row=2, col=1)
    
    fig.update_xaxes(title_text="Churn Risk Level", row=2, col=2)
    fig.update_yaxes(title_text="Number of Customers", row=2, col=2)
    
    return fig

def main():
    st.title("🛒 Grocery Store Analytics Dashboard")
    
    # Load data
    with st.spinner("Loading data..."):
        df = load_data()
    
    # Key Metrics
    st.header("📊 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_sales = df['total_price'].sum()
        st.metric("Total Sales", f"${total_sales:,.2f}")
    
    with col2:
        total_transactions = df['transaction_id'].nunique()
        st.metric("Total Transactions", f"{total_transactions:,}")
    
    with col3:
        avg_transaction = total_sales / total_transactions
        st.metric("Avg Transaction Value", f"${avg_transaction:.2f}")
    
    with col4:
        total_customers = df['customer_id'].nunique()
        st.metric("Unique Customers", f"{total_customers:,}")
    
    # Time Series Analysis
    st.header("📈 Sales Over Time")
    time_series_fig = create_time_series(df)
    st.plotly_chart(time_series_fig, use_container_width=True)
    
    # Category and Store Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("🏪 Store Performance")
        store_fig = create_store_performance(df)
        st.plotly_chart(store_fig, use_container_width=True)
    
    with col2:
        st.header("🛍️ Category Sales")
        category_fig = create_category_sales(df)
        st.plotly_chart(category_fig, use_container_width=True)
    
    # Payment and Hourly Analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.header("💳 Payment Methods")
        payment_fig = create_payment_distribution(df)
        st.plotly_chart(payment_fig, use_container_width=True)
    
    with col2:
        st.header("⏰ Hourly Sales Pattern")
        hourly_fig = create_hourly_pattern(df)
        st.plotly_chart(hourly_fig, use_container_width=True)
    
    # Add Sales Performance Dashboard
    st.header("📊 Sales Performance Analysis")
    sales_performance_fig = create_sales_performance_dashboard(df)
    st.plotly_chart(sales_performance_fig, use_container_width=True)
    
    # Add Product Performance Analysis
    st.header("📈 Product Performance Analysis")
    product_performance_fig = create_product_performance_analysis(df)
    st.plotly_chart(product_performance_fig, use_container_width=True)
    
    # Add Customer Behavior Analysis
    st.header("👥 Customer Behavior Analysis")
    
    # Add customer behavior metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        loyalty_percentage = (df['loyalty_member'].mean() * 100)
        st.metric("Loyalty Membership", f"{loyalty_percentage:.1f}%")
    
    with col2:
        avg_customer_transactions = df.groupby('customer_id')['transaction_id'].nunique().mean()
        st.metric("Avg Transactions per Customer", f"{avg_customer_transactions:.1f}")
    
    with col3:
        avg_customer_spend = df.groupby('customer_id')['total_price'].sum().mean()
        st.metric("Avg Customer Spend", f"${avg_customer_spend:.2f}")
    
    # Add customer behavior visualizations
    customer_behavior_fig = create_customer_behavior_analysis(df)
    st.plotly_chart(customer_behavior_fig, use_container_width=True)
    
    # Add customer preferences analysis
    st.subheader("🛒 Customer Product Preferences")
    customer_prefs_fig = create_customer_product_preferences(df)
    st.plotly_chart(customer_prefs_fig, use_container_width=True)
    
    # Add Inventory & Supply Chain Analytics
    st.header("📦 Inventory & Supply Chain Analytics")
    
    # Add inventory metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_daily_volume = df['quantity'].sum() / (df['transaction_datetime'].max() - df['transaction_datetime'].min()).days
        st.metric("Avg Daily Sales Volume", f"{avg_daily_volume:.1f} units")
    
    with col2:
        category_turnover = df.groupby('product_category')['quantity'].sum().mean()
        st.metric("Avg Category Turnover", f"{category_turnover:.1f} units")
    
    with col3:
        slow_moving_threshold = 1.0  # 1 unit per day
        product_daily_sales = df.groupby('product_id')['quantity'].sum() / (df['transaction_datetime'].max() - df['transaction_datetime'].min()).days
        slow_moving_pct = (product_daily_sales < slow_moving_threshold).mean() * 100
        st.metric("Slow-Moving Products", f"{slow_moving_pct:.1f}%")
    
    # Add inventory movement analysis
    inventory_fig = create_inventory_analytics(df)
    st.plotly_chart(inventory_fig, use_container_width=True)
    
    # Add demand forecasting
    st.subheader("📈 Demand Forecasting")
    forecast_fig = create_demand_forecast(df)
    st.plotly_chart(forecast_fig, use_container_width=True)
    
    # Add Operational Efficiency Analysis
    st.header("⚡ Operational Efficiency")
    
    # Add operational metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        peak_hour = df.groupby(df['transaction_datetime'].dt.hour)['transaction_id'].nunique().idxmax()
        st.metric("Peak Hour", f"{peak_hour:02d}:00")
    
    with col2:
        avg_trans_time = df.sort_values('transaction_datetime').groupby('store_location')['transaction_datetime'].diff().dt.total_seconds().mean()
        st.metric("Avg Transaction Time", f"{avg_trans_time:.1f} sec")
    
    with col3:
        weekend_ratio = (df[df['transaction_datetime'].dt.weekday >= 5]['total_price'].sum() / 
                        df[df['transaction_datetime'].dt.weekday < 5]['total_price'].sum() * 100)
        st.metric("Weekend Sales Ratio", f"{weekend_ratio:.1f}%")
    
    # Add operational efficiency visualization
    operational_fig = create_operational_efficiency_analysis(df)
    st.plotly_chart(operational_fig, use_container_width=True)
    
    # Add Marketing & Promotions Analysis
    st.header("🎯 Marketing & Promotions")
    
    # Add marketing metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_discount = df[df['discount_applied'] > 0]['discount_applied'].mean() * 100
        st.metric("Average Discount", f"{avg_discount:.1f}%")
    
    with col2:
        promo_sales_pct = (df[df['discount_applied'] > 0]['total_price'].sum() / 
                          df['total_price'].sum() * 100)
        st.metric("Sales with Promotions", f"{promo_sales_pct:.1f}%")
    
    with col3:
        avg_basket_promo = df[df['discount_applied'] > 0].groupby('transaction_id')['total_price'].mean()
        avg_basket_regular = df[df['discount_applied'] == 0].groupby('transaction_id')['total_price'].mean()
        basket_lift = ((avg_basket_promo.mean() / avg_basket_regular.mean()) - 1) * 100
        st.metric("Promotional Basket Lift", f"{basket_lift:+.1f}%")
    
    # Add marketing analysis visualization
    marketing_fig = create_marketing_analysis(df)
    st.plotly_chart(marketing_fig, use_container_width=True)
    
    # Add promotion effectiveness analysis
    st.subheader("📊 Promotion Effectiveness")
    promo_fig = create_promotion_effectiveness(df)
    st.plotly_chart(promo_fig, use_container_width=True)
    
    # Add Anomaly Detection Analysis
    st.header("🚨 Anomaly Detection")
    
    # Add anomaly metrics
    quantity_anomalies, price_anomalies, high_value_transactions = get_anomaly_metrics(df)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Quantity Anomalies", f"{quantity_anomalies:.1f}%",
                 help="Transactions with quantities > 3 standard deviations from mean")
    
    with col2:
        st.metric("Price Anomalies", f"{price_anomalies:.1f}%",
                 help="Transactions with prices > 3 standard deviations from mean")
    
    with col3:
        st.metric("High-Value Transactions", f"{high_value_transactions:.1f}%",
                 help="Transactions > 3x category average")
    
    # Add anomaly detection visualization
    anomaly_fig = create_anomaly_detection(df)
    st.plotly_chart(anomaly_fig, use_container_width=True)
    
    # Add potential fraud alerts
    st.subheader("⚠️ Potential Anomalies")
    
    # Show suspicious transactions
    suspicious_df = df[
        (df['quantity'] > df.groupby('product_id')['quantity'].transform('mean') + 
         3 * df.groupby('product_id')['quantity'].transform('std')) |
        (df['unit_price'] > df.groupby('product_id')['unit_price'].transform('mean') + 
         3 * df.groupby('product_id')['unit_price'].transform('std'))
    ]
    
    if len(suspicious_df) > 0:
        st.write(f"Found {len(suspicious_df)} suspicious transactions:")
        st.dataframe(
            suspicious_df[['transaction_datetime', 'store_location', 'product_name', 
                         'quantity', 'unit_price', 'total_price']]
        )
    else:
        st.write("No suspicious transactions found.")
    
    # Add Customer Retention Analysis
    st.header("🔄 Customer Retention & Churn")
    
    # Add retention metrics
    repeat_rate, avg_monthly_frequency, churn_risk = get_retention_metrics(df)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Repeat Purchase Rate", f"{repeat_rate:.1f}%",
                 help="Percentage of customers with more than one purchase")
    
    with col2:
        st.metric("Avg Monthly Frequency", f"{avg_monthly_frequency:.1f}",
                 help="Average number of purchases per customer per month")
    
    with col3:
        st.metric("Churn Risk", f"{churn_risk:.1f}%",
                 help="Percentage of customers inactive for 90+ days")
    
    # Add retention visualization
    retention_fig = create_retention_analysis(df)
    st.plotly_chart(retention_fig, use_container_width=True)
    
    # Add customer segments at risk
    st.subheader("🎯 Customers at Risk")
    
    # Identify customers at risk of churning
    last_purchase_date = df['transaction_datetime'].max()
    customer_status = df.groupby('customer_id').agg({
        'transaction_datetime': 'max',
        'total_price': 'sum',
        'transaction_id': 'nunique',
        'loyalty_member': 'first'
    }).reset_index()
    
    customer_status['days_since_purchase'] = (last_purchase_date - customer_status['transaction_datetime']).dt.days
    at_risk_customers = customer_status[
        (customer_status['days_since_purchase'] > 60) &
        (customer_status['total_price'] > customer_status['total_price'].median())
    ]
    
    if len(at_risk_customers) > 0:
        st.write(f"Found {len(at_risk_customers)} high-value customers at risk of churning:")
        st.dataframe(
            at_risk_customers[['customer_id', 'days_since_purchase', 'total_price', 
                             'transaction_id', 'loyalty_member']]
            .sort_values('total_price', ascending=False)
        )
    else:
        st.write("No high-value customers currently at risk of churning.")
    
    # Add Geographic Analysis
    st.header("🗺️ Geographic Analysis")
    
    # Add geographic metrics
    urban_avg_transaction, suburban_avg_transaction, urban_loyalty_rate = get_geographic_metrics(df)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        urban_suburban_ratio = (urban_avg_transaction / suburban_avg_transaction - 1) * 100
        st.metric("Urban vs Suburban Spending", 
                 f"{urban_suburban_ratio:+.1f}%",
                 help="Difference in average transaction value between urban and suburban locations")
    
    with col2:
        st.metric("Urban Loyalty Rate", 
                 f"{urban_loyalty_rate:.1f}%",
                 help="Percentage of urban customers who are loyalty members")
    
    with col3:
        downtown_volume = (df['store_location'] == 'Downtown').mean() * 100
        st.metric("Downtown Transaction Share", 
                 f"{downtown_volume:.1f}%",
                 help="Percentage of transactions occurring at downtown location")
    
    # Add geographic visualization
    geographic_fig = create_geographic_analysis(df)
    st.plotly_chart(geographic_fig, use_container_width=True)
    
    # Add regional insights
    st.subheader("📍 Regional Insights")
    
    # Calculate and display top products by location
    for location in df['store_location'].unique():
        location_data = df[df['store_location'] == location]
        top_products = location_data.groupby('product_name')['quantity'].sum().nlargest(3)
        
        st.write(f"**{location}** top products:")
        for product, quantity in top_products.items():
            st.write(f"- {product}: {quantity:,.0f} units")
    
    # Add Financial Analytics
    st.header("💰 Financial Analytics")
    
    # Add financial metrics
    overall_margin, discount_margin, highest_margin_category = get_financial_metrics(df)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Profit Margin", 
                 f"{overall_margin:.1f}%",
                 help="Average profit margin across all products")
    
    with col2:
        st.metric("Discounted Sales Margin", 
                 f"{discount_margin:.1f}%",
                 help="Average margin on discounted sales")
        
    with col3:
        st.metric("Highest Margin Category", 
                 highest_margin_category,
                 help="Product category with highest profit margin")
    
    # Add financial analysis visualization
    financial_fig = create_financial_analysis(df)
    st.plotly_chart(financial_fig, use_container_width=True)
    
    # Add margin insights
    st.subheader("📊 Margin Analysis Insights")
    
    # Calculate and display margin trends
    category_margins = df.groupby('product_category').agg({
        'total_price': 'sum',
        'quantity': 'sum'
    }).reset_index()
    
    st.write("**Category Performance:**")
    for _, row in category_margins.sort_values('total_price', ascending=False).head(3).iterrows():
        st.write(f"- {row['product_category']}: ${row['total_price']:,.2f} revenue ({row['quantity']:,.0f} units)")
    
    # Detailed Data View
    st.header("🔍 Detailed Data View")
    if st.checkbox("Show Raw Data"):
        st.dataframe(df)

if __name__ == "__main__":
    main() 