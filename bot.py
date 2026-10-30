import asyncio
import logging
import re
import os
import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

TOKEN = "8742096558:AAG_a7A6ZeukrG6won9xhJY4VNulT1-msg8"
WEB_APP_URL = "https://miloun-tech.github.io/max-auto/"

GROUP_CHAT_ID = "-1003919853128"
CHANNEL_ID = "-1003919853128"
CHANNEL_URL = "https://t.me/maksAutoUSA"
ADMIN_IDS = [623654677] 

INDEX_FILE_PATH = "static/index.html"
USERS_FILE = "users.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()
SAVED_LEADS = []       

def save_user(user_id):
    users = []
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                users = json.load(f)
        except:
            pass
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

def get_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return []

class OrderQuiz(StatesGroup):
    budget = State()
    brand = State()
    fuel = State()
    phone = State()

class AdminState(StatesGroup):
    waiting_for_broadcast = State()

def get_main_keyboard(is_admin=False):
    builder = ReplyKeyboardBuilder()
    builder.button(text="🎯 Підібрати авто")
    builder.button(text="🚗 Каталог авто")
    builder.button(text="🧮 Калькулятор")
    builder.button(text="📍 Відстежити авто")
    builder.button(text="📞 Наші контакти")
    builder.button(text="⭐️ Відгуки / FAQ")
    if is_admin:
        builder.button(text="👑 Адмін-панель")
        builder.adjust(1, 2, 2, 1, 1)
    else:
        builder.adjust(1, 2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

async def check_subscription(user_id: int) -> bool:
    if user_id in ADMIN_IDS: return True
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return True 

@dp.message(Command("start"), F.chat.type == "private")
async def start_cmd(message: types.Message, state: FSMContext):
    await state.clear()
    save_user(message.from_user.id)
    is_admin = message.from_user.id in ADMIN_IDS
    await message.answer(
        f"🇺🇸 **Вітаємо в Max Auto, {message.from_user.first_name}!**\n\n"
        "Ми доставляємо перевірені автомобілі з США, Кореї та Європи під ключ.\n\n"
        "Оберіть дію в меню нижче 👇",
        parse_mode="Markdown", reply_markup=get_main_keyboard(is_admin)
    )

@dp.message(F.text == "🚗 Каталог авто", F.chat.type == "private")
async def menu_catalog(message: types.Message):
    save_user(message.from_user.id)
    b = InlineKeyboardBuilder().button(text="🚘 Відкрити каталог", web_app=types.WebAppInfo(url=WEB_APP_URL))
    await message.answer("🚘 **Наш актуальний каталог автомобілів:**", reply_markup=b.as_markup())

@dp.message(F.text == "🧮 Калькулятор", F.chat.type == "private")
async def menu_calculator(message: types.Message):
    b = InlineKeyboardBuilder().button(text="🧮 Відкрити калькулятор", web_app=types.WebAppInfo(url=f"{WEB_APP_URL}?tab=calc"))
    await message.answer("🧮 **Розрахунок вартості та вигоди:**", reply_markup=b.as_markup())

@dp.message(F.text == "📍 Відстежити авто", F.chat.type == "private")
async def menu_tracking(message: types.Message):
    b = InlineKeyboardBuilder().button(text="📍 Трекінг по VIN", web_app=types.WebAppInfo(url=f"{WEB_APP_URL}?tab=tracking"))
    await message.answer("📍 **Відстежуйте доставку в реальному часі:**", reply_markup=b.as_markup())

@dp.message(F.text == "📞 Наші контакти", F.chat.type == "private")
async def menu_contacts(message: types.Message):
    b = InlineKeyboardBuilder()
    b.button(text="📸 Наш Instagram", url="https://www.instagram.com/maks_auto_ua")
    b.button(text="💬 Написати в Telegram", url="https://t.me/Maksim_Lonk")
    b.adjust(1)
    await message.answer("📞 **Контакти Max Auto**\n\n🗽 +380 95 365 66 01\n🗽 +380 67 191 19 65", reply_markup=b.as_markup())

@dp.message(F.text == "⭐️ Відгуки / FAQ", F.chat.type == "private")
async def menu_reviews_faq(message: types.Message):
    b = InlineKeyboardBuilder()
    b.button(text="📸 Наш Instagram (Відгуки)", url="https://www.instagram.com/maks_auto_ua")
    b.button(text="💬 Написати нам в Telegram", url="https://t.me/Maksim_Lonk")
    b.adjust(1)
    await message.answer("⭐️ **Відгуки та FAQ**\n\nПонад 500+ задоволених клієнтів по всій Україні!", reply_markup=b.as_markup())

@dp.message(F.text == "🎯 Підібрати авто", F.chat.type == "private")
async def start_quiz_trigger(message: types.Message, state: FSMContext):
    save_user(message.from_user.id)
    if not await check_subscription(message.from_user.id):
        b = InlineKeyboardBuilder()
        b.button(text="📢 Підписатися на канал", url=CHANNEL_URL)
        b.button(text="✅ Я підписався", callback_data="check_sub_done")
        b.adjust(1)
        await message.answer("⚠️ Щоб отримати індивідуальний підбір, підпишіться на наш офіційний канал:", reply_markup=b.as_markup())
        return
    b = InlineKeyboardBuilder()
    b.button(text="До $10,000", callback_data="bq_10k")
    b.button(text="$10,000 - $15,000", callback_data="bq_15k")
    b.button(text="$15,000 - $25,000", callback_data="bq_25k")
    b.button(text="Понад $25,000", callback_data="bq_max")
    b.adjust(1)
    await message.answer("Крок 1/4: 💰 Який бюджет розглядаєте?", reply_markup=b.as_markup())
    await state.set_state(OrderQuiz.budget)

@dp.callback_query(F.data == "check_sub_done")
async def verify_sub_callback(callback: types.CallbackQuery, state: FSMContext):
    if await check_subscription(callback.from_user.id):
        await callback.message.delete()
        b = InlineKeyboardBuilder()
        b.button(text="До $10,000", callback_data="bq_10k")
        b.button(text="$10,000 - $15,000", callback_data="bq_15k")
        b.button(text="$15,000 - $25,000", callback_data="bq_25k")
        b.button(text="Понад $25,000", callback_data="bq_max")
        b.adjust(1)
        await callback.message.answer("Крок 1/4: 💰 Який бюджет розглядаєте?", reply_markup=b.as_markup())
        await state.set_state(OrderQuiz.budget)
    else:
        await callback.answer("❌ Ви ще не підписалися!", show_alert=True)

@dp.callback_query(OrderQuiz.budget)
async def q_brand(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(budget=callback.data)
    b = InlineKeyboardBuilder()
    brands = [
        "Acura", "Audi", "BMW", "Chevrolet", "Dodge", 
        "Ford", "Honda", "Hyundai", "Jeep", "Kia", 
        "Lexus", "Mazda", "Mercedes", "Mitsubishi", "Nissan", 
        "Peugeot", "Porsche", "Renault", "Skoda", "Subaru", 
        "Tesla", "Toyota", "Volkswagen", "Volvo", "Інша"
    ]
    for brand in brands:
        b.button(text=brand, callback_data=f"br_{brand.lower()}")
    b.adjust(3) 
    await callback.message.edit_text("Крок 2/4: 🚘 Оберіть бажану марку авто:", reply_markup=b.as_markup())
    await state.set_state(OrderQuiz.brand)

@dp.callback_query(OrderQuiz.brand)
async def q_fuel(callback: types.CallbackQuery, state: FSMContext):
    selected_brand = callback.data.replace("br_", "")
    await state.update_data(brand=selected_brand)
    b = InlineKeyboardBuilder()
    b.button(text="Бензин", callback_data="fl_бензин")
    b.button(text="Дизель", callback_data="fl_дизель")
    b.button(text="Газ (LPG/LPI)", callback_data="fl_газ")
    b.button(text="Електро / Гібрид", callback_data="fl_електро")
    b.adjust(2)
    await callback.message.edit_text(f"Марка: {selected_brand.capitalize()}\nКрок 3/4: ⛽️ Який тип палива вас цікавить?", reply_markup=b.as_markup())
    await state.set_state(OrderQuiz.fuel)

@dp.callback_query(OrderQuiz.fuel)
async def q_phone(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(fuel=callback.data.replace("fl_", ""))
    b = ReplyKeyboardBuilder().button(text="📱 Надіслати номер", request_contact=True)
    await callback.message.delete()
    await callback.message.answer(
        "Крок 4/4: 📞 Натисніть кнопку нижче, щоб поділитися номером.", 
        reply_markup=b.as_markup(resize_keyboard=True, one_time_keyboard=True)
    )
    await state.set_state(OrderQuiz.phone)

@dp.message(OrderQuiz.phone, F.contact, F.chat.type == "private")
async def process_phone(message: types.Message, state: FSMContext):
    data = await state.get_data()
    lead_info = {
        "user_id": message.from_user.id,
        "name": message.from_user.full_name,
        "username": message.from_user.username,
        "brand": data.get('brand'),
        "fuel": data.get('fuel'),
        "phone": message.contact.phone_number
    }
    SAVED_LEADS.append(lead_info)
    save_user(message.from_user.id)
    is_admin = message.from_user.id in ADMIN_IDS
    await message.answer(
        "✅ **Заявку верифіковано!**\nМаксим вже переглядає лоти.", 
        parse_mode="Markdown", 
        reply_markup=get_main_keyboard(is_admin)
    )
    await state.clear()
    print(f"✅ Новий лід: {message.from_user.full_name} ({message.contact.phone_number}) | Запит: {data.get('brand')}, {data.get('fuel')}")

@dp.message(F.chat.id == int(GROUP_CHAT_ID))
async def catch_group_post_and_match(message: types.Message):
    if not message.photo or not message.caption:
        return
    
    caption = message.caption
    text_lower = caption.lower()
    
    if "рік" not in text_lower and "ціна" not in text_lower and "двигун" not in text_lower:
        return

    category = "usa"
    target_list_id = "list-usa"
    status_class = "status-usa"
    status_text = "США / Аукціон"

    if any(w in text_lower for w in ["коре", "європ", "китай", "німеччин"]):
        target_list_id = "list-other"
        status_class = "status-other"
        status_text = "Корея / Європа"
    elif any(w in text_lower for w in ["україн", "розмитнен", "в наявності", "на номерах"]):
        target_list_id = "list-ukraine"
        status_class = "status-ua"
        status_text = "В Україні"

    lines = caption.split('\n')
    car_title = lines[0] if lines[0].strip() else "Автомобіль Max Auto"
    
    price_match = re.search(r'ціна[^\d]*(\d{1,3}(?:[\s\.,]?\d{3})+)', text_lower)
    if not price_match:
        price_match = re.search(r'(\d{1,3}(?:[\s\.,]\d{3})*)\s*(?:\$|usd|долар|💵|💶)', text_lower)
        
    if price_match:
        car_price_str = re.sub(r'\D', '', price_match.group(1))
        price_val = int(car_price_str)
        car_price_display = f"$ {price_val:,}".replace(",", " ")
    else:
        price_val = 20000
        car_price_display = "$ 20 000"

    # Парсинг марки для фільтрації в HTML
    brands_list = ["acura", "audi", "bmw", "chevrolet", "dodge", "ford", "honda", "hyundai", "jeep", "kia", "lexus", "mazda", "mercedes", "mitsubishi", "nissan", "peugeot", "porsche", "renault", "skoda", "subaru", "tesla", "toyota", "volkswagen", "volvo"]
    brand_attr = "other"
    for b in brands_list:
        if b in text_lower:
            brand_attr = b
            break

    clean_id = str(GROUP_CHAT_ID).replace("-100", "")
    post_link = f"https://t.me/c/{clean_id}/{message.message_id}"

    new_card_html = f"""
            <div class="car-item" data-price="{price_val}" data-brand="{brand_attr}">
                <div class="car-title">{car_title}</div>
                <div class="car-specs">{caption[:80]}...</div>
                <div class="car-price-tag">{car_price_display}</div><span class="car-status {status_class}">{status_text}</span>
                <div style="display: flex; gap: 8px; margin-top: 10px;">
                    <button class="btn-primary" style="margin-top:0; flex:1;" onclick="orderCar('{car_title}')">Залишити заявку</button>
                    <a href="{post_link}" target="_blank" class="btn-primary" style="margin-top:0; flex:1; text-align:center; text-decoration:none; background: linear-gradient(135deg, #2563eb, #1d4ed8); display:flex; align-items:center; justify-content:center; font-size: 14px;">📸 Фото/Пост</a>
                </div>
            </div>"""

    if not os.path.exists(INDEX_FILE_PATH):
        print(f"❌ Помилка: Файл {INDEX_FILE_PATH} не знайдено.")
        return

    try:
        with open(INDEX_FILE_PATH, "r", encoding="utf-8") as f:
            html_content = f.read()
        
        target_marker = f'<div id="{target_list_id}" class="car-list'
        if target_marker in html_content:
            parts = html_content.split(target_marker)
            insert_pos = parts[1].find('>') + 1
            updated_html = parts[0] + target_marker + parts[1][:insert_pos] + new_card_html + parts[1][insert_pos:]
            
            with open(INDEX_FILE_PATH, "w", encoding="utf-8") as f:
                f.write(updated_html)
            print(f"✅ Додано нове авто: '{car_title}' (Ціна: {car_price_display}, Марка: {brand_attr})")
    except Exception as e:
        print(f"❌ Помилка оновлення HTML: {e}")

    # ДОДАНО КНОПКУ ДЛЯ РОЗСИЛКИ
    btn_details = InlineKeyboardBuilder().button(text="👀 Детальніше (Пост)", url=post_link).as_markup()

    for lead in SAVED_LEADS:
        brand_pref = str(lead.get('brand', '')).lower()
        fuel_pref = str(lead.get('fuel', '')).lower()
        
        brand_match = brand_pref != "other" and brand_pref in text_lower
        fuel_match = False
        
        if "електро" in fuel_pref and any(w in text_lower for w in ["електро", "ev", "гібрид"]): 
            fuel_match = True
        elif "дизель" in fuel_pref and "дизель" in text_lower:
            fuel_match = True
        elif "газ" in fuel_pref and any(w in text_lower for w in ["газ", "lpi", "lpg"]):
            fuel_match = True
        elif "бензин" in fuel_pref and "бензин" in text_lower:
            fuel_match = True
            
        try:
            if brand_match and fuel_match:
                await bot.send_message(lead['user_id'], f"🎯 **Ідеальний збіг!** {brand_pref.capitalize()} на потрібному паливі:")
            elif brand_match:
                await bot.send_message(lead['user_id'], f"🚘 **Знайшли {brand_pref.capitalize()}**, можливо вас зацікавить (інше паливо):")
            elif fuel_match:
                await bot.send_message(lead['user_id'], f"⚡️ **Авто з бажаним типом палива ({fuel_pref})**, але іншої марки:")
            else:
                await bot.send_message(lead['user_id'], "💡 **Нова пропозиція в каталозі:**")
                
            await message.copy_to(chat_id=lead['user_id'], reply_markup=btn_details)
            await asyncio.sleep(0.1)
        except Exception:
            pass

@dp.message(F.text == "👑 Адмін-панель", F.chat.type == "private")
async def admin_panel(message: types.Message):
    if message.from_user.id not in ADMIN_IDS: return
    b = InlineKeyboardBuilder()
    b.button(text="📊 Переглянути ліди", callback_data="admin_leads")
    b.button(text="📢 Довільна розсилка", callback_data="admin_broadcast")
    b.adjust(1)
    await message.answer("👑 **Адмін-панель**", reply_markup=b.as_markup())

@dp.callback_query(F.data == "admin_leads")
async def admin_show_leads(callback: types.CallbackQuery):
    if callback.from_user.id not in ADMIN_IDS: return
    if not SAVED_LEADS:
        await callback.message.answer("📭 Заявок у поточній сесії немає.")
    else:
        text = f"📋 **База лідів:**\n\n"
        for i, lead in enumerate(SAVED_LEADS[-10:], 1):
            text += f"{i}. {lead['name']} | 🚗 {lead['brand']} | 📞 {lead['phone']}\n"
        await callback.message.answer(text)
    await callback.answer()

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast_start(callback: types.CallbackQuery, state: FSMContext):
    if callback.from_user.id not in ADMIN_IDS: return
    users_count = len(get_users())
    await callback.message.answer(f"📢 Надішліть повідомлення для розсилки.\nДоступно клієнтів у базі: {users_count}\n('відміна' для скасування)")
    await state.set_state(AdminState.waiting_for_broadcast)
    await callback.answer()

@dp.message(AdminState.waiting_for_broadcast, F.chat.type == "private")
async def admin_broadcast_send(message: types.Message, state: FSMContext):
    if message.text and message.text.lower() == 'відміна':
        await message.answer("❌ Скасовано.", reply_markup=get_main_keyboard(True))
        await state.clear()
        return
    success_count = 0
    all_users = get_users()
    for user_id in all_users:
        try:
            await message.copy_to(chat_id=user_id)
            success_count += 1
            await asyncio.sleep(0.05)
        except:
            pass 
    await message.answer(f"✅ Успішно розіслано: {success_count} користувачам.", reply_markup=get_main_keyboard(True))
    await state.clear()
    print(f"✅ Розсилка завершена. Охоплено {success_count} осіб.")

@dp.message(F.chat.type == "private")
async def fallback_to_start(message: types.Message, state: FSMContext):
    await state.clear()
    save_user(message.from_user.id)
    is_admin = message.from_user.id in ADMIN_IDS
    await message.answer("Головне меню Max Auto 👇", reply_markup=get_main_keyboard(is_admin))

async def main():
    logging.basicConfig(level=logging.ERROR)
    print("🚀 Бот Max Auto успішно запущено!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())