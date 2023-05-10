# Copyright (c) 2021, Wahni IT Solutions and contributors
# For license information, please see license.txt

import frappe
from frappe.model.mapper import get_mapped_doc

@frappe.whitelist()
def make_employee(source_name, target_doc=None):
	def set_missing_values(source, target):
		target.personal_email, target.first_name = frappe.db.get_value(
			"Job Applicant", source.job_applicant, ["email_id", "applicant_name",]
		)
	doc = get_mapped_doc(
		"Job Offer",
		source_name,
		{
			"Job Offer": {
				"doctype": "Employee",
				"field_map": {"applicant_name": "employee_name", "offer_date": "scheduled_confirmation_date"},
			}
		},
		target_doc,
		set_missing_values,
	)
	
	if doc.personal_email:
		more_details = frappe.db.get_value('Job Applicant',doc.personal_email,
				     ['source','applicant_address','age','dob','phone_number','gender','blood_group','marital_status','date_of_marriage','nearest_place',
	  				  'emergency_contact_name','emergency_phone','relation','identity_card_type','id_no','id_date','health_details','yes_or_no','yes_details'], as_dict=1)
		doc.source = more_details.source
		doc.current_address = more_details.applicant_address
		doc.age = more_details.age
		doc.date_of_birth = more_details.dob
		doc.gender = more_details.gender
		doc.cell_number = more_details.phone_number
		doc.blood_group = more_details.blood_group
		doc.marital_status = more_details.marital_status
		doc.date_of_marriage = more_details.date_of_marriage
		doc.nearest_place = more_details.nearest_place
		doc.person_to_be_contacted = more_details.emergency_contact_name
		doc.emergency_phone_number =more_details.emergency_phone
		doc.relation = more_details.relation
		doc.identity_card_type = more_details.identity_card_type
		doc.id_no = more_details.id_no
		doc.id_date = more_details.id_date
		doc.health_details = more_details.health_details
		doc.yes_or_no = more_details.yes_or_no
		doc.yes_details = more_details.yes_details
		
		fam_details = frappe.get_all('Job Applicant Family Details', filters={"parent":doc.personal_email},  fields=['person_name', 'relation', "age", "occupation"])
		for i in fam_details:
			row = doc.append("job_applicant_family_details", {})
			row.person_name = i.person_name
			row.relation = i.relation
			row.age = i.age
			row.occupation = i.occupation

		education_details = frappe.get_all('Job Applicant Education', filters={"parent":doc.personal_email},  fields=['education_level', 'name_of_the_course', "university", "year_of_passing"])
		for i in education_details:
			row = doc.append("education", {})
			row.education_level = i.education_level
			row.qualification = i.name_of_the_course
			row.school_univ = i.university
			row.year_of_passing = i.year_of_passing

		career_details = frappe.get_all('Job Applicant Career History', filters={"parent":doc.personal_email},  fields=['company_name', 'designation', "salary", "yrs_of_service"])
		for i in career_details:
			row = doc.append("external_work_history", {})
			row.company_name = i.company_name
			row.designation = i.designation
			row.salary = i.salary
			row.total_experience = i.yrs_of_service
		
		references_details = frappe.get_all('Employment References', filters={"parent":doc.personal_email},  fields=['person_name', 'company_name', "desigantion", "tel_no","email_id"])
		for i in references_details:
			row = doc.append("employment_references", {})
			row.person_name = i.person_name
			row.company_name = i.company_name
			row.desigantion = i.desigantion
			row.tel_no = i.tel_no
			row.email_id = i.email_id
	return doc