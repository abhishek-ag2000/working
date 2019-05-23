from locust import HttpLocust, TaskSet
from locust.events import request_failure

def login(l):
    l.client.post("accounts/login/", {"username":"niladry", "password":"qwerty123456789"})

def logout(l):
    l.client.post("accounts/logout/", {"username":"niladry", "password":"qwerty123456789"})

def index(l):
    l.client.get("")


def company_create(l):
    l.client.post("company/create/", {"User":"niladry", "Name":"BBC PVT LTD", "bussiness_nature": "Retail", "maintain": "Accounts with Inventory", "Type_of_company": "Individual", "State": "West Bengal"})

def group_create(l):
    l.client.post("accounting_double_entry/company/74/date/39/groupcreate/", {"User":"niladry", "Company":"BBC PVT LTD", "group_Name": "Hardware Debtors", "Master": "Sundry Debtors", "Nature_of_group1": "Assets", "balance_nature": "Debit"})


def ledger_create(l):
    l.client.post("accounting_double_entry/company/74/date/39/ledgercreate/", {"User":"niladry", "Company":"BBC PVT LTD", "name": "Salary A/c", "group1_Name": "Indirect Expense"})

def journal_create(l):
    l.client.post("accounting_double_entry/company/74/date/39/journal/create/", {"User":"niladry", "Company":"BBC PVT LTD", "By": "Salary A/c", "To": "Cash", "Debit": 5000, "Credit": 5000})

def Payment_create(l):
    l.client.post("accounting_double_entry/company/74/date/39/payment/create/", {"User":"niladry", "Company":"BBC PVT LTD", "account": "Salary A/c", "payments.particular": "Cash", "payments.amount": 5000})

def Receipt_create(l):
    l.client.post("accounting_double_entry/company/74/date/39/receipt/create/", {"User":"niladry", "Company":"BBC PVT LTD", "account": "Salary A/c", "receipts.particular": "Cash", "receipts.amount": 5000})

def Contra_create(l):
    l.client.post("accounting_double_entry/company/74/date/39/contra/create/", {"User":"niladry", "Company":"BBC PVT LTD", "account": "Salary A/c", "contras.particular": "Cash", "contras.amount": 5000})


class UserBehavior(TaskSet):
    tasks = {index: 1, company_create: 2, group_create: 2, ledger_create: 2, journal_create: 2, Payment_create: 2, Receipt_create: 2, Contra_create: 2}

    def on_start(self):
        login(self)

    def on_stop(self):
        logout(self)

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000

