import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, WebAppInfo
from database import init_db, add_user

TOKEN = "8517362183:AAE5NEmb2QphoprzEQMeJ3dsdloIPcV2-0k"
WEBAPP_URL = "https://your-railway-app-url.up.railway.app/index.html"

# እርስዎ የሰጡዋቸው 4ቱ ቻናሎች (ለማረጋገጫ የተዘጋጁ)
CHANNELS = [
    {"name": "Ethio Tech 011", "url": "https://t.me/ethiotech011", "id": "@ethiotech011", "forced": True},
    {"name": "Big Tech Sami", "url": "https://t.me/Big_Tech_sami", "id": "@Big_Tech_sami", "forced": True},
    {"name": "Video Best Quality", "url": "https://t.me/videobestquality", "id": "@videobestquality", "forced": True},
    {"name": "Ethio Free Inter", "url": "https://t.me/ETHIO_FREE_INTER", "id": "@ETHIO_FREE_INTER", "forced": True}
]

BOT_PROOF_CHANNEL_ID = -1003774219402

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def check_subscriptions(user_id: int) -> bool:
    for ch in CHANNELS:
        if ch["forced"]:
            try:
                member = await bot.get_chat_member(chat_id=ch["id"], user_id=user_id)
                if member.status in ["left", "kicked"]:
                    return False
            except Exception:
                pass
    return True

def get_join_keyboard():
    keyboard = []
    for ch in CHANNELS:
        if ch["forced"]:
            keyboard.append([InlineKeyboardButton(text=f"📢 {ch['name']} መቀላቀያ", url=ch["url"])])
    keyboard.append([InlineKeyboardButton(text="✅ አባል ሆጫለሁ (Verify)", callback_data="check_join")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Regl Pay Mini App ክፈት", web_app=WebAppInfo(url=WEBAPP_URL))]
    ])

@dp.message(CommandStart())
async def start_command(message: Message):
    args = message.text.split()
    referrer_id = None
    if len(args) > 1 and args[1].isdigit():
        parsed_id = int(args[1])
        if parsed_id != message.from_user.id:
            referrer_id = parsed_id

    await add_user(message.from_user.id, referrer_id)

    is_joined = await check_subscriptions(message.from_user.id)
    if not is_joined:
        await message.answer(
            "⚠️ <b>Regl Pay</b> ቦቱን ለመጠቀም መጀመሪያ ከታች ያሉትን <b>ቻናሎች</b> መቀላቀል አለብዎት!",
            reply_markup=get_join_keyboard(),
            parse_mode="HTML"
        )
        return

    await message.answer(
        f"👋 ሰላም <b>{message.from_user.first_name}</b> ወደ <b>Regl Pay</b> እንኳን በደህና መጡ!\n\n"
        "ማስታወቂያዎችን እና ታስኮችን በማየት በቀን ከፍተኛ ገቢ ማግኘት ይችላሉ። ከታች ያለውን ቁልፍ በመንካት ሚኒ አፑን ይክፈቱ፦",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )

@dp.callback_query(F.data == "check_join")
async def verify_join(callback: CallbackQuery):
    is_joined = await check_subscriptions(callback.from_user.id)
    if not is_joined:
        await callback.answer("❌ ግዴታ የሆኑትን ቻናሎች ገና አልቀላቀሉም!", show_alert=True)
        return
    
    await callback.message.edit_text(
        "🎉 እናመሰግናለን! ቻናሎቹን በተሳካ ሁኔታ ተቀላቅለዋል። አሁን ሚኒ አፑን መክፈት ይችላሉ፦",
        reply_markup=main_menu(),
        parse_mode="HTML"
    )
    await callback.answer()

async def main():
    await init_db()
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
