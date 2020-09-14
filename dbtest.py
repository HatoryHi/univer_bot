import telebot
import config
import mysql.connector

from telebot import types

conn = mysql.connector.connect(
    user=config.USER, password=config.PASS, host=config.HOST, database=config.DB)
cursor = conn.cursor()

phone_number = ''
name = ''
surname = ''
group = ''
course = ''

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=["start"])
def welcome(message):
    # keyboard
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    reg = types.KeyboardButton("регистрация")
    auth = types.KeyboardButton("аутентификация")
    markup.add(reg, auth)
    bot.send_message(message.chat.id, ' Добро пожаловать,' + str(message.from_user.username), reply_markup=markup)
    bot.register_next_step_handler(message, phone)


@bot.message_handler(commands=["start"])
def phone(message):
    global phone_number, name, surname, group, course, crit
    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    button_phone = types.KeyboardButton(text="Отправить номер телефона", request_contact=True)
    keyboard.add(button_phone)
    bot.send_message(message.chat.id, "Отправь мне свой номер телефона ", reply_markup=keyboard)
    if message.text == 'регистрация':
        bot.register_next_step_handler(message, my_group)

    elif message.text == 'аутентификация':
        bot.register_next_step_handler(message, sel)


def sel(number):
    num = number.contact.phone_number
    try:
        with conn.cursor() as cursor:
            # SQL
            sql = "SELECT * FROM user WHERE student_phone_number = %s"
            # Выполнить команду запроса (Execute Query).
            cursor.execute(sql, (num,))

            for row in cursor:
                # bot.send_message(number.chat.id, row[], reply_markup=None)

                print(row['id'])
    except Exception as e:
        print(e)
        conn.close()


def my_group(message):
    global phone_number
    phone_number = message.contact.phone_number
    print(phone_number)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    ks = types.KeyboardButton(text="КС")
    kb = types.KeyboardButton(text="КБ")
    ky = types.KeyboardButton(text="КУ")
    ki = types.KeyboardButton(text="КИ")
    keyboard.add(ks, kb, ky, ki)
    bot.send_message(message.chat.id, "Выберите вашу группу: ", reply_markup=keyboard)
    bot.register_next_step_handler(message, my_course)


def my_course(message):
    global group
    group = message.text
    print(group)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    first = types.KeyboardButton(text="1")
    second = types.KeyboardButton(text="2")
    three = types.KeyboardButton(text="3")
    four = types.KeyboardButton(text="4")
    keyboard.add(first, second, three, four)
    bot.send_message(message.chat.id, "Выберите вашу курс: ", reply_markup=keyboard)
    bot.register_next_step_handler(message, reg_name)


def reg_name(message):
    global course
    try:
        course = int(message.text)
        print(course)
        bot.send_message(message.from_user.id, 'Какая у вас фамилия?')
        bot.register_next_step_handler(message, reg_surname)
    except Exception as e:
        bot.send_message(message.from_user.id, 'Вводите цифрами')
        my_course(message)


def reg_surname(message):
    global name
    name = message.text
    print(name)
    bot.send_message(message.from_user.id, 'Ваше имя?')
    bot.register_next_step_handler(message, reg_all)


def reg_all(message):
    global surname
    surname = message.text
    print(surname)

    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='нет', callback_data='no')
    keyboard.add(key_no)
    question = ' Фамилия - ' + surname + ' , ' + 'имя - ' + name + ' , ' + ' группа -  ' + group + ' , ' + ' курс -  ' + str(
        course) + ',' + 'все ' \
                        'верно ' + '? '
    bot.send_message(message.from_user.id, text=question, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'yes':
        insert_stmt = (
            'INSERT INTO user(student_phone_number, student_group, student_course, student_surname,student_name)'
            'VALUES (%s, %s, %s, %s, %s)'
        )
        data = (str(phone_number), str(group), str(course), str(surname), str(name))

        try:
            cursor.execute(insert_stmt, data)
            conn.commit()
            print(data)
        except Exception as e:
            print(e)
            print(data)
            conn.rollback()
            conn.close()
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Регистрация успешна!')
        next_step(call.message)
    # bot.send_message(call.message.chat.id, 'Регистрация успешна!')
    elif call.data == 'no':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text='Попробуем еще раз!')
        phone(call.message)


#  кусок выше больше не трогать блт

def next_step(message):
    new_keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    scheldure = types.KeyboardButton(text="расписание")
    new_keyboard.add(scheldure)
    bot.send_message(message.chat.id, " Что хотите сделать?  ", reply_markup=new_keyboard)
    bot.register_next_step_handler(message, scheldure_buttons)


def scheldure_buttons(message):
    keys = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    pn = types.KeyboardButton(text='понедельник')
    vt = types.KeyboardButton(text='вторник')
    sr = types.KeyboardButton(text='среда')
    ch = types.KeyboardButton(text='четверг')
    pt = types.KeyboardButton(text='пятница')
    keys.add(pn, vt, sr, ch, pt)
    bot.send_message(message.chat.id, 'Какой день?', reply_markup=keys)
    bot.register_next_step_handler(message, pon)


def pon(message):
    if message.text == 'понедельник':
        photo = open('./scheldure/pn.png', 'rb')
        bot.send_photo(message.chat.id, photo)
        next_step(message)
    elif message.text == 'вторник':
        photo = open('./scheldure/vt.png', 'rb')
        bot.send_photo(message.chat.id, photo)
        next_step(message)


bot.polling(none_stop=True)
