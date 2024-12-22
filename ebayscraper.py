from DrissionPage import ChromiumPage
from DrissionPage import ChromiumOptions
import pandas as pd
from bs4 import BeautifulSoup
import time
import json

website = ChromiumPage()

def check_captcha():
    soup = BeautifulSoup(website.html, "html.parser")
    if soup.find("div", class_="target-icaptcha-slot") or soup.find("div", class_="g-recaptcha"):
        time.sleep(30)

all_data = []
urls = pd.read_csv(r"C:\Users\User\Desktop\work\urls.csv")
urls =list(set(urls['urls']))

# Цикл по каждому элементу из списка cl
for i in urls:
    website.get(i)
    check_captcha()
    
    bs = BeautifulSoup(website.html, 'lxml')
    times = int(bs.find("ol", class_="pagination__items").findAll('li')[-1].text)
    print(times)
    code = bs.find(class_="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--manufacturerPartNumber").find(class_="ux-labels-values__values").text
        
    if times == 0:
        times = 1
            
    for tme in range(times):
        soup = BeautifulSoup(website.html, 'html.parser')

        # Ищем таблицу совместимости
        listings = soup.findAll(class_="motors-compatibility-table")

        if listings:
            table = listings[0].find("table")

            # Извлекаем заголовки таблицы (если есть)
            headers = [header.text.strip() for header in table.find_all('th')]

            # Если словарь еще не инициализирован заголовками, инициализируем его
            if not all_data and headers:
                all_data = {header: [] for header in headers}
                all_data["ManufacturerPartCode"] = []

            # Если заголовков нет, будем использовать индексы колонок
            use_index = not bool(headers)

            # Извлекаем данные из каждой строки таблицы
            for row in table.find_all('tr'):
                cells = row.find_all('td')

                # Пропускаем пустые строки
                if not cells:
                    continue

                # Заполняем данные по индексам столбцов, если нет заголовков
                if use_index:
                    for idx, cell in enumerate(cells):
                        col_name = f"Column {idx + 1}"
                        if col_name not in all_data:
                            all_data[col_name] = []
                        all_data[col_name].append(cell.text.strip())
                    all_data["ManufacturerPartCode"].append(code)
                else:
                    # Заполняем данные с заголовками
                    for header, cell in zip(headers, cells):
                        all_data[header].append(cell.text.strip())
                    all_data["ManufacturerPartCode"].append(code)
                
            try:
                website.ele("tag:button@type=next").click("js")
                time.sleep(0.7)
            except:
                print("конец")

    time.sleep(1)  # Случайная задержка от 4 до 6 секунд

df = pd.DataFrame(all_data)
df.to_csv("ebay.csv")