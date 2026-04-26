##  🛍️ Project Title: End-To-end  Retail Data Analytics Project 

1. Project Goal: The goal of this project is to analyze retail consumer shopping data to uncover customer behavior patterns across demographics, product categories, shopping channels, seasons, and payment methods. The analysis aims to identify the factors that influence purchase decisions and repeat buying behavior, and provide actionable recommendations to improve customer engagement, optimize marketing efforts, and support better product strategy.
2. Business Problem Statement: 
Business Problem - A leading retail company wants to better understand how customers shop across different demographics, product categories, and sales channels. Management has observed shifts in purchasing behavior and wants to determine what drives customer decisions and repeat purchases. Key factors of interest include discounts, product reviews, seasonal trends, payment preferences, and online versus offline shopping behavior. The company aims to use consumer shopping data to identify meaningful trends and generate insights that can improve sales performance, customer satisfaction, retention, marketing effectiveness, and product strategy.

## 📊 Expected Data Columns

Csv file columns are here :

| Column name | Type | Description |
|---|---|---|
| `customer_id` | number | Unique customer identifier |
| `age` | number | Customer age (18–70) |
| `gender` | text | Male / Female |
| `item_purchased` | text | Name of item bought |
| `category` | text | Clothing / Accessories / Footwear / Outerwear |
| `purchase_amount_(usd)` | number | Purchase value in USD |
| `location` | text | US state or city |
| `size` | text | S / M / L / XL |
| `color` | text | Item colour |
| `season` | text | Spring / Summer / Fall / Winter |
| `review_rating` | decimal | 1.0 – 5.0 |
| `subscription_status` | text | Yes / No |
| `shipping_type` | text | Free Shipping / Express / Standard etc. |
| `discount_applied` | text | Yes / No |
| `previous_purchases` | number | Number of past purchases |
| `payment_method` | text | PayPal / Cash / Credit Card etc. |
| `frequency_of_purchases` | text | Weekly / Monthly / Annually etc. |
| `age_group` | text | Auto-created if missing (18-25, 26-35 …) |
| `frequency_purchase_days` | number | Auto-created if missing (7, 14, 30 …) |

## 📁 Project Structure
Consumer-behavior-Data-Analysis-Project-1/
├── README.md
├── data
│   ├── 01_raw
│   │   └── customer_shopping_behavior.csv
│   └── 02_processed
│       └── customer_data_cleaned.csv
├── notebooks
│   ├── 01_data_cleaning.py
│   ├── 02_exploratory_data_analysis.ipynb
│   ├── customer_app.py
│   └── requirements.txt
└── report_dashboard
    ├── Cust_dashboard_1.png
    ├── Cust_dashboard_2.png
    ├── Cust_dashboard_3.png
    ├── Cust_dashboard_4.png
    └── Cust_dashboard_5.png

## ⚙️ Requirements Tool and Tecnologies
- Python
- Pandas
- NumPy
- Matplotlib
- Seaborn 
- Power BI
- Jupyter Notebook
- streamlit
- plotly
- openpyxl

# 🛍️ Customer Shopping Behaviour Dashboard

A fully interactive data science dashboard built with **Python**, **Streamlit**, and **Plotly**.  
Load your customer shopping dataset, explore insights through live charts, and filter everything from the sidebar — instantly.

## 📸 The Dashboard Shows

| Section | What you see |
|---|---|
| KPI Cards | Total revenue, avg order value, avg rating, subscription rate, avg previous purchases |
| Revenue Breakdown | Revenue by category and by season |
| Top Items | Top 10 items by revenue, revenue by age group |
| Customer Profile | Payment method, gender, shipping type, size — all as donut charts |
| Behaviour | Purchase frequency, review rating distribution |
| Purchase Cycle | Days between purchases by category and gender |
| Scatter Plot | Age vs spend, coloured by category, sized by loyalty |
| Discount Analysis | Avg spend and rating split by discount, promo code, and subscription |
| Locations | Top 15 locations by revenue |
| Raw Data | Filterable table with CSV download button |

## 🚀 How to Run

**Step 1 — Open your terminal or VS Code terminal**

**Step 2 — Navigate to your project folder**
cd path/to/your/project/folder

For example:
cd C:/Users/YourName/Documents/shopping-dashboard

**Step 3 — Run the dashboard**
streamlit run customer_app.py

**Step 4 — Your browser opens automatically at:**
Local URL: http://localhost:8501
Network URL: http://192.168.1.156:8501

## 🔧 Sidebar Filters

All charts update instantly when you change any filter:

| Filter | What it does |
|---|---|
| **Season** | Show only Spring / Summer / Fall / Winter orders |
| **Gender** | Filter by Male or Female customers |
| **Category** | Show only selected product categories |
| **Subscription status** | Filter subscribed vs non-subscribed customers |
| **Discount applied** | Filter orders where discount was or was not used |
| **Age range** | Slider to narrow customer age range |
| **Purchase amount** | Slider to filter by order value |

## 📄 Licence

This project is open for personal and educational use.

## 👤 Author

Hey, I am Manisha. I build real-time data analytics projects and break them down into clear, structured steps so ayone can easily follow and execute them.

