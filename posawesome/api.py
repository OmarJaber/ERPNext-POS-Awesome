import frappe

@frappe.whitelist()
def get_additional_item_descriptions(item_code: str):
    additional_item_descriptions = frappe.get_all(
        "POS Additional Item Description Table",
        fields=["description"],
        filters={"parent": item_code}    
    )

    return additional_item_descriptions

@frappe.whitelist()
def get_restaurant_tables():
    tables =  frappe.get_all(
        "POS Restaurant Table",
        order_by="table_number desc"
    )

    return tables


@frappe.whitelist()
def get_companies_pos_offers_names(offer_name: str, exclude_company: str):
    try:
        new_pos_offer_names = []

        companies = frappe.get_all(
            "Company",
            fields = ["name", "abbr"],
            filters={
                "name": ["!=", exclude_company]
            }
        )
        
        for company in companies:
            new_pos_offer_names.append(
                {
                    "company": company["name"],
                    "suggested_offer_name": f"""{company["abbr"]}-{offer_name}"""
                }
            )

        return new_pos_offer_names
    except:
        tb = frappe.get_traceback()
        print(frappe.get_traceback())

@frappe.whitelist()
def make_multi_company_pos_offers(current_pos_offer_name: str, for_companies):
    try:
        for_companies = frappe.parse_json(for_companies)
        created_offers = []
        current_offer = None

        for companyies_table in for_companies:
            pos_offer = frappe.get_doc(
                "POS Offer",
                current_pos_offer_name
            )


            # if pos_offer.name == current_pos_offer_name:
            #     frappe.throw(frappe._(f"POS Offer: ({pos_offer_new_name}) already exist for Company: ({pos_offer.company})"), "POS Offers Multi Company Creator")
            pos_offer.is_created_from_pos_offer = 1
            pos_offer.company = companyies_table["company"]
            if frappe.db.exists("POS Offer", companyies_table["suggested_offer_name"]):
                frappe.db.rollback()
                return { "status": "fail", "data": f"POS Offer ({companyies_table['suggested_offer_name']}) Already exist"}

            pos_offer.insert(set_name=companyies_table["suggested_offer_name"])
            # pos_offer.save()
            created_offers.append(companyies_table["suggested_offer_name"])

        frappe.db.commit()
        return { "status": "success", "data": f"Successfully Created {len(created_offers)} POS Offers"}

    except:
        print(frappe.get_traceback())
        
