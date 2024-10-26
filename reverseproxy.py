from flask import Flask, request, Response
from DrissionPage import ChromiumPage
import time
import requests

app = Flask(__name__)

# Инициализация DrissionPage
website = ChromiumPage()

# Ваши куки
cookies = [
    {'name': 'NID', 'value': '518=ApstY0lx9Ao-S-6kscRrDtWcjVwb_rDFtWHih20MNIfa--wkp6z6_pp_ldQv1vGyBD947rJVioRpDFKzTy0Fl69mq_eoei6icC4D-DLFfuWv_rG65_UyfnsrkpIskJNqyutOzBhpLZBcM-uD-7ED3uUH-U2BGtonEWWxmZUlZfyFVCghPrNWQeSpCAY', 'domain': '.google.com'},
    {'name': 'AMP_6e403e775d', 'value': 'JTdCJTIyZGV2aWNlSWQlMjIlM0ElMjJhYzkyMWU4Yi0wNDcxLTQ5YTgtYmVhNC05MTNlMTI3ZTRmNWMlMjIlMkMlMjJ1c2VySWQlMjIlM0ElMjJ4M1dKNmwwRk1DZ3prTEtiMkltbXlnQmZGeWoyJTIyJTJDJTIyc2Vzc2lvbklkJTIyJTNBMTcyOTIzMTY4MzA5NyUyQyUyMm9wdE91dCUyMiUzQWZhbHNlJTJDJTIybGFzdEV2ZW50VGltZSUyMiUzQTE3MjkyMzIzMDc3OTklMkMlMjJsYXN0RXZlbnRJZCUyMiUzQTExNCU3RA==', 'domain': '.quillbot.com'},
    {'name': '_uetvid', 'value': 'e97e63808cb311efb03ab5fb90fc4a13', 'domain': '.quillbot.com'},
    {'name': '_ga_D39F2PYGLM', 'value': 'GS1.1.1729231684.2.1.1729232279.0.0.281888902', 'domain': '.quillbot.com'},
    {'name': 'OptanonConsent', 'value': 'isGpcEnabled=0&datestamp=Fri+Oct+18+2024+12%3A17%3A59+GMT%2B0600+(%D0%9A%D0%B8%D1%80%D0%B3%D0%B8%D0%B7%D0%B8%D1%8F)&version=202211.1.0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1%2CC0005%3A1&AwaitingReconsent=false', 'domain': '.quillbot.com'},
    {'name': 'qdid', 'value': '16725995772315476883', 'domain': 'quillbot.com'},
    {'name': 'AMP_MKTG_6e403e775d', 'value': 'JTdCJTdE', 'domain': '.quillbot.com'},
    {'name': 'useridtoken', 'value': 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjcxOGY0ZGY5MmFkMTc1ZjZhMDMwN2FiNjVkOGY2N2YwNTRmYTFlNWYiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vcGFyYXBocmFzZXItNDcyYzEiLCJhdWQiOiJwYXJhcGhyYXNlci00NzJjMSIsImF1dGhfdGltZSI6MTcyOTE4OTg3MCwidXNlcl9pZCI6IngzV0o2bDBGTUNnemtMS2IySW1teWdCZkZ5ajIiLCJzdWIiOiJ4M1dKNmwwRk1DZ3prTEtiMkltbXlnQmZGeWoyIiwiaWF0IjoxNzI5MjMxNjIxLCJleHAiOjE3MjkyMzUyMjEsImVtYWlsIjoiemh1bnVzb3ZfYUBhdWNhLmtnIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJmaXJlYmFzZSI6eyJpZGVudGl0aWVzIjp7ImVtYWlsIjpbInpodW51c292X2FAYXVjYS5rZyJdfSwic2lnbl9pbl9wcm92aWRlciI6InBhc3N3b3JkIn19.rxdUzvmrH3pQ6S5_KKJx0-T8fvUZLYJlzFC3d16G3ZqaB3GQuETZb51ixo7Ekp92xPzwEopDj4zpP9sfKvDAKFR4ez15e8ebrWUhZGhC6hAhOFkdlPM_PIR0GFYmhKtsRp4QgeTQS4spxJTlFGZjzeWtHGdUelNM_P6USSzijbe5pzJPCoKMwyuxQJQJZRMu_NNQmmQm6E79I0SCf7C-Ivm7VKcYhgo_MbuQYFwskdUli_MvRHWOY_s6IJT2U_ex9Iq5DKTwXSy4KHh8Y1hmOGo0gb16fwd0HIaHtfPnWX3Hk8_vsv8TGKEqjJyRA_UjRal0EcifjRUftvAjSiUDnw', 'domain': 'quillbot.com'},
    {'name': 'abIDV2', 'value': '695', 'domain': 'quillbot.com'},
    {'name': '_sp_ses.48cd', 'value': '*', 'domain': '.quillbot.com'},
    {'name': '_gid', 'value': 'GA1.2.222995632.1729189430', 'domain': '.quillbot.com'},
    {'name': 'qbDeviceId', 'value': 'ac921e8b-0471-49a8-bea4-913e127e4f5c', 'domain': 'quillbot.com'},
    {'name': 'connect.sid', 'value': 's%3Aj2ABiTQi81FKA7cb_OpB2qa7Hl0XVrt9.QJqv4WV05YV4mvOTZhA41jt7Gk%2FhocH00mBVUa0dIp0', 'domain': 'quillbot.com'},
    {'name': '_fbp', 'value': 'fb.1.1729188921579.1329477593', 'domain': '.quillbot.com'},
    {'name': 'FPID', 'value': 'FPID2.2.3gZ0SJYfa9RRmvuTJqHRAdDgdsBVgKHmDfoedBIJrjA%3D.1729188981', 'domain': '.quillbot.com'},
    {'name': '_ga', 'value': 'GA1.1.1415028515.1729188981', 'domain': '.quillbot.com'},
    {'name': 'anonID', 'value': 'a2890ae71202f6a5', 'domain': 'quillbot.com'},
    {'name': 'premium', 'value': 'false', 'domain': 'quillbot.com'},
    {'name': 'authenticated', 'value': 'true', 'domain': 'quillbot.com'},
    {'name': '_gcl_au', 'value': '1.1.783906031.1729188981', 'domain': '.quillbot.com'},
    {'name': 'cl_val', 'value': '35', 'domain': '.quillbot.com'},
    {'name': 'FPLC', 'value': '48FoIMssoJid3M8MZebHMF8s5paqXoFJVYNRmKmsc93iSwNl1%2BUIhQ7xC2u6rvrDqCpGGQNO24kGAx3hjJdeXpKKeiEMvOmXoP5X90uka29PMLE60kirbOZB6V2ngQ%3D%3D', 'domain': '.quillbot.com'},
    {'name': '_sp_id.48cd', 'value': '3baf5dd6-1f74-4a9c-9901-87526fb84a46.1729188980.2.1729188985.1729188967.5cb97337-fc39-4935-a7be-0da5f6cf0b9f', 'domain': '.quillbot.com'},
]

# Задайте User-Agent для запросов
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
}

