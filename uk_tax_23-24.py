#!/usr/bin/env python3

import sys
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Tax year specific variables
# Personal allowance
personal_allowance = 12570
personal_allowance_taper = 100000

# Income tax
basic_rate_limit = 37700
higher_rate_limit = 125140
basic_rate = 0.20
higher_rate = 0.40
additional_rate = 0.45

# National Insurance
ni_primary_threshold = 12570
ni_upper_limit = 50270
ni_rate_1 = 0.12
ni_rate_2 = 0.02

# Student loan repayments
student_loan_plan_2_threshold = 27295
student_loan_plan_2_rate = 0.09

# Salary range
salary_top_range = 250000

def adjusted_personal_allowance(incomes):
    reduction_rate = 0.5

    personal_allowance_tapered = np.where(
        incomes > personal_allowance_taper,
        np.maximum(personal_allowance - ((incomes - personal_allowance_taper) * reduction_rate), 0),
        personal_allowance,
    )

    return personal_allowance_tapered

def income_tax(taxable_income):

    tax_20 = np.where(
        taxable_income <= basic_rate_limit,
        taxable_income * basic_rate,
        basic_rate_limit * basic_rate,
    )

    tax_40 = np.where(
        (taxable_income > basic_rate_limit) & (taxable_income <= higher_rate_limit),
        (taxable_income - basic_rate_limit) * higher_rate,
        np.where(
            taxable_income > higher_rate_limit,
            (higher_rate_limit - basic_rate_limit) * higher_rate,
            0,
        ),
    )

    tax_45 = np.where(
        taxable_income > higher_rate_limit,
        (taxable_income - higher_rate_limit) * additional_rate,
        0,
    )

    return tax_20, tax_40, tax_45

def national_insurance(incomes):
    ni = np.where(
        incomes <= ni_primary_threshold,
        0,
        np.where(
            incomes <= ni_upper_limit,
            (incomes - ni_primary_threshold) * ni_rate_1,
            (ni_upper_limit - ni_primary_threshold) * ni_rate_1 + (incomes - ni_upper_limit) * ni_rate_2,
        ),
    )

    return ni

def student_loan_repayment_plan_2(incomes):
    repayments = np.where(
        incomes > student_loan_plan_2_threshold,
        (incomes - student_loan_plan_2_threshold) * student_loan_plan_2_rate,
        0,
    )

    return repayments

def calculate_taxes(incomes, pension_contrib_percent=0, voluntary_pension_contrib=0, include_student_loan=False):
    pension_contributions = incomes * pension_contrib_percent
    incomes_after_pension = incomes - pension_contributions - voluntary_pension_contrib

    personal_allowance_tapered = adjusted_personal_allowance(incomes_after_pension)

    taxable_income = np.maximum(incomes_after_pension - personal_allowance_tapered, 0)
    tax_20, tax_40, tax_45 = income_tax(taxable_income)
    income_taxes = tax_20 + tax_40 + tax_45
    national_insurances = national_insurance(incomes)
    student_loan_repayments = np.zeros_like(incomes)

    if include_student_loan:
        student_loan_repayments = student_loan_repayment_plan_2(incomes)

    combined_taxes = income_taxes + national_insurances + student_loan_repayments
    take_home_amounts = incomes - combined_taxes

    return tax_20, tax_40, tax_45, national_insurances, combined_taxes, take_home_amounts, student_loan_repayments

