import sqlite3
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

bot = Bot(token='6870569497:AAGdeZx2Qdvc0SckaExEdh96Q-hLO8ik9ao')

dp = Dispatcher(bot=bot)

click_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("CLICK")]
    ], resize_keyboard=True
)

ex_coin_markup = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton('100 Notcoin🪙 to 1 Diamond💎', callback_data='exchange_bronze')
        ]
    ]
)

duplicates = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton('2x to 30 Diamonds💎', callback_data='purchase_2x')
        ],
        [
            InlineKeyboardButton('3x to 60 Diamonds💎', callback_data='purchase_3x')
        ],
        [
            InlineKeyboardButton('4x to 120 Diamonds💎', callback_data='purchase_4x')
        ],
        [
            InlineKeyboardButton('5x to 240 Diamonds💎', callback_data='purchase_5x')
        ]
    ]
)

wallet = 0
bronze_wallet = 0

conn = sqlite3.connect('bot_database.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS user_balances (
        user_id INTEGER PRIMARY KEY,
        notcoins INTEGER DEFAULT 0,
        bronze_coins INTEGER DEFAULT 0
    )
''')
conn.commit()

cursor.execute('SELECT user_id, notcoins, bronze_coins FROM user_balances')
initial_balances = cursor.fetchall()
user_balances = {user_id: (notcoins, bronze_coins) for user_id, notcoins, bronze_coins in initial_balances}


def update_user_balance(user_id, notcoins, bronze_coins):
    cursor.execute('''
        INSERT INTO user_balances (user_id, notcoins, bronze_coins)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET notcoins=?, bronze_coins=?
    ''', (user_id, notcoins, bronze_coins, notcoins, bronze_coins))
    conn.commit()


@dp.message_handler(text="/start")
async def start_func(message: types.Message):
    await message.answer(f"Hi {message.from_user.username}👋\n"
                         f"Welcome to Notcoin lite\n "
                         f"Here our commands👉 /help")


@dp.message_handler(text='/help')
async def help_func(message: types.Message):
    await message.answer('''In order to get Notcoins:
     tap to CLICK button
- To exchange your Notcoins🪙 to Diamond💎 click /exchange
- To see how many coins you have, click /wallet
- To see leaderboard click /top
- To get more information of the bot:
    Click /about
- To see upgrades click /upgrade.''', reply_markup=click_keyboard)


@dp.message_handler(text='/upgrade')
async def upgrade_abilities(message: types.Message):
    await message.answer('Now you can purchase 2x\n'
                         'Click /help to see our commands',
                         reply_markup=duplicates)


@dp.callback_query_handler(lambda c: c.data == 'purchase')
async def process_exchange(callback_query: types.CallbackQuery):
    global wallet
    if wallet >= 2:
        wallet -= 2
        await callback_query.answer("Purchased 2x multiplier! Clicks doubled.")

    else:
        await callback_query.answer("Insufficient clicks to purchase 2x multiplier.")


@dp.message_handler(text='/about')
async def about_bot(message: types.Message):
    await message.answer("Simple game-based🕹🎮 Notcoin lite🪙 bot🤖 for all👾. "
                         "Yes✅, we copied©️ a little🤏 part of Notcoin🪙 but "
                         "we`ll be pleased😇 if you enjoy the game🎉.\n"
                         "The bot🤖 created to:\n   "
                         "1️⃣ give coins🪙 by clicking👆\n   "
                         "2️⃣ compete🥇🆚🥈🆚🥉 by collecting👉 Diamonds💎\n   "
                         "3️⃣ make fun😁.\n"
                         "Developer: https://t.me/Igamberdiyev_816")


@dp.message_handler(text='CLICK')
async def click(message: types.Message):
    global user_balances
    user_id = message.from_user.id
    notcoins, bronze_coins = user_balances.get(user_id, (0, 0))
    notcoins += 1
    user_balances[user_id] = (notcoins, bronze_coins)
    update_user_balance(user_id, notcoins, bronze_coins)
    await message.answer(f'+1 Notcoin🪙')
    # await message.delete()


@dp.message_handler(text="/wallet")
async def show_wallet(message: types.Message):
    global user_balances
    user_id = message.from_user.id
    notcoins, bronze_coins = user_balances.get(user_id, (0, 0))
    await message.answer(f'You have {notcoins} Notcoin(s)🪙\n'
                         f'You have {bronze_coins} Diamond(s)💎\n'
                         f'Click /help to see our commands')


@dp.message_handler(text='/exchange')
async def exchange(message: types.Message):
    await message.answer("Now, you can exchange\n "
                         "Click /help to see our commands",
                         reply_markup=ex_coin_markup)


@dp.callback_query_handler(lambda c: c.data == 'exchange_bronze')
async def process_exchange(callback_query: types.CallbackQuery):
    global user_balances
    user_id = callback_query.from_user.id
    notcoins, bronze_coins = user_balances.get(user_id, (0, 0))
    if notcoins >= 100:
        notcoins -= 100
        bronze_coins += 1
        user_balances[user_id] = (notcoins, bronze_coins)
        update_user_balance(user_id, notcoins, bronze_coins)
        await callback_query.answer("Exchanged 100 Notcoins for 1 Diamond💎 successfully✅.")
    else:
        await callback_query.answer("You don't have enough Notcoins🪙 to exchange❌.")


@dp.message_handler(text='/top')
async def leaderboard(message: types.Message):
    cursor.execute('SELECT user_id, notcoins, bronze_coins FROM user_balances ORDER BY bronze_coins DESC')
    user_balances_sorted = cursor.fetchall()

    leaderboard_text = "🏆 Leaderboard 🏆\n"
    for index, (user_id, notcoins, bronze_coins) in enumerate(user_balances_sorted, start=1):
        user = await bot.get_chat(user_id)
        leaderboard_text += f"{index}. {user.username or user.first_name}:  {bronze_coins} Diamond(s)💎\n"
    await message.answer('Click /help to see our commands')
    await message.answer(leaderboard_text)


if __name__ == "__main__":
    executor.start_polling(dispatcher=dp, skip_updates=True)
