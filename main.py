import telebot
from telebot import types
import sqlite3

#Токен телеграм бота
bot = telebot.TeleBot('')

#Змінна для збереження статусу
user_states = {}

def init_db():
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

#Обробка команди старт
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("Замовити товар", callback_data="order"),
        types.InlineKeyboardButton("Консультація", callback_data="consult"),
        types.InlineKeyboardButton("Мої покупки", callback_data="my_orders")
    )
    bot.send_message(message.chat.id, "Оберіть дію:", reply_markup=markup)


#Метод для обробки викликів кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "order":
        order_menu(call.message)
    elif call.data == "consult":
        user_states[call.from_user.id] = "awaiting_consult"
        bot.send_message(call.message.chat.id, "Напишіть ваше питання для консультації:")
    elif call.data == "case":
        save_order(call.message.chat.id, "Чохол")
        bot.send_message(call.message.chat.id, "✅ Ви придбали чохол.")
    elif call.data == "charger":
        save_order(call.message.chat.id, "Зарядка")
        bot.send_message(call.message.chat.id, "✅ Ви придбали зарядку.")
    elif call.data == "my_orders":
        conn = sqlite3.connect('orders.db')
        cursor = conn.cursor()
        cursor.execute("SELECT item FROM orders WHERE user_id = ?", (call.from_user.id,))
        orders = cursor.fetchall()
        conn.close()

        if orders:
            order_list = "\n".join(f"• {item[0]}" for item in orders)
            bot.send_message(call.message.chat.id, f"Ваші покупки:\n{order_list}")
        else:
            bot.send_message(call.message.chat.id, "У вас ще немає покупок.")
    elif call.data == "back":
        start(call.message)

#Метод для відображення меню покупки
def order_menu(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("Чохол", callback_data="case"),
        types.InlineKeyboardButton("Зарядка", callback_data="charger"),
        types.InlineKeyboardButton("⬅ Назад", callback_data="back")
    )
    bot.send_message(message.chat.id, "Оберіть замовлення", reply_markup=markup)

#Метод для збереження покупки користувача
def save_order(user_id, item):
    conn = sqlite3.connect('orders.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO orders (user_id, item) VALUES (?, ?)', (user_id, item))
    conn.commit()
    conn.close()

#Метод для обробки текстових повідомлень
@bot.message_handler()
def info(message):
    user_id = message.from_user.id
    state = user_states.get(user_id)

    if state == "awaiting_consult":
        bot.send_message(message.chat.id, "Ваше питання отримано!")
        user_states.pop(user_id, None)
        start(message)
    elif message.text.lower() == "привіт":
        bot.reply_to(message, "Привіт!")

#Запуск бота
bot.polling(none_stop=True)