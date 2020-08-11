from django.shortcuts import render
import re
from urllib.request import urlopen, Request
import os
from datetime import datetime

from openpyxl import Workbook
from bs4 import BeautifulSoup

save_excel = True #Change to "True" to save email into Excel

book = Workbook()
sheet = book.active

# Create your views here.
def index(request):
    # path="images"
    file_path=""
    if request.method == 'POST':

        url_address=request.POST["url_add"]
        # print(url_address)

        file_name = request.POST["file_name"]
        # print(file_name)
        # webpage = "http://www.cell-phone-list.net/cell-phone-number-list.html"

        webpage = url_address

        if save_excel:
            name_the_file = file_name
            # name_the_file = input("Name the file you would like to save the data in (don't include .xlsx): ")
            file_path = "/static/images/"+name_the_file+".xlsx"
        try:
            page = urlopen(webpage)

            start_scrape(page)

            # path = "static/images/"+ name_the_file + ".xlsx"
            # file = name_the_file + ".xlsx"

        except:
            hdr = {'User-Agent': 'Mozilla/5.0'}
            req = Request(webpage, headers=hdr)
            page = urlopen(req)
            start_scrape(page, name_the_file)

        context = {'file_path' : file_path, 'status': True, 'file_name': name_the_file}
        return render(request, 'index.html', context)
    # context = {'file_name': file_path}
    return render(request, 'index.html')


def start_scrape(page, name_the_file):
    print("\n\nWebpage is currently being scrapped... please wait...")

    scrape = BeautifulSoup(page, 'html.parser')
    scrape = scrape.get_text()

    phone_numbers = set(
        re.findall(r"((?:\d{3}|\(\d{3}\))?(?:\s|-|\.)?\d{3}(?:\s|-|\.)\d{4})", scrape))  # "set" removes duplicates
    emails = set(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,3}", scrape))

    nodupnumber = len(list(phone_numbers))
    nodupemail = len(list(emails))

    dupnumber = len(list(re.findall(r"((?:\d{3}|\(\d{3}\))?(?:\s|-|\.)?\d{3}(?:\s|-|\.)\d{4})", scrape)))
    dupemail = len(list(re.findall(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,3}", scrape)))

    number_of_dup_number = int(dupnumber) - int(nodupnumber)
    number_of_dup_email = int(dupemail) - int(nodupemail)

    email_list = list(emails)

    if len(phone_numbers) == 0:
        print("No phone number(s) found.")

        print("-----------------------------\n")
    else:
        count = 1
        for item in phone_numbers:
            print("Phone number #" + str(count) + ': ' + item)
            count += 1

    print("-----------------------------\n")

    if len(emails) == 0:
        print("No email address(es) found.")
        print("-----------------------------\n")
    else:
        count = 1
        for item in emails:
            print('Email address #' + str(count) + ': ' + item)
            count += 1

    if save_excel:
        for row in zip(email_list):
            sheet.append(row)
        excel_file = ("static/images/"+name_the_file+".xlsx")
        book.save(excel_file)

    print("\nDuplicates have been removed from list.")
    print("Total phone numbers: ", nodupnumber)
    print("Total email addresses: ", nodupemail)
    print("There were " + str(number_of_dup_number) + " duplicate phone numbers.")
    print("There were " + str(number_of_dup_email) + " duplicate email addresses.")

    if save_excel:
        print("\n\nData has been stored inside of an Excel spreadsheet named: "
              + excel_file + " in this directory: " + os.getcwd())
        mod_time = os.stat(excel_file).st_mtime
        print("\nCompleted at: " + str(datetime.fromtimestamp(mod_time)))
        print("\nSize of file: " + str(os.stat(excel_file).st_size) + " KB")
