import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
import os
import time

# Определяем текущую директорию
current_dir = os.getcwd()

# Функция для проверки CAPTCHA
async def check_captcha(page):
    while True:
        html = await page.content()
        soup = BeautifulSoup(html, "html.parser")
        if soup.find("div", class_="target-icaptcha-slot") or soup.find("div", class_="g-recaptcha"):
            print("CAPTCHA обнаружена, ждем 30 секунд...")
            await asyncio.sleep(30)
        else:
            break

# Функция для сохранения данных в CSV
def save_to_csv(all_data):
    file_path = os.path.join(current_dir, "result.csv")
    df = pd.DataFrame(all_data)
    df.to_csv(file_path, index=False)
    print(f"Данные сохранены в {file_path}")

# Функция для обработки одной ссылки
async def process_page(page, link, all_data, mistakes):
    try:
        await page.goto(link, timeout=30000)
        await check_captcha(page)
        time.sleep(0.3)
        # Загружаем HTML и парсим его с помощью BeautifulSoup
        html = await page.content()
        bs = BeautifulSoup(html, 'lxml')

        # Определяем количество страниц пагинации
        times_element = bs.find("ol", class_="pagination__items")
        try:
            times = int(times_element.findAll('li')[-1].text)
        except Exception as e:
            print(f"problem: {e}")
            mistakes.append(link)
            return

        # Получаем код производителя
        code_element = bs.find(
            class_="ux-labels-values ux-labels-values--inline col-6 ux-labels-values--manufacturerPartNumber"
        )
        if code_element:
            code = code_element.find(class_="ux-labels-values__values").text.strip()
        else:
            print(f"Проблема с кодом производителя, добавляем в ошибки.")
            mistakes.append(link)
            return

        # Переход по каждой странице пагинации
        for tme in range(times):
            print(f"Обрабатываем страницу {tme + 1} из {times} для {code}")
            html = await page.content()
            soup = BeautifulSoup(html, 'html.parser')

            # Ищем таблицу совместимости
            listings = soup.findAll(class_="motors-compatibility-table")
            if listings:
                table = listings[0].find("table")
                headers = [header.text.strip() for header in table.find_all('th')]

                # Если заголовки еще не определены, инициализируем словарь
                if not all_data and headers:
                    all_data.update({header: [] for header in headers})
                    all_data["ManufacturerPartCode"] = []

                # Извлекаем данные из строк таблицы
                for row in table.find_all('tr'):
                    cells = row.find_all('td')
                    if not cells:
                        continue

                    if headers:
                        # Сопоставляем данные с заголовками
                        for header, cell in zip(headers, cells):
                            all_data[header].append(cell.text.strip())
                    else:
                        # Сопоставляем данные с индексами колонок
                        for idx, cell in enumerate(cells):
                            col_name = f"Column {idx + 1}"
                            if col_name not in all_data:
                                all_data[col_name] = []
                            all_data[col_name].append(cell.text.strip())
                    all_data["ManufacturerPartCode"].append(code)

            # Сохраняем данные после обработки каждой страницы
            save_to_csv(all_data)

            try:
                if tme != times-1:
                    await page.wait_for_selector(".pagination__next.icon-btn", timeout=10000)
                    next_button = await page.query_selector(".pagination__next.icon-btn")
                    await next_button.click(force=True)
                    
            except Exception as e:
                print(e)
                break


    except Exception as e:
        mistakes.append(link)
        print(f"Ошибка при обработке {link}: {e}")

# Асинхронная функция для обработки ссылок в 10 вкладках
async def process_links_in_tabs(context, link_chunks, all_data, mistakes):
    tasks = []
    for chunk in link_chunks:
        page = await context.new_page()  # Создаем новую вкладку
        task = process_links_in_tab(page, chunk, all_data, mistakes)
        tasks.append(task)
    await asyncio.gather(*tasks)

# Функция для обработки группы ссылок в одной вкладке
async def process_links_in_tab(page, links, all_data, mistakes):
    for link in links:
        await process_page(page, link, all_data, mistakes)
    await page.close()

# Основная асинхронная функция
async def main():
    links_file = os.path.join(current_dir, "Adylbek_urls.csv")
    links = list(pd.read_csv(links_file)["urls"])
    value_to_remove = links[0]
    while value_to_remove in links:
        links.remove(value_to_remove)
    all_data = {}
    mistakes = []

    # Разбиваем ссылки на 10 групп
    chunk_size = len(links) // 10
    link_chunks = [links[i:i + chunk_size] for i in range(0, len(links), chunk_size)]

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Обрабатываем ссылки в 10 вкладках
        await process_links_in_tabs(context, link_chunks, all_data, mistakes)

        await browser.close()

    # Сохраняем данные
    result_file = os.path.join(current_dir, "result.csv")
    pd.DataFrame(all_data).to_csv(result_file, index=False)

    # Сохраняем ошибки
    if mistakes:
        mistakes_file = os.path.join(current_dir, "mistakes.csv")
        pd.DataFrame({"mistakes": mistakes}).to_csv(mistakes_file, index=False)
        print(f"Ошибки сохранены в {mistakes_file}")

# Запуск кода
if __name__ == "__main__":
    asyncio.run(main())
