# encoding=utf8
# -*- coding: utf-8 -*- u
from __future__ import unicode_literals
from __future__ import division
import frappe
import frappe, os , math
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_site_base_path, cint, cstr, date_diff, flt, formatdate, getdate, get_link_to_form, \
    comma_or, get_fullname, add_years, add_months, add_days, nowdate
from frappe.utils.data import flt, nowdate, getdate, cint, rounded, add_months, add_days, get_last_day
from frappe.utils.password import update_password as _update_password
from frappe.utils import cint, cstr, flt, nowdate, comma_and, date_diff, getdate, formatdate ,get_url
import datetime
from datetime import date
from frappe.model.mapper import get_mapped_doc
import sys
from frappe.utils import cstr
from frappe.model.document import Document
import json


@frappe.whitelist()
def update_related_customer_percentages(parent_customer):
    # Get the current customer's percent table
    current_customer = frappe.get_doc("Customer", parent_customer)

    if len(current_customer.custom_percent_table) < 1:
        frappe.throw("No Record Found in Percent Table")

    percent_table_data = current_customer.custom_percent_table

    # Find all related customers
    related_customers = frappe.get_all(
        "Related Customer",
        filters={"parent_customer": parent_customer},
        fields=["name"]
    )

    # Initialize a dictionary to count updated related customers by item group
    update_counts = {row.item_group: 0 for row in percent_table_data}

    # Loop through each related customer
    for related_customer in related_customers:
        # Get related customer document
        related_customer_doc = frappe.get_doc("Related Customer", related_customer.name)

        # Track if any changes were made for each item group
        changes_made = False

        # Update the percent_table for matching item groups
        for row in percent_table_data:
            # Check if the item group exists in the related customer's percent_table
            existing_row = next((item for item in related_customer_doc.percent_table if item.item_group == row.item_group), None)

            if existing_row:
                # Update the existing percentages for the item group
                if (existing_row.employee_percentage != row.employee_percentage or 
                    existing_row.company_percentage != row.company_percentage):
                    existing_row.employee_percentage = row.employee_percentage
                    existing_row.company_percentage = row.company_percentage
                    changes_made = True  # Mark that changes were made
                    update_counts[row.item_group] += 1  # Increment count for this item group

        # Save changes to the related customer only if there were updates
        if changes_made:
            related_customer_doc.save()

    return update_counts  # Return the counts of updated related customers by item group



@frappe.whitelist()
def get_employee_percentage(invoice_name):
    invoice_doc = frappe.get_doc("Sales Invoice", invoice_name)

    total_cash = 0

    for item in invoice_doc.items:
        amount = item.rate * item.qty

        employee_percentage = frappe.get_value(
            "Percent Table", 
            filters={
                "parenttype": 'Related Customer', 
                "parent": invoice_doc.custom_related_customer, 
                "item_group": item.item_group
            }, 
            fieldname="employee_percentage"
        ) or 100

        total_cash += amount * (employee_percentage / 100)
    
    return total_cash




@frappe.whitelist()
def get_item_percentage_and_amount(customer, related_customer, item):
    item = json.loads(item)

    employee_percentage = 0
    company_percentage = 0
    employee_amount = 0
    company_amount = 0

    total_amount = item['rate'] * item['qty']

    employee_percentage, company_percentage = frappe.get_value(
        "Percent Table", 
        filters={
            "parenttype": 'Related Customer', 
            "parent": related_customer, 
            "item_group": item['item_group']
        }, 
        fieldname=["employee_percentage", "company_percentage"]
    ) or (100, 0)


    employee_amount = total_amount * (employee_percentage / 100)
    company_amount = total_amount * (company_percentage / 100)
    
    return employee_percentage, company_percentage, employee_amount, company_amount








