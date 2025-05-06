import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="Personal Finance Planner",
    page_icon="💰",
    layout="wide"
)

# Main title
st.title("💰 Personal Finance Planner")

# Create tabs for different features
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Budget Tracker", 
    "🎯 Savings Goal", 
    "🏦 EMI Calculator", 
    "📈 Investment Simulator"
])

# We'll fill each tab in the following sections
with tab1:
    st.header("📊 Monthly Budget Tracker")
    
    # Input for monthly income
    income = st.number_input("Monthly Income ($)", min_value=0.0, value=3000.0, step=100.0)
    
    # Expense categories with default values
    expense_categories = {
        "Housing (Rent/Mortgage)": 0.0,
        "Utilities": 0.0,
        "Food/Groceries": 0.0,
        "Transportation": 0.0,
        "Entertainment": 0.0,
        "Healthcare": 0.0,
        "Debt Payments": 0.0,
        "Savings": 0.0,
        "Other": 0.0
    }
    
    # Create input fields for each category
    st.subheader("Monthly Expenses")
    expenses = {}
    for category, default_val in expense_categories.items():
        expenses[category] = st.number_input(
            f"{category} ($)",
            min_value=0.0,
            value=default_val,
            step=10.0,
            key=f"exp_{category}"
        )
    
    # Calculate totals
    total_expenses = sum(expenses.values())
    balance = income - total_expenses
    
    # Display summary
    st.subheader("Monthly Summary")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"${income:,.2f}")
    col2.metric("Total Expenses", f"${total_expenses:,.2f}", delta=f"-${total_expenses:,.2f}")
    col3.metric("Remaining Balance", f"${balance:,.2f}", 
                delta_color="inverse" if balance < 0 else "normal")
    
    # Visualization
    st.subheader("Expense Distribution")
    
    # Filter out categories with $0 spending
    filtered_expenses = {k: v for k, v in expenses.items() if v > 0}
    
    if filtered_expenses:
        # Pie chart
        fig1, ax1 = plt.subplots()
        ax1.pie(
            filtered_expenses.values(),
            labels=filtered_expenses.keys(),
            autopct='%1.1f%%',
            startangle=90
        )
        ax1.axis('equal')  # Equal aspect ratio ensures pie is drawn as a circle
        st.pyplot(fig1)
        
        # Bar chart
        fig2, ax2 = plt.subplots()
        ax2.bar(filtered_expenses.keys(), filtered_expenses.values())
        plt.xticks(rotation=45, ha='right')
        ax2.set_ylabel('Amount ($)')
        st.pyplot(fig2)
    else:
        st.warning("No expenses entered yet!")

