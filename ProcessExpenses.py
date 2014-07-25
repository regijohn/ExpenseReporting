import sys
import csv
import re

#Class
class ExpenseItem:
	countOfItems = 0
	totalExpense = 0

        #category: eg. GROCERIES, UTILITIES etc
	#segment: eg. MUST_HAVE, NEEDS etc. Indicates whether the expense is a must have vs a want
	def __init__(self, iCategory, iSegment):
                self.category = iCategory
                self.segment = iSegment

                #Patterns for searching for this expense
                self.patterns = []

        #Update the ExpenseItem with the actual line item expense
        def Update(self, lineItemExpense):
                self.countOfItems = self.countOfItems + 1
                self.totalExpense = self.totalExpense + lineItemExpense

#Import each entry from the ItemTable file and create a dictonary
#to store each entry.
#The dictionary will have ITEM_CATEGORY as the key.
#The value will be an ExpenseItem object
def ProcessItemTable(itemTableFile, expenseItems):
    csvFileReader = csv.DictReader(open(itemTableFile, 'rb'))

    for line in csvFileReader:
        #Check to see if we've already added the item
        #If not, then add the item into the dictionary
        if line['ITEM_CATEGORY'] not in expenseItems:
            expenseItems[line['ITEM_CATEGORY']] = ExpenseItem(line['ITEM_CATEGORY'], line['ITEM_SEGMENT'])

        #Add the patterns
        expenseItems[line['ITEM_CATEGORY']].patterns.append(line['ITEM_PATTERN'])

#Process the expense items in the data file
def ProcessExpenseItems(expenseDataFile, expenseItems):
    
    csvFileReader = csv.DictReader(open(expenseDataFile, 'rb'))
    
    for line in csvFileReader:

        #found tracks whether the item that was read in matched
        #one of the patterns in the ItemTable file
	found = False

	#isExpense tracks whether the item was an expense or a debit
        isExpense = False
        
        #Get the amount
	lineItemExpense = float(line['Amount'])

	#If the amount is a negative, that means this is an expense
	if lineItemExpense < 0:
                isExpense = True
                #Turn the value into a positive number
                lineItemExpense = -lineItemExpense

        description = None
        key = None

        #Check to see if we're processing the credit card or debit card entries
        #For debit card, the description is in a field called ExtDesc
        #for credit card, the description is in a field called Description
        if 'ExtDesc' in line.keys():
            description = line['ExtDesc']
            words = description.split(' ')
        elif 'Description' in line.keys():
            description = line['Description']
            words = description.split(' ')[4:]

        #If possible, match the description of the item to a known pattern by iterating through
        #each ExpenseItem, and then checking against each pattern in the ExpenseItem
        for expenseItem in expenseItems.values():
                for pattern in expenseItem.patterns:  
                        if re.search(pattern, description):
                                #If found, then update the ExpenseItem with this expense
                                #But only if this is an expense
                                if isExpense: expenseItem.Update(lineItemExpense)
                                found = True
                        if found: break
                if found: break

        #If we don't find a matching pattern, then append the value 
        #to the expenseItems dictionary for later processing
        if ((not found) and isExpense):     
                
                #If description is empty, then this usually means the expense is from a check. 
                if not description: 
                        key = line['TranDesc'] #"Check" is usually in the TranDesc field

                #We check for specific transaction types
                #Withdrawal and ATM Withdrawal, we'll create a new key for this
##                if 'Withdrawal' in line['Trandesc']:
##                        key = 'Withdrawal'

                #Generate a key for the dictionary item by using the first or
                #first 2 words of description.
                if not key:
                        if (len(words) > 1):
                                key = words[0] + '_' + words[1]
                        else:
                                key = words[0]

                #Check to see if the key already exists. If not, then add it
                if key not in expenseItems:
                        expenseItems[key] = ExpenseItem(key, 'UNKNOWN')

                #Increment the count of such items
                expenseItems[key].Update(lineItemExpense)
                    
#Get the data file and item table
if len(sys.argv) < 3:
        print "Usage: python ProcessExpenses.py <itemtable>.csv <expensedata>.csv"
        sys.exit()
itemTableFile = sys.argv[1]

#Initialize the dictionary that will hold all the expense items
expenseItems = dict()

#Get the expense items from the table file
ProcessItemTable(itemTableFile, expenseItems)

totalExpense = 0
mustHaveTotalExpense = 0

#Get the data. We may be giving more than 1 file
for i in range(2, len(sys.argv)):
        ProcessExpenseItems(sys.argv[i],expenseItems)

#Get the total expenses and print out each expense item
for item in expenseItems.values():
    totalExpense = totalExpense + item.totalExpense

    if item.segment == 'MUST_HAVE':
        mustHaveTotalExpense = mustHaveTotalExpense + item.totalExpense

    print item.category, item.totalExpense
        
print 'Total Expense = ', totalExpense, 'Must Have Total Expense = ', mustHaveTotalExpense








