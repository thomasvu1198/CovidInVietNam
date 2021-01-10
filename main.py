import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector

# lay thong tin ve cac thanh pho


def getcity():
    option = webdriver.ChromeOptions()
    option.add_argument("--headless")
    driver = webdriver.Chrome(
        ChromeDriverManager().install(), chrome_options=option)
    driver.get(
        "https://vi.wikipedia.org/wiki/T%E1%BB%89nh_th%C3%A0nh_Vi%E1%BB%87t_Nam")
    table_source = driver.find_elements_by_tag_name('table')[4]

    cities = []
    cities_id = []
    rows = table_source.find_elements_by_tag_name('tr')

    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="221198",
        database="Covid19"
    )
    i = 1
    while i < len(rows):
        cols = rows[i].find_elements_by_tag_name('td')
        cities.append(cols[1].text)
        cities_id.append(cols[0].text)
        i = i + 1
        if i == len(rows):
            cities[29] = cities[29][10:]
            mycursor = mydb.cursor(buffered=True)
            del_sql = "DELETE FROM city"
            mycursor.execute(del_sql)
            mydb.commit()
            for index in range(0, len(cities_id)):
                mycursor = mydb.cursor(buffered=True)
                sql_com = "INSERT INTO city (id, name) VALUES(%s,%s)"
                val = (cities_id[index], f"{cities[index]}")
                mycursor.execute(sql_com, val)
                mydb.commit()
                print(
                    f"Insert into database city ID: {cities_id[index]}, city name: {cities[index]}")
            break
    mycursor = mydb.cursor(buffered=True)
    sql = "INSERT INTO city(name) VALUES ('None')"
    mycursor.execute(sql)
    mydb.commit()
    driver.close()

# lay thong tin covid


def getcovidstat():
    option = webdriver.ChromeOptions()
    option.add_argument("--headless")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=option)
    driver.get('https://ncov.moh.gov.vn/')
    table_source = driver.find_elements_by_id('sailorTableArea')

    table_data = table_source[0].find_element_by_id('sailorTable')
    rows = table_source[0].find_elements_by_tag_name('tr')
    count = 0
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="******",
        database="Covid19"
    )

    mycursor = mydb.cursor(buffered=True)
    del_sql = "DELETE FROM covid_data"
    mycursor.execute(del_sql)
    mydb.commit()
    print("delete all data: Done")
    for index in range(1, len(rows)):
        cols = rows[index].find_elements_by_tag_name('td')
        patient = cols[0].get_attribute('innerText').replace(
            "(", "").replace(" ", "").replace(")", "")
        age = cols[1].get_attribute('innerText')
        city = cols[3].get_attribute('innerText')
        status = cols[4].get_attribute('innerText')
        nationality = cols[5].get_attribute('innerText')

        mycursor = mydb.cursor(buffered=True)

        ins_sql1 = "INSERT INTO covid_data(patient, age, status, nationality) VALUES (%s,%s,%s,%s)"
        val1 = (patient, age, status, nationality)
        mycursor.execute(ins_sql1, val1)
        # val = (f"{name}")
        mycursor.execute(f"SELECT id FROM city WHERE name = '{city}'")
        CityID = mycursor.fetchone()
        if CityID is not None:
            CityID = CityID[0]
            sql = "UPDATE covid_data SET city_id = %s WHERE patient = %s"
            val = (CityID, f"{patient}")
            mycursor.execute(sql, val)
            mydb.commit()
            print(f"INSERT INTO DATABASE PATIENT {patient} FROM {city}")
        else:
            mycursor.execute(f"SELECT id FROM city WHERE name = 'None'")
            CityID = mycursor.fetchone()[0]
            sql = "UPDATE covid_data SET city_id = %s WHERE patient = %s"
            val = (CityID, f"{patient}")
            mycursor.execute(sql, val)
            mydb.commit()
            print(f"INSERT INTO DATABASE PATIENT {patient} FROM {city}")

    driver.quit()


