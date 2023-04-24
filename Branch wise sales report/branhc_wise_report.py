def execute(filters=None):
	columns = get_columns(filters)
	data = get_data(filters)
	return columns, data, None

def get_data(filters):
	si = frappe.qb.DocType("Sales Invoice")
------------------------------------------------------------	

	query = (
		frappe.qb.from_(si)
		.select(
			si.posting_date,
			si.cost_center,
			Sum(si.total).as_("total"),
			Sum(si.total_taxes_and_charges).as_("total_taxes_and_charges"),
			Sum(si.grand_total).as_("grand_total"),
			Sum(si.loyalty_points).as_("loyalty_points")
		)
		.groupby("cost_center")
		.where(si.cost_center != "")
		.where(si.status.isin(["Paid","Partly Paid"]))
	)
-------------------------------------------------------------

	if filters.get("from_date"):
		query = query.where(si.posting_date >= filters.get("from_date"))
	if filters.get("to_date"):
		query = query.where(si.posting_date <= filters.get("to_date"))
	if filters.get("cost_center"):
		query = query.where(si.cost_center == filters.get("cost_center"))

	data = query.run(as_dict =True)
	
-----------------------------------------------------------------

	li_of_mode = frappe.get_all("Mode of Payment",pluck="name")
	li_mode_of_pay = []
	for j in li_of_mode:
		if "Cash" in j:
			li_mode_of_pay.append(j)

	for i in data:
		li_of_sl = frappe.get_all("Sales Invoice", {"cost_center": i.cost_center, "status": ["in", ["Paid","Partly Paid"]]}, pluck="name")
		total_credit = frappe.get_all("Sales Invoice Payment", {"parent": ["in", li_of_sl], "mode_of_payment": ["in", li_mode_of_pay]}, ['sum(amount) as total_credit'])
		i["cash_amnt"] = total_credit[0]["total_credit"]
		total_credit = frappe.get_all("Sales Invoice Payment", {"parent": ["in", li_of_sl], "mode_of_payment": "Credit Card"}, ['sum(amount) as total_credit'])
		i["credit_amnt"] = total_credit[0]["total_credit"]
		

	return data