@app.route('/')
def index():
    # Отображение главной страницы Quillbot
    website.get("https://quillbot.com/")
    website.set.cookies(cookies)  # Устанавливаем куки
    time.sleep(2)  # Ждем, чтобы страница полностью загрузилась
    html_content = website.html
    return Response(html_content, content_type='text/html')

@app.route('/paraphrase', methods=['POST'])
def paraphrase():
    input_text = request.form.get('text', 'Default text')

    # Вход на сайт Quillbot
    website.get("https://quillbot.com/login?returnUrl=/")
    website.set.cookies(cookies)
    
    # Ждем загрузки страницы после логина
    time.sleep(3)

    # Открываем страницу с функционалом перефразирования
    website.get("https://quillbot.com/")
    time.sleep(2)

    # Вводим текст для перефразирования
    website.ele("tag:textarea@id=input-box").input(input_text)
    time.sleep(1)

    # Нажимаем на кнопку перефразирования
    website.ele("tag:button@id=paraphrase-btn").click()

    # Ожидание завершения обработки
    time.sleep(3)

    # Извлекаем результат перефразирования
    paraphrased_text = website.run_script('return document.querySelector("#output-box").innerText')

    # Возвращаем результат клиенту
    return Response(paraphrased_text, content_type='text/plain')

@app.route('/<path:path>', methods=['GET', 'POST'])
def proxy(path):
    # Прокси для остальных маршрутов
    url = f"https://quillbot.com/{path}"
    
    # Создайте сессию
    session = requests.Session()

    # Установите куки
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])

    # Включаем кастомные заголовки
    if request.method == 'POST':
        response = session.post(url, headers=headers, data=request.form, verify=False)
    else:
        response = session.get(url, headers=headers, params=request.args, verify=False)

    return Response(response.content, content_type=response.headers['Content-Type'])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)  # Запускаем приложение на HTTP
