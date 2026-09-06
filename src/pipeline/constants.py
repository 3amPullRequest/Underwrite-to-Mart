# Live portal path
BASE_URL_NMVCCS = "https://crashviewer.nhtsa.dot.gov/crashviewer/LegacyNMVCCS"
SEARCH_URL_NMVCCS = f"{BASE_URL_NMVCCS}/Index"

# XML endpoint
XML_BASE_URL_NMVCCS = "https://crashviewer.nhtsa.dot.gov/crashviewer/nass-NMVCCS/CaseForm.aspx"

# By default, extract everything
SEARH_FILTERS = {
    "btnSubmit": "submit1",
    "ddlCrashCriteria": "-1", "ddlYear": "-1", "ddlMonth": "-1",
    "ddlCrashType": "-1", "ddlMinVeh": "-1", "ddlMaxVeh": "-1",
    "ddlCrashConfig": "-1", "ddlCritReason": "-1",
    "ddlStartModelYear": "-1", "ddlEndModelYear": "-1",
    "ddlPrimeDamage": "-1", "ddlMake": "-1", "ddlModel": "-1",
    "ddlBodyType": "-1",
}