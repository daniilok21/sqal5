import requests

BASE_URL = 'http://localhost:5000/api/users'

"""
Данные админа:
admin@example.com
admin123
"""

print("Начало тестирования API пользователей")

print("\n Получение списка всех пользователей:")
input("Нажмите Enter для продолжения")
response = requests.get(BASE_URL)
print(f"Статус код: {response.status_code}")
users = response.json()['users']
print(f"Найдено пользователей: {len(users)}")
print(users)

print("\nДобавление нового пользователя:")
input("Нажмите Enter для продолжения")
response = requests.post(BASE_URL, json={
    'surname': 'Examplov',
    'name': 'Example',
    'age': 25,
    'position': 'lol',
    'speciality': 'lol',
    'address': 'lol',
    'email': 'example@example.com',
    'password': '123456'
})
# 'email' должен быть уникальным'
# Упадет если одинаковые email
print(f"Статус код: {response.status_code}")
new_user = response.json()
user_id = new_user['id']
print(f"Создан пользователь с ID: {user_id}")
response = requests.get(BASE_URL)
users = response.json()['users']
print(users)

print("\nПолучение созданного пользователя:")
input("Нажмите Enter для продолжения")
response = requests.get(f"{BASE_URL}/{user_id}")
print(f"Статус код: {response.status_code}")
user_data = response.json()['user']
print("Данные пользователя:")
print(f"Имя: {user_data['name']}")
print(f"Фамилия: {user_data['surname']}")
print(f"Email: {user_data['email']}")

print("\nРедактирование данных пользователя:")
input("Нажмите Enter для продолжения")
update_data = {'name': 'Petr', 'surname': 'Ivanov'}
response = requests.put(f"{BASE_URL}/{user_id}", json=update_data)
print(f"Статус код: {response.status_code}")

response = requests.get(f"{BASE_URL}/{user_id}")
updated_user = response.json()['user']
print(f"Новое имя: {updated_user['name']}")
print(f"Новая фамилия: {updated_user['surname']}")
response = requests.get(BASE_URL)
users = response.json()['users']
print(users)

print("\nУдаление пользователя:")
input("Нажмите Enter для продолжения")
response = requests.delete(f"{BASE_URL}/{user_id}")
print(f"Статус код: {response.status_code}")
response = requests.get(BASE_URL)
users = response.json()['users']
print(users)

print("\nТестирование завершено")