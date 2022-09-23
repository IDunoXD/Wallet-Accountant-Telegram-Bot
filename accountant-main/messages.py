from utils import TestStates


help_message = 'Цей бот створений для обробки фінансової інформації.\n' \
               'У випадку якщо бот не працює напишіть "/start",\n' \
               'команда перезавантажить бота без втрати даних.'
start_message = 'Виберіть функцію'
invalid_key_message = 'Ключ "{key}" не подходит.\n' + help_message
state_change_success_message = 'Текущее состояние успешно изменено'
state_reset_message = 'Состояние успешно сброшено'
current_state_message = 'Текущее состояние - "{current_state}", что удовлетворяет условию "один из {states}"'

MESSAGES = {
    'start': start_message,
    'help': help_message,
    'invalid_key': invalid_key_message,
    'state_change': state_change_success_message,
    'state_reset': state_reset_message,
    'current_state': current_state_message,
}