def plot_data(ax1, ax2, include_student_loan=False):
    incomes = np.linspace(0, salary_top_range, 1000)

    tax_20, tax_40, tax_45, national_insurances, combined_taxes, take_home_amounts, student_loan_repayments = calculate_taxes(
        incomes, include_student_loan=include_student_loan
    )

    income_taxes = tax_20 + tax_40 + tax_45
    income_taxes_percentage = income_taxes / incomes * 100
    national_insurances_percentage = national_insurances / incomes * 100
    combined_taxes_percentage = combined_taxes / incomes * 100
    student_loan_repayments_percentage = student_loan_repayments / incomes * 100
    marginal_combined_taxes = np.gradient(combined_taxes) / np.gradient(incomes) * 100

    combined_label = "Combined Income Tax & NI"
    if include_student_loan:
        combined_label += " (incl. SL)"

    marginal_label = "Marginal " + combined_label

    # Plot the annual totals graph
    ax1.plot(incomes / 1000, income_taxes / 1000, label="Income Tax", color="C0")
    ax1.plot(incomes / 1000, national_insurances / 1000, label="National Insurance", color="C1")
    if include_student_loan:
        ax1.plot(incomes / 1000, student_loan_repayments / 1000, label="Student Loan Repayment Plan 2", color="C2")
    ax1.plot(incomes / 1000, combined_taxes / 1000, label=combined_label, color="C3")
    ax1.plot(incomes / 1000, take_home_amounts / 1000, label="Take-home Amount", color="C4")

    ax1.set_xlabel("Gross Income (£k)")
    ax1.set_ylabel("Total Amount (£k)")
    ax1.set_title("Taxes, National Insurance, and Take-home Amount")
    ax1.legend()
    ax1.grid()

    # Plot the percentage graph
    ax2.plot(incomes / 1000, income_taxes_percentage, label="Income Tax (%)", color="C0")
    ax2.plot(incomes / 1000, national_insurances_percentage, label="National Insurance (%)", color="C1")

    if include_student_loan:
        ax2.plot(incomes / 1000, student_loan_repayments_percentage, label="Student Loan Repayment Plan 2 (%)", color="C2")
    ax2.plot(incomes / 1000, combined_taxes_percentage, label=combined_label + " (%)", color="C3")
    ax2.plot(incomes / 1000, marginal_combined_taxes, label=marginal_label, linestyle='--', color="C4")

    ax2.set_xlabel("Gross Income (£k)")
    ax2.set_ylabel("Percentage of Income (%)")
    ax2.set_title("Taxes, NI, and Student Loan Repayment as Percentage of Income")
    ax2.legend()
    ax2.set_ylim(0, 100)  # Set Y-axis limits for the bottom graph
    ax2.set_yticks(np.arange(0, 101, 10))  # Set Y-axis ticks at intervals of 10
    ax2.grid()

def plot_graphs(save_plot=False):
    fig, (ax1, ax2) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Income Tax, National Insurance, and actual take-home pay (with and without Student Loan)")

    plot_data(ax1[0], ax2[0], include_student_loan=False)
    plot_data(ax1[1], ax2[1], include_student_loan=True)

    if save_plot:
        plt.savefig('tax_overview.png')
    else:
        plt.show()

def print_tax_breakdown(gross_income, pension_contrib_percent=0, voluntary_pension_contrib=0):
    for include_student_loan in [True, False]:
        print(f"\n\033[1;32mWith{'out' * (not include_student_loan)} student loan:\033[0m")

        tax_20, tax_40, tax_45, national_insurances, combined_taxes, take_home_amounts, student_loan_repayments = calculate_taxes(
            np.array([gross_income]), pension_contrib_percent, voluntary_pension_contrib, include_student_loan
        )

        print(f"\033[1;34m Gross Income:\033[0m £{gross_income:.2f}")
        print(f"\033[1;34m Pre-tax Pension Contributions:\033[0m £{gross_income * pension_contrib_percent:.2f}")
        print(f"\033[1;34m Voluntary Pension Contributions:\033[0m £{voluntary_pension_contrib:.2f}")
        print(f"\033[1;34m Adjusted Gross Income:\033[0m £{gross_income - gross_income * pension_contrib_percent - voluntary_pension_contrib:.2f}")
        print(f"\033[1;34m Personal Allowance:\033[0m £{adjusted_personal_allowance(np.array([gross_income - gross_income * pension_contrib_percent - voluntary_pension_contrib]))[0]:.2f}")
        print(f"\033[1;34m Taxable Income:\033[0m £{max(gross_income - gross_income * pension_contrib_percent - voluntary_pension_contrib - adjusted_personal_allowance(np.array([gross_income - gross_income * pension_contrib_percent - voluntary_pension_contrib]))[0], 0):.2f}")
        print(f"\033[1;34m Income Tax:\033[0m £{sum([tax_20[0], tax_40[0], tax_45[0]])}")
        print(f"  \033[1;34m 20% Rate:\033[0m £{tax_20[0]:.2f}")
        print(f"  \033[1;34m 40% Rate:\033[0m £{tax_40[0]:.2f}")
        print(f"  \033[1;34m 45% Rate:\033[0m £{tax_45[0]:.2f}")
        print(f"\033[1;34m National Insurance:\033[0m £{national_insurances[0]:.2f}")

        if include_student_loan:
            print(f"\033[1;34m Student Loan Repayment Plan 2:\033[0m £{student_loan_repayments[0]:.2f}")

        print(f"\033[1;34m Combined Taxes:\033[0m £{combined_taxes[0]:.2f}")
        print(f"\033[1;34m Take-home Amount:\033[0m £{take_home_amounts[0]:.2f}")

