import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import mysql.connector


option = webdriver.ChromeOptions()
option.add_argument("--headless")
driver = webdriver.Chrome(
    ChromeDriverManager().install(), chrome_options=option)
driver.get("https://vi.wikipedia.org/wiki/T%E1%BB%89nh_th%C3%A0nh_Vi%E1%BB%87t_Nam")
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
            sql_com = "INSERT INTO city (city_id, city_name) VALUES(%s,%s)"
            val = (cities_id[index], f"{cities[index]}")
            mycursor.execute(sql_com, val)
            mydb.commit()
            print(
                f"Insert into database city ID: {cities_id[index]}, city name: {cities[index]}")
        break

# for city in cities:


driver.close()
