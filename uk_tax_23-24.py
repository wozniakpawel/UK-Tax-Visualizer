#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt

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

def calculate_taxes(incomes, include_student_loan=False):
    personal_allowance_tapered = adjusted_personal_allowance(incomes)

    taxable_income = np.maximum(incomes - personal_allowance_tapered, 0)
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

    tax_20, tax_40, tax_45, national_insurances, combined_taxes, take_home_amounts, student_loan_repayments = calculate_taxes(incomes, include_student_loan)

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

def plot_graphs():
    fig, (ax1, ax2) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle("Income Tax, National Insurance, and actual take-home pay (with and without Student Loan)")

    plot_data(ax1[0], ax2[0], include_student_loan=False)
    plot_data(ax1[1], ax2[1], include_student_loan=True)

    plt.show()

def print_tax_breakdown(gross_income):
    for include_student_loan in [True, False]:
        print(f"\nWith{'out' * (not include_student_loan)} student loan:")

        personal_allowance_tapered = adjusted_personal_allowance(np.array([gross_income]))
        taxable_income = np.maximum(gross_income - personal_allowance_tapered, 0)

        tax_20, tax_40, tax_45, national_insurances, combined_taxes, take_home_amounts, student_loan_repayments = calculate_taxes(
            np.array([gross_income]), include_student_loan
        )

        print(f"Gross Income: £{gross_income:.2f}")
        print(f"Adjusted Personal Allowance: £{personal_allowance_tapered[0]:.2f}")
        print(f"Taxable Income: £{taxable_income[0]:.2f}")
        print(f"Income Tax: £{sum([tax_20[0], tax_40[0], tax_45[0]])}")
        print(f"  20% Rate: £{tax_20[0]:.2f}")
        print(f"  40% Rate: £{tax_40[0]:.2f}")
        print(f"  45% Rate: £{tax_45[0]:.2f}")
        print(f"National Insurance: £{national_insurances[0]:.2f}")

        if include_student_loan:
            print(f"Student Loan Repayment Plan 2: £{student_loan_repayments[0]:.2f}")

        print(f"Combined Taxes: £{combined_taxes[0]:.2f}")
        print(f"Take-home Amount: £{take_home_amounts[0]:.2f}")

# Plot graphs for an income range
plot_graphs()
# Calculate tax for a specific income
# print_tax_breakdown(50000)
