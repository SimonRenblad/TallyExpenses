import requests
import json
from fractions import Fraction
from decimal import Decimal
import decimal

URL = ''

test_input = {

    "name": "Jan Expense Report",
    "persons": ["Alice", "Bob", "Claire", "David"],
    "expenses": [
        {
            "category": "Breakfast",
            "amount": 60,
            "paidBy": "Bob",
            "exclude": ["Claire","David"]
        },
        {
            "category": "Phone Bill",
            "amount": 100,
            "paidBy": "Claire"
        },
        {
            "category": "Groceries",
            "amount": 80,
            "paidBy": "David"
        },
        {
            "category": "Petrol",
            "amount": 40,
            "paidBy": "David"
        }
    ]
}

def get_api_input():
    return requests.request('POST', URL).json()

#takes in a recorded expense and returns a **list of transactions
def handleExpense(persons, expense):

    transactions = []

    amount = expense["amount"]

    paidBy = expense["paidBy"]

    #handle exclusions
    if "exclude" in expense:
        exclusions = expense["exclude"]
    else:
        exclusions = []

    numPayees = len(persons) - len(exclusions) - 1
    if isinstance(amount, int):
        payeeAmount = Fraction(amount, numPayees)
    elif isinstance(amount, float):
        payeeAmount = Fraction(Decimal(amount))
    else:
        print("error, undefined type")

    for p in persons:
        if p == paidBy or p in exclusions:
            continue
        else:
            t = {"from": p, "to": paidBy, "amount": payeeAmount}
            transactions.append(t)

    return transactions

def mergeTransactions(transactions):

    # check for identical items
    for i in range(len(transactions)):
        for j in range(i+1, len(transactions)):
            if transactions[i]["from"] == transactions[j]["from"] and \
                transactions[i]["to"] == transactions[j]["to"] and \
                transactions[i]["from"] is not None:
                    transactions[i]["amount"] += transactions[j]["amount"]
                    transactions[j]["from"] = None

    #delete merged items
    for t in transactions:
        if t["from"] is None:
            transactions.remove(t)

    return transactions

def eliminateRedundantTransactions(transactions):

    # check for identical items
    for i in range(len(transactions)):
        for j in range(i+1, len(transactions)):
            if transactions[i]["from"] == transactions[j]["to"] and \
                transactions[i]["to"] == transactions[j]["from"] and \
                transactions[i]["from"] is not None:
                    transactions[i]["amount"] -= transactions[j]["amount"]
                    transactions[j]["from"] = None

    #delete merged items
    for t in transactions:

        if t["from"] is None:

            transactions.remove(t)

        elif t["amount"] < 0:

            #change to positive
            t["amount"] = abs(t["amount"])

            #swap payee
            temp = t["from"]
            t["from"] = t["to"]
            t["to"] = temp
    return transactions


def formatTransactionAmounts(transactions):
    for t in transactions:
        d = Decimal(t["amount"].numerator) / Decimal(t["amount"].denominator)
        t["amount"] = d.quantize(Decimal('0.00'), rounding=decimal.ROUND_HALF_UP)

    return transactions

def tallyExpenses(data):

    #persons variable
    persons = data["persons"]

    #expenses list
    expenses = data["expenses"]

    #transactions list
    transactions = []

    #iterate over expenses
    for expense in expenses:
        transactions += handleExpense(persons, expense)

    #merge identical transfers
    transactions = mergeTransactions(transactions)

    #eliminate redundant (opposing transfers)
    transactions = eliminateRedundantTransactions(transactions)

    #change to decimal and round
    transactions = formatTransactionAmounts(transactions)

    print(transactions)

tallyExpenses(test_input)
