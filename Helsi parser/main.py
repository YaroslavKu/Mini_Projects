import time
from math import ceil

import xlsxwriter as xlsxwriter
from selenium import webdriver


DRIVER_PATH = 'to/chromedriver/path'
LINK        = 'https://reform.helsi.me/'
LOGIN       = 'login'
PASSWORD    = 'password'


def main():
    driver = webdriver.Chrome(DRIVER_PATH)
    driver.get(LINK)

    input("Press enter to input email")
    driver.find_element_by_name('user.email').send_keys(LOGIN)

    input("Press enter to input password")
    driver.find_element_by_name('password').send_keys(PASSWORD)

    input("Press enter to continue")


    # Open table with all patients
    driver.find_element_by_xpath('//a[@href="/my-patients?firstload=1"]').click()
    driver.find_element_by_name('person[age_to]').send_keys('99')
    driver.find_element_by_id('submit_filter_my_patients').click()

    # Get num of pages
    s = driver.find_element_by_class_name('form-title__wrap').text
    num_of_pages = ceil(float(''.join(s for s in s if s.isdigit())) / 20)
    print(num_of_pages)

    # Creat .xlsx pile
    workbook = xlsxwriter.Workbook('Patients.xlsx')
    worksheet = workbook.add_worksheet("My sheet")
    row = 0

    # Parse info
    for page in range(num_of_pages):
        patients = []

        for p in driver.find_elements_by_class_name('name'):
            if p.text == "П.І.Б.":
                continue
            patients.append({"pib": p.text.strip('assignment\n')})

        count = 0
        for p in driver.find_elements_by_class_name('birthdate'):
            if p.text == "Дата народження":
                continue
            patients[count]["birth"] = p.text
            count += 1

        count = 0
        for p in driver.find_elements_by_class_name('phone'):
            if p.text == "Адреса" or p.text == "Телефон":
                continue
            patients[count]["phone"] = p.text
            count += 1

        count = 0
        for i, p in enumerate(driver.find_elements_by_class_name('address')):
            if p.text == "Адреса":
                continue
            patients[count]["address"] = p.text
            count += 1

        for p in patients:
            print(p.get("pib"))
            print(p.get("birth"))
            print(p.get("phone"))
            print(p.get("address"))
            print()

            worksheet.write(row, 0, p.get("pib"))
            worksheet.write(row, 1, p.get("birth"))
            worksheet.write(row, 2, p.get("phone"))
            worksheet.write(row, 3, p.get("address"))
            row += 1

        if page != num_of_pages-1:
            driver.find_element_by_link_text('chevron_right').click()
            # time.sleep(1)

    workbook.close()
    driver.quit()


if __name__ == '__main__':
    main()