def analyst():
    mydb = mysql.connector.connect(
        host="localhost",
        user="root",
        password="221198",
        database="Covid19"
    )

    total_cases = []
    active_cases = []
    death_cases = []

    # Them so benh nhan nhiem benh vao tung thanh pho trong table city
    mycursor = mydb.cursor(buffered=True)
    sql = "SELECT DISTINCT city_id FROM covid_data"
    mycursor.execute(sql)
    ids = mycursor.fetchall()
    for id in ids:
        # update tong so cases
        sql = "SELECT patient from covid_data where city_id = %s"
        val = (id)
        mycursor.execute(sql, val)
        total = len(mycursor.fetchall())
        sql1 = "UPDATE city SET total_cases = %s WHERE id = %s"
        val1 = (total, id[0])
        mycursor.execute(sql1, val1)

        # update active cases
        sql_active = "SELECT patient FROM covid_data WHERE city_id = %s AND status = 'Đang điều trị'"
        val_active = (id)
        mycursor.execute(sql_active, val_active)
        active = len(mycursor.fetchall())
        sql1_active = "UPDATE city SET active_cases = %s WHERE id = %s"
        val1__active = (active, id[0])
        mycursor.execute(sql1_active, val1__active)

        # update death cases
        sql_death = "SELECT patient FROM covid_data WHERE city_id = %s AND status = 'Tử vong'"
        val_death = (id)
        mycursor.execute(sql_death, val_death)
        death = len(mycursor.fetchall())
        sql1_death = "UPDATE city SET death_cases = %s WHERE id = %s"
        val1__death = (active, id[0])
        mycursor.execute(sql1_death, val1__death)

        # update recover cases
        recover = total - death - active
        sql1_recover = "UPDATE city SET recover_cases = %s WHERE id = %s"
        val1__recover = (recover, id[0])
        mycursor.execute(sql1_recover, val1__recover)

        mydb.commit()
        print(f"{id[0]}: {total}, {death}, {recover}")

    # voi nhung thanh pho khong bi gi, thi cac cot gan = 0 roi update status cua cac thanh pho
    SelectCity = "SELECT DISTINCT id FROM city"
    mycursor.execute(SelectCity)
    Identifiers = mycursor.fetchall()
    for Identifier in Identifiers:
        # gan cac gia tri 0 vao cac thanh pho khong co cases
        sql = 'SELECT total_cases from city WHERE id = %s'
        val = (Identifier)
        mycursor.execute(sql, val)
        all_cases = mycursor.fetchone()
        if all_cases[0] is None:
            sql1 = "UPDATE city SET total_cases = %s , active_cases = %s, death_cases = %s, recover_cases = %s WHERE id = %s"
            val1 = (0, 0, 0, 0, Identifier[0])
            mycursor.execute(sql1, val1)
            print(
                f"update city has none cases id: {Identifier[0]}, {all_cases[0]}")
            mydb.commit()
        # update status

        # cases  =0
        safe = "Safe"
        # cases =  1-10
        unsafe = "Unsafe"
        # cases = 11 -20
        dangerous = "Dangerous"
        # cases = 21 -> >50
        very_dangerous = "Very Dangerous"

        sql_active_cases = "SELECT active_cases FROM city WHERE id = %s"
        val_id = (Identifier)
        mycursor.execute(sql_active_cases, val_id)
        activeCases = mycursor.fetchone()[0]
        if activeCases is 0:
            sql_safe = "UPDATE city SET status = %s WHERE id = %s"
            val_safe = (safe, Identifier[0])
            mycursor.execute(sql_safe, val_safe)
            mydb.commit()
            print(f"Update db id: {Identifier[0]}, status = {safe}")
        elif activeCases in range(1, 11):
            sql_unsafe = "UPDATE city SET status = %s WHERE id = %s"
            val_unsafe = (unsafe, Identifier[0])
            mycursor.execute(sql_unsafe, val_unsafe)
            mydb.commit()
            print(f"Update db id: {Identifier[0]}, status = {unsafe}")

        elif activeCases in range(11, 21):
            sql_dangerous = "UPDATE city SET status = %s WHERE id = %s"
            val_dangerous = (dangerous, Identifier[0])
            mycursor.execute(sql_dangerous, val_dangerous)
            mydb.commit()
            print(f"Update db id: {Identifier[0]}, status = {dangerous}")

        elif activeCases >=21:
            sql_very_dangerous = "UPDATE city SET status = %s WHERE id = %s"
            val_very_dangerous = (very_dangerous, Identifier[0])
            mycursor.execute(sql_very_dangerous, val_very_dangerous)
            mydb.commit()
            print(f"Update db id: {Identifier[0]}, status = {very_dangerous}")
        
# getcity()
getcovidstat()
analyst()