def calculate_tax_savings(incomes, pension_contrib_percent, voluntary_pension_contrib):
    taxes_no_contributions = calculate_taxes(incomes, pension_contrib_percent=0, voluntary_pension_contrib=0)
    taxes_with_contributions = calculate_taxes(incomes, pension_contrib_percent, voluntary_pension_contrib)
    combined_taxes_no_contributions = taxes_no_contributions[4]
    combined_taxes_with_contributions = taxes_with_contributions[4]
    tax_savings = combined_taxes_no_contributions - combined_taxes_with_contributions
    return tax_savings

def plot_tax_savings_vs_pension_contributions(income, max_voluntary_contrib=0.5, save_plot=False):
    fig, ax = plt.subplots(figsize=(8, 6))
    fig.suptitle(f"Tax savings analysis for a gross income of £{income}")

    voluntary_contributions = np.linspace(0, income * max_voluntary_contrib, 1000)
    tax_savings = calculate_tax_savings(np.array([income]), 0, voluntary_contributions)
    tax_savings_percentage = tax_savings / voluntary_contributions * 100

    _, _, _, _, combined_taxes, _, _ = calculate_taxes(np.array([income]), voluntary_pension_contrib=voluntary_contributions)
    effective_tax_rate = combined_taxes / income * 100

    ax.plot(voluntary_contributions, tax_savings_percentage, label="Tax Savings as a Percentage of Contribution", color="C0")
    ax.plot(voluntary_contributions, effective_tax_rate, label="Effective Tax Rate", color="C1")

    ax.set_xlabel("Voluntary Pension Contributions (£)")
    ax.set_ylabel("Percentage (%)")
    ax.set_title("Tax Savings Percentage and Effective Tax Rate vs. Voluntary Pension Contributions")
    ax.legend()
    ax.grid()

    if save_plot:
        plt.savefig('tax_savings_single.png')
    else:
        plt.show()

def plot_tax_savings_3d(salary_top_range=salary_top_range, max_voluntary_contrib_percentage=0.5, save_plot=False):
    fig = plt.figure(figsize=(18, 8))
    ax1 = fig.add_subplot(121, projection='3d')
    ax2 = fig.add_subplot(122, projection='3d')

    incomes = np.arange(0, salary_top_range + 1000, 1000)
    X, Y = np.meshgrid(incomes, np.linspace(0, max(incomes) * max_voluntary_contrib_percentage, len(incomes)))
    Z1 = np.empty(X.shape)
    Z2 = np.empty(X.shape)

    for i, income in enumerate(incomes):
        tax_savings = calculate_tax_savings(np.array([income]), 0, Y[:, i])
        tax_savings_percentage = tax_savings / Y[:, i] * 100
        _, _, _, _, combined_taxes, _, _ = calculate_taxes(np.array([income]), voluntary_pension_contrib=Y[:, i])
        effective_tax_rate = combined_taxes / income * 100

        Z1[:, i] = tax_savings_percentage
        Z2[:, i] = effective_tax_rate

    ax1.plot_surface(X / 1000, Y / 1000, Z1, cmap='viridis')
    ax1.set_xlabel('Income (£k)')
    ax1.set_ylabel('Voluntary Pension Contributions (£k)')
    ax1.set_zlabel('Tax Savings as a Percentage of Contribution (%)')
    ax1.set_title('Tax Savings Percentage vs. Income and Voluntary Pension Contributions')

    ax2.plot_surface(X / 1000, Y / 1000, Z2, cmap='viridis')
    ax2.set_xlabel('Income (£k)')
    ax2.set_ylabel('Voluntary Pension Contributions (£k)')
    ax2.set_zlabel('Effective Tax Rate (%)')
    ax2.set_title('Effective Tax Rate vs. Income and Voluntary Pension Contributions')

    if save_plot:
        plt.savefig('tax_savings_overview.png')
    else:
        plt.show()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        try:
            gross_income = float(sys.argv[1])
            if gross_income >= 0:
                # Provide a breakdown for some specific gross income
                print_tax_breakdown(gross_income)
                plot_tax_savings_vs_pension_contributions(gross_income)
            else:
                raise ValueError("Gross income must be a non-negative number.")
        except ValueError as e:
            print(f"Invalid argument. Expected a number, got {sys.argv[1]}")
            print(str(e))
    else:
        # Plot graphs for an income range
        plot_graphs()
        plot_tax_savings_3d()