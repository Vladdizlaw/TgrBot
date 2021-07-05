import matplotlib.pyplot as plt
import matplotlib
import telebot
from telebot.types import LabeledPrice
print(matplotlib.get_backend())
bot = telebot.TeleBot('1790510758:AAECzPWrf0pfNl8oxLVsSxhW2Tn7fv2dThc')
FSM = 'not_active'
provider_token = '381764678:TEST:26702'

meter = [{'time':'01.01','data':29.09},{'time':'02.01','data':12.09}, {'time':'04.01','data':45.09},{'time':'06.01','data':32.09},{'time':'12.01','data':21.09},{'time':'20.01','data':21.09}]



def menu_keyboard():

    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton(
            '💳      ОПЛАТА       💳', callback_data='sales'),

    )
    keyboard.row(
        telebot.types.InlineKeyboardButton(
            '⚙️      Настройка     ⚙️', callback_data='settings')
    )
    keyboard.row(
        telebot.types.InlineKeyboardButton(
            '🔌     Показания     🔌', callback_data='meter_data'),

    )

    return keyboard


@ bot.message_handler(commands=['start'])
def startMenu(message):
    global FSM
    global meter
    #if FSM != 'not_active':
     #   return
    keyboard = menu_keyboard()
    FSM = 'menu'
    bot.send_message(message.chat.id, text=FSM,

                     reply_markup=keyboard)


@ bot.callback_query_handler(func=lambda call: True)
def getAnswer(query):

    global FSM, current_meter
    # bot.edit_message_text(chat_id=query.message.chat.id, message_id=query.message.message_id, text=query.message)
    if query.data == 'settings':
        keyboard = telebot.types.InlineKeyboardMarkup()

        keyboard.row(
            telebot.types.InlineKeyboardButton(
                'Добавить пользователя', callback_data='add_user'),
            telebot.types.InlineKeyboardButton(
                'PRO версия', callback_data='PRO')
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton(
                '🔙      Назад в меню        🔙', callback_data='menu'),

        )
        FSM = 'settings'
        bot.edit_message_text(chat_id=query.message.chat.id,
                              message_id=query.message.message_id, reply_markup=keyboard, text=FSM)

    if query.data == 'sales':
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton(
                'ОБЕЩАННЫЙ ПЛАТЕЖ', callback_data='hold_sale'),
            telebot.types.InlineKeyboardButton(
                'ОПЛАТИТЬ', callback_data='sale', pay=True),
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton(
                '🔙     Назад в меню    🔙', callback_data='menu')
        )
        FSM = 'sales'
        bot.edit_message_text(chat_id=query.message.chat.id,
                              message_id=query.message.message_id, reply_markup=keyboard, text=FSM)

    if query.data == 'meter_data':

        keyboard = telebot.types.InlineKeyboardMarkup()

        keyboard.row(
            telebot.types.InlineKeyboardButton(
                'Текущие показания', callback_data='current_data'),
            telebot.types.InlineKeyboardButton(
                'Переданные показания', callback_data='last_sent_data')
        )
        keyboard.row(
            telebot.types.InlineKeyboardButton(
                '🔙     Назад в меню     🔙', callback_data='menu')
        )
        FSM = 'meter_data'
        bot.edit_message_text(chat_id=query.message.chat.id,
                              message_id=query.message.message_id, reply_markup=keyboard, text=FSM)

    if query.data == 'menu':
        keyboard = menu_keyboard()
        FSM = 'menu'
        bot.edit_message_text(chat_id=query.message.chat.id,
                              message_id=query.message.message_id, reply_markup=keyboard, text=FSM)

    if query.data == 'sale':

        keyboard = telebot.types.InlineKeyboardMarkup()
        FSM = 'pre_sale'
        current_meter=meter[-1]['data']
        keyboard.row(
            telebot.types.InlineKeyboardButton(
                'Оплатить {0} кВт'.format(current_meter), callback_data='payment'),
            telebot.types.InlineKeyboardButton(
                '🔙     Назад в меню     🔙', callback_data='menu')
        )
        bot.edit_message_text(chat_id=query.message.chat.id,
                              message_id=query.message.message_id, reply_markup=keyboard, text=FSM)
    if query.data == 'payment':

        FSM = 'payment'
        amount = int(current_meter*300)

        prices = [LabeledPrice(label='руб', amount=amount)]
        bot.send_invoice(query.message.chat.id, title='Оплата показаний', description='Оплата {0}Квт'.format(current_meter),
                         provider_token=provider_token,
                         currency='RUB',
                         invoice_payload='payload12',
                         start_parameter='test',
                         prices=prices,

                         is_flexible=False

                         )

        @ bot.shipping_query_handler(func=lambda query: True)
        def shipping(shipping_query):
            print(shipping_query)
            bot.answer_shipping_query(
                shipping_query.id, ok=True, error_message='Error shipping')

        @ bot.pre_checkout_query_handler(func=lambda query: True)
        def shipping(checkout_query):
            bot.answer_pre_checkout_query(
                checkout_query.id, ok=True, error_message='Error precheckout')

        @ bot.message_handler(content_types=['succesful_payment'])
        def got_payment(message):
            bot.send_message(message.chat.id, 'Done {0}'.format(
                message.succesfull_payment.totla_amount))

            keyboard = telebot.types.InlineKeyboardMarkup()
            keyboard.row(
                telebot.types.InlineKeyboardButton(
                    '🔙     Назад в меню     🔙', callback_data='menu')
            )
            bot.edit_message_text(chat_id=query.message.chat.id,
                                  message_id=query.message.message_id, reply_markup=keyboard, text=FSM)
    if query.data == 'current_data':
        FSM = 'current_data'
        
        times_data=[]
        data=[]
        times_bar=[]
        for m in meter:
            data.append(m['data'])
            times_data.append(m['time'])
        for t in times_data:
            times_bar.append(int(t[0:2]))
        fig, ax = plt.subplots()
        # ax=fig.add_subplot(111)
        ax.set_title('Показания c {} по {}'.format(times_data[0],times_data[-1]))
        ax.set_xlabel('Дни')
        ax.set_ylabel('Показания счетчика,Kwt')
        ax.set(xlim=[min(times_bar), max(times_bar)])
        ax.set(ylim=[0,max(data)])
        ax.set(xticks=range(max(times_bar)))
        ax.grid()
        ax.bar(times_bar, data)
        #plt.show()
        fig.savefig('currentmonth.png')
        with open('currentmonth.png', 'rb') as photo:
            bot.send_photo(query.message.chat.id, photo)


bot.skip_pending = True
bot.polling(none_stop=True, interval=0)
