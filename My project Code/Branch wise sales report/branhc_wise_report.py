import frappe
from frappe import _
from frappe.query_builder.functions import Sum


def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data

def get_data(filters):
	si = frappe.qb.DocType("Sales Invoice")
	
	query = (
		frappe.qb.from_(si)
		.select(
			si.cost_center,
			Sum(si.net_total).as_("net_total"),
			Sum(si.total_taxes_and_charges).as_("total_taxes_and_charges"),
			Sum(si.grand_total).as_("grand_total"),
			Sum(si.loyalty_amount).as_("loyalty_amount")
		)
		.groupby(si.cost_center)
		.where(si.cost_center != "")
		.where(si.docstatus==1)
	)
	if filters.get("from_date"):
		query = query.where(si.posting_date >= filters.get("from_date"))
	if filters.get("to_date"):
		query = query.where(si.posting_date <= filters.get("to_date"))
	if filters.get("cost_center"):
		query = query.where(si.cost_center == filters.get("cost_center"))

	data = query.run(as_dict =True)
	li_of_mode = frappe.get_all("Mode of Payment", pluck="name")
	mode_cash = []
	for j in li_of_mode:
		if "Cash" in j:
			mode_cash.append(j)
	for i in data:
		li_of_sl = frappe.get_all("Sales Invoice",
			{
				"cost_center": i.get("cost_center"), 
                "docstatus": 1,
                "posting_date": ["between",  (filters.get("from_date"), filters.get("to_date"))]
	        }, pluck="name")
		total_cash = frappe.get_all("Sales Invoice Payment", {"parent": ["in", li_of_sl], "mode_of_payment": ["in", mode_cash]}, ['sum(amount) as total_cash'])
		i["cash_amnt"] = total_cash[0]["total_cash"]
		total_credit = frappe.get_all("Sales Invoice Payment", {"parent": ["in", li_of_sl], "mode_of_payment": "Credit Card"}, ['sum(amount) as total_credit'])
		i["credit_amnt"] = total_credit[0]["total_credit"]
		
	return data