# Grocery Store Analytics Dashboard

A comprehensive analytics dashboard for grocery store data analysis built with Streamlit and Python. This dashboard provides real-time insights into sales patterns, customer behavior, marketing effectiveness, and operational efficiency.

## 🌟 Features

### 📊 Sales & Revenue Analytics
- Daily sales trends and transaction volume
- Product category performance
- Store location comparisons
- Payment method distribution

### 🎯 Marketing & Promotions
- Discount impact analysis
- Promotional effectiveness
- Customer segment response
- Holiday performance tracking

### 🔄 Customer Retention & Churn
- Purchase frequency patterns
- Customer recency analysis
- Churn risk identification
- High-value customer tracking

### 🗺️ Geographic Analysis
- Regional product preferences
- Urban vs suburban behavior
- Store location performance
- Payment method variations by region

### 💰 Financial Analytics
- Product category margins
- Discount impact on profitability
- Volume vs margin analysis
- Daily profit trends

### 🚨 Anomaly Detection
- Unusual transaction patterns
- Price anomalies
- Quantity outliers
- High-value transaction monitoring

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- pip

### Installation

1. Clone the repository
```bash
git clone https://github.com/imzeeshaan/grocery-analytics.git
cd grocery-analytics
```

2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages
```bash
pip install streamlit pandas plotly numpy
```

### Running the Application

#### Local Development
1. Generate sample data
```bash
python grocery_data_generator.py
```

2. Launch the dashboard
```bash
streamlit run grocery_analysis_app.py
```

#### Streamlit Cloud Deployment
1. Fork this repository
2. Go to [Streamlit Cloud](https://streamlit.io/cloud)
3. Create a new app
4. Select your forked repository
5. Set the main file path as: `grocery_analysis_app.py`
6. Deploy!

## 📊 Data Structure

The application uses transaction data with the following schema:
```python
{
    'transaction_id': str,          # Unique transaction identifier
    'transaction_datetime': datetime,# Date and time of transaction
    'store_location': str,          # Store location (Downtown, Suburb North, etc.)
    'customer_id': str,             # Unique customer identifier
    'product_id': str,              # Unique product identifier
    'product_name': str,            # Product name
    'product_category': str,        # Product category
    'quantity': int,                # Number of items purchased
    'unit_price': float,            # Price per unit
    'total_price': float,           # Total transaction amount
    'payment_method': str,          # Payment method used
    'loyalty_member': bool,         # Customer loyalty status
    'discount_applied': float       # Discount percentage (0-1)
}
```

## 🛠️ Built With

- [Streamlit](https://streamlit.io/) - Web application framework
- [Plotly](https://plotly.com/) - Interactive visualization library
- [Pandas](https://pandas.pydata.org/) - Data manipulation library
- [NumPy](https://numpy.org/) - Numerical computing library

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/NewAnalysis`)
3. Commit your changes (`git commit -m 'Add new analysis feature'`)
4. Push to the branch (`git push origin feature/NewAnalysis`)
5. Open a Pull Request

## 📧 Contact

Project Link: [https://github.com/imzeeshaan/grocery-analytics](https://github.com/imzeeshaan/grocery-analytics)

## 🙏 Acknowledgments

- Inspired by real-world retail analytics needs
- Streamlit community for excellent documentation and examples
- Contributors who help improve this project