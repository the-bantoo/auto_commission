import frappe
from frappe import _

def make_journal_entry(inv, method):
    create_journal_entry(inv)

def verify_partner(inv, method):
    # verify partner exists as a customer
    ph_settings = get_packhouse_settings()
    if inv.sales_partner and ph_settings.comm_journals == 1:
        if not frappe.db.exists("Customer", inv.sales_partner):
            frappe.throw(_("Please ensure that the sales partner's name, {0}, matches an existing customer to be credited.").format(frappe.bold(inv.sales_partner)))
        
        if not ph_settings.commission_account or ph_settings.commission_account == '' or not ph_settings.commission_cost_center or ph_settings.commission_cost_center == '':
            frappe.throw(_("Please ensure Commission Account and Cost Center are set in {0}").format(frappe.bold("Packhouse Settings")))
        
        if ph_settings.jv_warning == 1 and (inv.sales_partner not in get_partners()):
            frappe.msgprint(_("Add {0} to {1} in Packhouse Settings to automatically create a Journal Entry for their commission".format(frappe.bold(inv.sales_partner), frappe.bold("Active Partners"))))


def get_partners():
    ph_settings = get_packhouse_settings()
    partners = []
    for p in ph_settings.active_partners:
        partners.append(p.partner)

    return partners

def create_journal_entry(inv):
    
    ph_settings = get_packhouse_settings()
    if not ph_settings.comm_journals == 1: return

    note = '''Sales Partner Commission with {0} \nSales Invoice - {5} \nSales Total - {1} {2} \nCommission {3}% - {1} {4}
            '''.format(inv.sales_partner, inv.currency, inv.amount_eligible_for_commission, inv.commission_rate, inv.total_commission, inv.name)
    
    je_dict = { 
        'doctype': 'Journal Entry',
        'title': "{1} Commission for {0}".format(inv.sales_partner, inv.name), 
        'voucher_type': 'Journal Entry', 
        'naming_series': 'ACC-JV-.YYYY.-',
        'company': ph_settings.company, 
        'posting_date': inv.posting_date,
        'user_remark': note,
        'remark': 'Note: {0}'.format(note),
        'pay_to_recd_from': inv.sales_partner,
        'letter_head': inv.letter_head,
        'is_opening': 'No',
        'docstatus': 1,
        'accounts': [
                {
                    'account': ph_settings.commission_account,
                    'cost_center': ph_settings.commission_cost_center,
                    'debit_in_account_currency': inv.total_commission, 
                    'debit': inv.total_commission,
                    'against_account': inv.sales_partner,
                }, 
                {
                    'account': '1310 - Debtors - ZA',
                    'party_type': 'Customer', 
                    'party': inv.sales_partner,
                    'cost_center': ph_settings.commission_cost_center,
                    'credit_in_account_currency': inv.total_commission,
                    'credit': inv.total_commission,
                    'is_advance': 'No',
                    'against_account': ph_settings.commission_account,
                }
            ]
    }
    je = frappe.get_doc(je_dict)
    je.insert(ignore_permissions=True)

def get_packhouse_settings():
    return frappe.get_cached_doc('Packhouse Settings', 'Packhouse Settings')