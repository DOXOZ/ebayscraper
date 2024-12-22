from DrissionPage import ChromiumPage, ChromiumOptions, Chromium
from bs4 import BeautifulSoup
import pandas as pd
import time
import os
opt = ChromiumOptions().headless()
website = ChromiumPage()

current_dir = os.path.dirname(os.path.realpath(__file__))

def check_captcha():
    soup = BeautifulSoup(website.html, "html.parser")
    if soup.find("div", class_="target-icaptcha-slot") or soup.find("div", class_="g-recaptcha"):
        time.sleep(30)

links_file = os.path.join(current_dir, "urls.csv")
links = list(pd.read_csv(links_file)["urls"])
value_to_remove = links[0]
all_data = []

while value_to_remove in links:
    links.remove(value_to_remove)

mistakes = []

for i in links:
    website.get(i,timeout=0.1)
    check_captcha()

    bs = BeautifulSoup(website.html, 'lxml')
    times = bs.find("ol", class_="pagination__items")
    if times:
        times=int(times.findAll('li')[-1].text)
    else:
        mistakes.append(i)
        continue
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
    file_path = os.path.join(current_dir, "result.csv")
    pd.DataFrame({"result": all_data}).to_csv(file_path)
    time.sleep(1)  # Случайная задержка от 4 до 6 секунд

if mistakes:
    file_pathb = os.path.join(current_dir, "mistakes.csv")
    pd.DataFrame({"mistakes": mistakes}).to_csv(file_pathb)