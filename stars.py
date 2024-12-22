import hashlib
import secrets
from telethon import TelegramClient
from telethon.tl.functions.account import GetPasswordRequest
from telethon.tl.functions.payments import GetStarsRevenueWithdrawalUrlRequest
from telethon.tl.types import InputCheckPasswordSRP

# Ваши учетные данные Telegram
api_id = '816522'
api_hash = '0f4dfabcbeab216e54aba46032411d68'
client = TelegramClient('session', api_id, api_hash)

# SRP функции
def hash_sha256(data):
    """Вычисление SHA-256 хэша."""
    return hashlib.sha256(data).digest()

def calculate_x(salt, password):
    """Вычисление 'x' из соли и пароля."""
    salted_password = salt + password.encode()
    return int.from_bytes(hash_sha256(salted_password), "big")

def calculate_A(g, N):
    """Вычисление клиентского публичного ключа 'A'."""
    a = secrets.randbits(2048)  # Генерация случайного 'a'
    A = pow(g, a, N)
    return a, A

def calculate_u(A, B):
    """Вычисление 'u' как хэш 'A' и 'B'."""
    u = int.from_bytes(hash_sha256(A.to_bytes(256, "big") + B.to_bytes(256, "big")), "big")
    return u

def calculate_S(B, g, x, a, u, N):
    """Вычисление общего секрета 'S'."""
    base = B - pow(g, x, N)
    exp = a + u * x
    S = pow(base, exp, N)
    return S

def calculate_M1(A, B, S):
    """Вычисление доказательства знания пароля 'M1'."""
    K = hash_sha256(S.to_bytes(256, "big"))  # Общий ключ
    M1 = hash_sha256(A.to_bytes(256, "big") + B.to_bytes(256, "big") + K)
    return M1
async def srp_auth_and_withdraw():
    # Шаг 1: Получить информацию о пароле
    password_info = await client(GetPasswordRequest())

    # Вывод информации для отладки
    print(password_info.stringify())  # Вывод структуры объекта Password

    # Шаг 2: Ввод пароля пользователем
    user_password = input("Введите пароль двухфакторной аутентификации: ")

    # Шаг 3: Получение параметров от Telegram
    N = int.from_bytes(password_info.srp.n, "big")  # Простое число N
    g = password_info.srp.g  # Генератор g
    B = int.from_bytes(password_info.srp.B, "big")  # Публичный ключ сервера
    salt = password_info.srp.salt  # Соль
    srp_id = password_info.srp.id  # ID SRP сессии

    # Шаг 4: Вычисления SRP
    x = calculate_x(salt, user_password)  # Вычисление x
    a, A = calculate_A(g, N)  # Генерация клиентских параметров
    u = calculate_u(A, B)  # Вычисление 'u'
    S = calculate_S(B, g, x, a, u, N)  # Вычисление общего секрета
    M1 = calculate_M1(A, B, S)  # Вычисление M1

    # Шаг 5: Создание объекта InputCheckPasswordSRP
    password = InputCheckPasswordSRP(
        srp_id=srp_id,
        A=A.to_bytes(256, "big"),
        M1=M1
    )

    # Шаг 6: Запросить URL для вывода средств
    withdrawal_result = await client(GetStarsRevenueWithdrawalUrlRequest(
        peer="inputPeerChannel",  # Замените на ваш канал или бота
        stars=1000,               # Количество звёзд для вывода
        password=password
    ))

    print("URL для вывода средств:", withdrawal_result.url)


# Запуск клиента и выполнение функции
with client:
    client.loop.run_until_complete(srp_auth_and_withdraw())
