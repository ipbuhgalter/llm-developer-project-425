import json
from work_with_database import DatabaseManager
import services

json_string_create = '''
{
    "event": {
        "action": "create-ticket",
        "user_id": "integralik@gmail.com",
        "title": "Название письма",
        "text": "Текст письма"
    }
}
'''

json_string_list = '''
{
    "event": {
        "action": "list-my-tickets",
        "user_id": "integralik@gmail.com"
    }
}
'''

json_string_append = '''
{
    "event": {
        "action": "append-message",
        "ticket_id": "d0ddbcbc-3984-4109-a97c-3c0865826f68",
        "role": "user",
        "text": "Текст ответа"
    }
}
'''


def parse_json(json_string):
    try:
        data = json.loads(json_string)  # Парсим строку JSON
        print("Разобранные данные:")
        for key, value in data.items():
            print(f"{key}: {value}")
    except json.JSONDecodeError as e:
        print(f"Ошибка при разборе JSON: {e}")

def create_ticket(user_id: str, title: str, text: str, db: DatabaseManager):
    ticket_id = services.get_uuid()
    category = "bug"
    status = "open"
    timestamp = services.get_time()
    db.execute_query('INSERT INTO tickets(id, user_id, category, status, text, created_at, updated_at) VALUES(?, ?, ?, ?, ?, ?, ?)', (ticket_id, user_id, category, status, title, timestamp, timestamp))
    message_id = services.get_uuid()
    role = 'user'
    db.execute_query('INSERT INTO messages(id, ticket_id, role, text, created_at) VALUES(?, ?, ?, ?, ?)', (message_id, ticket_id, role, text, timestamp))
    return '{"ticket_id": ' + ticket_id + ', "created_at": "' + str(timestamp) + '"}';

def list_my_tickets(user_id: str, db: DatabaseManager):
    tickets = db.fetch_query('SELECT * FROM tickets WHERE user_id = ?', (user_id,))
    for ticket in tickets:
        print(ticket)
    return []

def append_message(ticket_id: str, role: str, text: str, db: DatabaseManager):
    message_id = services.get_uuid()
    timestamp = services.get_time()
    db.execute_query('INSERT INTO messages(id, ticket_id, role, text, created_at) VALUES(?, ?, ?, ?, ?)', (message_id, ticket_id, role, text, timestamp))
    return '{"message_id": ' + message_id + ', "ok": true}'

data = json.loads(json_string_list)['event']

db = DatabaseManager('my_database.db')
db.connect()
if data['action'] == 'create-ticket':
    result = create_ticket(data['user_id'], data['title'], data['text'], db)
if data['action'] == 'list-my-tickets':
    result = list_my_tickets(data['user_id'], db)
if data['action'] == 'append-message':
    result = append_message(data['ticket_id'], data['role'], data['text'], db)
db.close()
print(result)

