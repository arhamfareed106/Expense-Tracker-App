import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import seaborn as sns
import os

# Setup
conn = sqlite3.connect('expense.db')
cursor = conn.cursor()

# Create table
cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    category TEXT NOT NULL,
    amount REAL NOT NULL
)
''')
conn.commit()

# Add sample data if empty
cursor.execute('SELECT COUNT(*) FROM expenses')
if cursor.fetchone()[0] == 0:
    sample_data = [
        ('2024-06-01', 'Food', 25.5),
        ('2024-06-02', 'Transport', 10.0),
        ('2024-06-03', 'Shopping', 50.0),
        ('2024-06-10', 'Food', 30.0),
        ('2024-07-01', 'Bills', 100.0),
        ('2024-07-05', 'Food', 20.0),
        ('2024-07-06', 'Transport', 15.0),
        ('2024-07-10', 'Shopping', 60.0),
        ('2024-07-12', 'Entertainment', 40.0),
        ('2024-07-15', 'Health', 75.0),
        ('2024-07-18', 'Food', 22.0),
        ('2024-07-20', 'Transport', 12.0),
        ('2024-07-22', 'Bills', 110.0),
        ('2024-07-25', 'Shopping', 80.0),
        ('2024-07-28', 'Entertainment', 55.0),
        ('2024-07-30', 'Health', 60.0)
    ]
    cursor.executemany('INSERT INTO expenses (date, category, amount) VALUES (?, ?, ?)', sample_data)
    conn.commit()

# Load data
df = pd.read_sql('SELECT date, category, amount FROM expenses', conn, parse_dates=['date'])
df.set_index('date', inplace=True)

# Prepare Data
monthly = df['amount'].resample('M').sum()
category_totals = df.groupby('category')['amount'].sum()
monthly_mean = monthly.rolling(window=2).mean()
daily = df['amount'].resample('D').sum()

# Highest day annotation
highest_day = daily.idxmax()
highest_value = daily.max()

# Plot all charts on one dashboard
fig, axs = plt.subplots(2, 3, figsize=(18, 10))
fig.suptitle('💼 Expense Dashboard', fontsize=18)

# 1. Monthly Expense Trend (Bar)
axs[0, 0].bar(monthly.index.to_series().dt.strftime('%Y-%m'), monthly.values, color='skyblue')
axs[0, 0].set_title('Monthly Expenses')
axs[0, 0].set_ylabel('Amount')

# 2. Category Breakdown (Pie)
axs[0, 1].pie(category_totals, labels=category_totals.index, autopct='%1.1f%%', startangle=140)
axs[0, 1].set_title('Spending by Category')

# 3. Moving Average Line
axs[0, 2].plot(monthly.index, monthly.values, label='Monthly', color='blue')
axs[0, 2].plot(monthly_mean.index, monthly_mean.values, label='2-Month Avg', linestyle='--', color='orange')
axs[0, 2].legend()
axs[0, 2].set_title('Monthly Trend with Moving Avg')

# 4. Top Categories (Bar)
top_cats = category_totals.sort_values(ascending=True)
axs[1, 0].barh(top_cats.index, top_cats.values, color='purple')
axs[1, 0].set_title('Top Spending Categories')

# 5. Daily Spending (Line)
axs[1, 1].plot(daily.index, daily.values, color='green')
axs[1, 1].axvline(highest_day, color='red', linestyle='--', label='Highest Day')
axs[1, 1].annotate(f'Highest: {highest_value}',
                   xy=(highest_day, highest_value),
                   xytext=(highest_day, highest_value + 10),
                   arrowprops=dict(facecolor='red', shrink=0.05),
                   fontsize=8)
axs[1, 1].set_title('Daily Spending Trend')
axs[1, 1].legend()

# # 6. Summary Stats Plotm
# axs[1, 2].axis('on')
# axs[1, 2].text(0.1, 0.8, f'Total Spend: ₹{df["amount"].sum():.2f}', fontsize=12)
# axs[1, 2].text(0.1, 0.6, f'Avg Monthly: ₹{monthly.mean():.2f}', fontsize=12)
# axs[1, 2].text(0.1, 0.4, f'Max Category: {top_cats.idxmax()} ₹{top_cats.max():.2f}', fontsize=12)
# axs[1, 2].set_title('📊 Summary Stats')
# axs[1, 2].axis('off')

# plt.tight_layout(rect=(0, 0.03, 1, 0.95))
# plt.show()

# # -------------------------
# # Export to Excel
# # -------------------------
# output_file = 'expenses_report.xlsx'
# df.reset_index().to_excel(output_file, index=False)
# print(f"\n📁 Expense data exported to: {os.path.abspath(output_file)}")

# # Close DB connection
# conn.close()