with tab2:
    st.header("🎯 Savings Goal Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        goal_amount = st.number_input("Goal Amount ($)", min_value=1.0, value=10000.0, step=100.0)
        monthly_savings = st.number_input("Monthly Savings ($)", min_value=1.0, value=500.0, step=10.0)
        current_savings = st.number_input("Current Savings ($)", min_value=0.0, value=0.0, step=100.0)
    
    with col2:
        interest_rate = st.slider("Annual Interest Rate (%)", min_value=0.0, max_value=20.0, value=3.5, step=0.1)
        inflation_rate = st.slider("Annual Inflation Rate (%)", min_value=0.0, max_value=10.0, value=2.0, step=0.1)
    
    # Calculate time to reach goal
    if st.button("Calculate Time to Reach Goal"):
        if monthly_savings <= 0:
            st.error("Monthly savings must be greater than 0!")
        else:
            remaining = goal_amount - current_savings
            if remaining <= 0:
                st.success("🎉 You've already reached your savings goal!")
            else:
                # Adjust for inflation (real interest rate)
                real_interest_rate = (1 + interest_rate/100) / (1 + inflation_rate/100) - 1
                monthly_rate = real_interest_rate / 12
                
                # Calculate months needed
                if monthly_rate == 0:
                    months = remaining / monthly_savings
                else:
                    months = np.log(1 + (monthly_rate * remaining) / monthly_savings) / np.log(1 + monthly_rate)
                
                months = max(1, int(np.ceil(months)))
                years = months // 12
                remaining_months = months % 12
                
                # Project savings growth
                dates = []
                amounts = []
                current_date = datetime.now()
                current_amount = current_savings
                
                for month in range(0, months + 1):
                    dates.append(current_date)
                    amounts.append(current_amount)
                    current_date += timedelta(days=30)  # Approximation
                    current_amount = current_amount * (1 + monthly_rate) + monthly_savings
                
                # Create dataframe for visualization
                df = pd.DataFrame({
                    "Date": dates,
                    "Amount": amounts
                })
                
                # Display results
                st.success(
                    f"**Time to reach goal:** {years} years and {remaining_months} months "
                    f"(≈ {months} months total)"
                )
                
                # Visualization
                st.subheader("Savings Projection")
                fig, ax = plt.subplots()
                ax.plot(df["Date"], df["Amount"])
                ax.set_xlabel("Time")
                ax.set_ylabel("Amount ($)")
                ax.set_title("Projected Savings Growth")
                ax.grid(True)
                st.pyplot(fig)
                
                # Show projected final amount
                final_amount = amounts[-1]
                st.info(
                    f"At this rate, you'll have approximately **${final_amount:,.2f}** "
                    f"(in today's dollars) after {months} months."
                )

with tab3:
    st.header("🏦 EMI Calculator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        principal = st.number_input("Loan Amount ($)", min_value=1.0, value=20000.0, step=100.0)
        tenure_years = st.slider("Loan Tenure (Years)", min_value=1, max_value=30, value=5)
    
    with col2:
        interest_rate = st.slider("Annual Interest Rate (%)", min_value=0.1, max_value=20.0, value=7.5, step=0.1)
        tenure_months = st.slider("Loan Tenure (Months)", min_value=0, max_value=11, value=0)
    
    # Calculate EMI
    total_tenure_months = tenure_years * 12 + tenure_months
    monthly_rate = interest_rate / 12 / 100
    
    if monthly_rate == 0:  # Handle 0% interest case
        emi = principal / total_tenure_months
    else:
        emi = principal * monthly_rate * (1 + monthly_rate)**total_tenure_months / ((1 + monthly_rate)**total_tenure_months - 1)
    
    total_payment = emi * total_tenure_months
    total_interest = total_payment - principal
    
    # Display results
    st.subheader("EMI Calculation Results")
    col1, col2, col3 = st.columns(3)
    col1.metric("Monthly Payment (EMI)", f"${emi:,.2f}")
    col2.metric("Total Interest", f"${total_interest:,.2f}")
    col3.metric("Total Payment", f"${total_payment:,.2f}")
    
    # Amortization schedule visualization
    if st.checkbox("Show Amortization Schedule"):
        months = []
        principals = []
        interests = []
        balances = []
        
        current_balance = principal
        
        for month in range(1, total_tenure_months + 1):
            interest_payment = current_balance * monthly_rate
            principal_payment = emi - interest_payment
            current_balance -= principal_payment
            
            months.append(month)
            principals.append(principal_payment)
            interests.append(interest_payment)
            balances.append(current_balance if current_balance > 0 else 0)
        
        # Create dataframe
        amort_df = pd.DataFrame({
            "Month": months,
            "Principal": principals,
            "Interest": interests,
            "Remaining Balance": balances
        })
        
        # Display table
        st.dataframe(amort_df.style.format({
            "Principal": "${:,.2f}",
            "Interest": "${:,.2f}",
            "Remaining Balance": "${:,.2f}"
        }))
        
        # Visualization
        st.subheader("Payment Breakdown Over Time")
        fig, ax = plt.subplots()
        ax.stackplot(
            months,
            principals,
            interests,
            labels=['Principal', 'Interest']
        )
        ax.legend(loc='upper right')
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount ($)")
        ax.set_title("EMI Composition Over Time")
        st.pyplot(fig)

with tab4:
    st.header("📈 Investment Growth Simulator")
    
    col1, col2 = st.columns(2)
    
    with col1:
        initial_investment = st.number_input("Initial Investment ($)", min_value=0.0, value=1000.0, step=100.0)
        monthly_contribution = st.number_input("Monthly Contribution ($)", min_value=0.0, value=100.0, step=10.0)
        years = st.slider("Investment Period (Years)", min_value=1, max_value=50, value=10)
    
    with col2:
        annual_return = st.slider("Expected Annual Return (%)", min_value=0.1, max_value=20.0, value=7.0, step=0.1)
        annual_inflation = st.slider("Expected Annual Inflation (%)", min_value=0.0, max_value=10.0, value=2.5, step=0.1)
    
    # Calculate investment growth
    if st.button("Simulate Investment Growth"):
        months = years * 12
        monthly_return = (1 + annual_return/100)**(1/12) - 1
        monthly_inflation = (1 + annual_inflation/100)**(1/12) - 1
        
        # Calculate real return (adjusted for inflation)
        real_monthly_return = (1 + monthly_return) / (1 + monthly_inflation) - 1
        
        # Simulate growth
        dates = []
        nominal_values = []
        real_values = []
        contributions = []
        
        current_date = datetime.now()
        nominal_value = initial_investment
        real_value = initial_investment
        total_contributions = initial_investment
        
        for month in range(months + 1):
            dates.append(current_date)
            nominal_values.append(nominal_value)
            real_values.append(real_value)
            contributions.append(total_contributions)
            
            if month < months:
                current_date += timedelta(days=30)  # Approximation
                nominal_value = nominal_value * (1 + monthly_return) + monthly_contribution
                real_value = real_value * (1 + real_monthly_return) + monthly_contribution
                total_contributions += monthly_contribution
        
        # Create dataframe
        investment_df = pd.DataFrame({
            "Date": dates,
            "Nominal Value": nominal_values,
            "Inflation-Adjusted Value": real_values,
            "Total Contributions": contributions
        })
        
        # Display summary
        final_nominal = nominal_values[-1]
        final_real = real_values[-1]
        total_contributed = contributions[-1]
        growth_nominal = final_nominal - total_contributed
        growth_real = final_real - total_contributed
        
        st.success(
            f"After {years} years, your investment could grow to:\n\n"
            f"- **Nominal Value:** ${final_nominal:,.2f}\n"
            f"- **Inflation-Adjusted Value:** ${final_real:,.2f}\n\n"
            f"Total contributions: ${total_contributed:,.2f}\n"
            f"Nominal growth: ${growth_nominal:,.2f}\n"
            f"Real growth (after inflation): ${growth_real:,.2f}"
        )
        
        # Visualization
        st.subheader("Investment Growth Over Time")
        fig, ax = plt.subplots()
        ax.plot(investment_df["Date"], investment_df["Nominal Value"], label="Nominal Value")
        ax.plot(investment_df["Date"], investment_df["Inflation-Adjusted Value"], label="Inflation-Adjusted Value")
        ax.plot(investment_df["Date"], investment_df["Total Contributions"], label="Total Contributions", linestyle="--")
        ax.legend()
        ax.set_xlabel("Time")
        ax.set_ylabel("Value ($)")
        ax.set_title("Investment Growth Projection")
        ax.grid(True)
        st.pyplot(fig)

# Add this at the end of the file (outside all tabs)

# Generate PDF report
if st.button("📄 Generate PDF Report"):
    # Create a simple text report (in a real app, you'd use pdfkit or similar)
    report_content = f"""
    Personal Finance Planner Report
    Generated on {datetime.now().strftime('%Y-%m-%d')}
    
    ===== Budget Summary =====
    Income: ${income:,.2f}
    Expenses: ${total_expenses:,.2f}
    Balance: ${balance:,.2f}
    
    ===== Savings Goals =====
    Goal Amount: ${goal_amount:,.2f}
    Monthly Savings: ${monthly_savings:,.2f}
    
    ===== Loan Information =====
    Loan Amount: ${principal:,.2f}
    EMI: ${emi:,.2f}
    Total Interest: ${total_interest:,.2f}
    
    ===== Investment Projection =====
    Initial Investment: ${initial_investment:,.2f}
    Projected Value (after {years} years): ${final_nominal:,.2f}
    """
    
    # Create download button
    st.download_button(
        label="⬇️ Download Report",
        data=report_content,
        file_name="financial_report.txt",
        mime="text/plain"
    )