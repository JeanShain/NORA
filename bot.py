import asyncio
import uuid
import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from db import add_album, add_song, get_songs_by_album, get_song, get_random_songs
from databaseUser import add_user, get_user_role, set_role, get_user_id_by_username
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TOKEN")
bot = Bot(token=TOKEN)
dp = Dispatcher()
bot_active = {}


# ===== USER ROLES ======================
ROLE_ADMIN = "admin"
ROLE_VIP = "vip"
ROLE_USER = "user"


def get_user_role_local(message: types.Message):
    return get_user_role(message.from_user.id)

@dp.message(Command("authorization"))
async def authorization(message: types.Message):
    username = message.from_user.username

    role = get_user_role(message.from_user.id)

    await message.answer(
        f"👤: @{username}\n"
        f"🔐: {role.upper()}"
    )

# add admin
@dp.message(Command("add_admin"))
async def add_admin(message: types.Message):
    if get_user_role(message.from_user.id) != ROLE_ADMIN:
        return await message.answer("🔐You don't have permission!")

    try:
        username = message.text.split()[1].replace("@", "").lower()
    except:
        return await message.answer("Format: /add_admin username")

    user_id = get_user_id_by_username(username)

    if not user_id:
        return await message.answer("❗User don't exist!")


    set_role(user_id, ROLE_ADMIN)

    await message.answer("User successfully added to admin!")

# add vip
@dp.message(Command("add_vip"))
async def add_vip(message: types.Message):
    if get_user_role(message.from_user.id) != ROLE_ADMIN:
        return await message.answer("🔐You don't have permission!")

    try:
        username = message.text.split()[1].replace("@", "").lower()
    except:
        return await message.answer("Format: /add_vip username")

    user_id = get_user_id_by_username(username)

    if not user_id:
        return await message.answer("❗User don't exist!")

    set_role(user_id, ROLE_VIP)

    await message.answer("User successfully added to vip!")
# =======================================


# ===== DLT MSG =========================
user_messages = {}


def save_message(chat_id, message_id, msg_type="content"):
    if chat_id not in user_messages:
        user_messages[chat_id] = []

    user_messages[chat_id].append((message_id, msg_type))

async def clear_chat(chat_id):
    if chat_id in user_messages:
        new_list = []

        for msg_id, msg_type in user_messages[chat_id]:
            if msg_type == "content":
                try:
                    await bot.delete_message(chat_id, msg_id)
                except:
                    pass
            else:
                new_list.append((msg_id, msg_type))

        user_messages[chat_id] = new_list

async def clear_all_chat(chat_id):
    if chat_id in user_messages:
        for msg_id, msg_type in user_messages[chat_id]:
            try:
                await bot.delete_message(chat_id, msg_id)
            except:
                pass

        user_messages[chat_id] = []
# =======================================


class AddSong(StatesGroup):
    waiting_for_album = State()


# ===== ALBUM IMG ======================
ALBUM_COVERS = {
    "live": "AgACAgIAAxkBAAMGadUmT9AVcWkCa9ueESiyD8xXVjsAAi0YaxuXGalKb_-7oHfe5JQBAAMCAAN5AAM7BA",
    "acoustic": "AgACAgIAAxkBAAMIadUmY7PE_rp2ygwT4MhvtSDx6FIAAi4YaxuXGalK0IH7TYwjk_sBAAMCAAN5AAM7BA",
    "deluxe": "AgACAgIAAxkBAAMKadUmdkbV53q5IrwXYBhteNgeJUUAAi8YaxuXGalKPgjw5A3GFf0BAAMCAAN5AAM7BA",
    "night22": "AgACAgIAAxkBAAMMadUmiVXvAT18rfmyeCixUzHlhb0AAjAYaxuXGalKQOm2Ft7qLjABAAMCAAN5AAM7BA",
}
# =======================================


# ===== MENU ============================
def main_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="ALBUMS")],
            [KeyboardButton(text="SECRETROOM")],
            [KeyboardButton(text="STOP")]
        ],
        resize_keyboard=True
    )
    return keyboard
# =======================================


# ===== START ===========================
@dp.message(Command('start'))
async def start(message: types.Message):
    add_user(
        message.from_user.id,
        message.from_user.username or ""
    )
    chat_id = message.chat.id
    bot_active[chat_id] = True
    await clear_chat(chat_id)

    msg = await message.answer_animation(
        animation="CgACAgIAAxkBAAICYmnVb-mh46YZBbMBFjRMaTatSwABowACdJ4AApcZqUrtcCLcU_VvkTsE",
        caption=(
            "YO!\n"
            "Вітаємо в NORA —— місце де можна легко слухати найновіші переклади від ALFA MUSIC.\n\n"
            "ALBUMS ——> готові альбоми;\n"
            "SECRETROOM ——> згенеруй свій власний;\n\n"
            "<i>//NORA\n//No Official Release Alfa</i>"
        ),
        parse_mode='HTML',
        reply_markup=main_menu()
    )
    save_message(chat_id, msg.message_id, 'menu')

@dp.message(lambda message: message.text == "START")
async def start_bot(message: types.Message):
    save_message(message.chat.id, message.message_id, "user")
    chat_id = message.chat.id
    bot_active[chat_id] = True

    await clear_chat(chat_id)

    msg = await message.answer_animation(
        animation='CgACAgIAAxkBAAICYmnVb-mh46YZBbMBFjRMaTatSwABowACdJ4AApcZqUrtcCLcU_VvkTsE',
        caption=('Welcome, again!\n\n\n'
                 'ALBUMS ——> готові альбоми;\n'
                 'SECRETROOM ——> згенеруй свій власний;\n\n'
                 '<i>//NORA\n//No Official Release Alfa</i>'),
        parse_mode='HTML',
        reply_markup=main_menu()
    )
    save_message(chat_id, msg.message_id, 'menu')
# =======================================


# ===== STOP ============================
def stopped_menu():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="START")]
        ],
        resize_keyboard=True
    )
    return keyboard

@dp.message(lambda message: message.text == "STOP")
async def stop_bot(message: types.Message):
    save_message(message.chat.id, message.message_id, "user")
    chat_id = message.chat.id
    bot_active[chat_id] = False

    await clear_all_chat(chat_id)

    msg = await message.answer(
        "Press START",
        reply_markup=stopped_menu()
    )

    save_message(chat_id, msg.message_id, 'menu')
# =======================================

# ===== ALBUM ===========================
@dp.message(lambda message: message.text == "ALBUMS")
async def albums_button(message: types.Message):
    save_message(message.chat.id, message.message_id, "user")
    if not bot_active.get(message.chat.id, True):
        return
    await clear_chat(message.chat.id)
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='📀LIVE', callback_data="album_live")],
        [InlineKeyboardButton(text='📀ACOUSTIC', callback_data="album_acoustic")],
        [InlineKeyboardButton(text='📀DELUXE', callback_data="album_deluxe")],
        [InlineKeyboardButton(text='📀THE NIGHT\'22', callback_data="album_night22")],
        [InlineKeyboardButton(text='🔐NOR', callback_data="album_nor")]
    ])

    msg = await message.answer_photo(
        photo='AgACAgIAAxkBAAICWmnVasLpJHQAAeLmSMjlrjFpdR_UQgACpBlrG5cZqUrW1T_U11gDJAEAAwIAA3gAAzsE',
        caption=(
            "Обери альбомну збірку, де:\n\n"
        "📀 Live               —> UA;\n"
        "📀 Acoustic       —> Acoustic mix;\n"
        "📀 Deluxe          —> RU;\n"
        "📀 TheNight'22 —> 2022;\n"
        "🔐 NOR               —> only for VIP;"
        ),
        reply_markup=keyboard)
    save_message(message.chat.id, msg.message_id)


@dp.callback_query(lambda c: c.data.startswith("album_"))
async def handle_album(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    role = get_user_role(user_id)
    data = callback.data
    chat_id = callback.message.chat.id

    if data == "album_nor" and role not in [ROLE_ADMIN, ROLE_VIP]:
        return await callback.answer("🔐Only for VIP", show_alert=True)

    await clear_chat(chat_id)

    if data == "album_live":
        songs = get_songs_by_album("live")

        msg = await callback.message.answer_photo(
            photo="AgACAgIAAxkBAAMGadUmT9AVcWkCa9ueESiyD8xXVjsAAi0YaxuXGalKb_-7oHfe5JQBAAMCAAN5AAM7BA",
            caption=(
                "<b>                                 LIVE</b>\n"
                "<i>                    ◀︎ ALFA MUSIC ▶︎</i>\n\n\n"
                "✳︎━━━━━━TRACKLIST━━━━━━✳︎"
            ),
            parse_mode="HTML",
        )
        save_message(chat_id, msg.message_id)

        for song_id, title, file_id in songs:
            msg = await callback.message.answer_audio(audio=file_id, title=title)
            save_message(chat_id, msg.message_id, 'content')

    elif data == "album_acoustic":
        songs = get_songs_by_album("acoustic")

        msg = await callback.message.answer_photo(
            photo="AgACAgIAAxkBAAMIadUmY7PE_rp2ygwT4MhvtSDx6FIAAi4YaxuXGalK0IH7TYwjk_sBAAMCAAN5AAM7BA",
            caption=(
                "<b>                           ACOUSTIC</b>\n"
                "<i>                    ◀︎ ALFA MUSIC ▶︎</i>\n\n\n"
                "✳︎━━━━━━TRACKLIST━━━━━━✳︎"
            ),
            parse_mode="HTML",
        )
        save_message(chat_id, msg.message_id)

        for song_id, title, file_id in songs:
            msg = await callback.message.answer_audio(audio=file_id, title=title)
            save_message(chat_id, msg.message_id, 'content')

    elif data == "album_deluxe":
        songs = get_songs_by_album("deluxe")

        msg = await callback.message.answer_photo(
            photo="AgACAgIAAxkBAAMKadUmdkbV53q5IrwXYBhteNgeJUUAAi8YaxuXGalKPgjw5A3GFf0BAAMCAAN5AAM7BA",
            caption=(
                "<b>                             DELUXE</b>\n"
                "<i>                    ◀︎ ALFA MUSIC ▶︎</i>\n\n\n"
                "✳︎━━━━━━TRACKLIST━━━━━━✳︎"
            ),
            parse_mode="HTML",
        )
        save_message(chat_id, msg.message_id)

        for song_id, title, file_id in songs:
            msg = await callback.message.answer_audio(audio=file_id, title=title)
            save_message(chat_id, msg.message_id, 'content')

    elif data == "album_night22":
        songs = get_songs_by_album("night22")

        msg = await callback.message.answer_photo(
            photo="AgACAgIAAxkBAAMMadUmiVXvAT18rfmyeCixUzHlhb0AAjAYaxuXGalKQOm2Ft7qLjABAAMCAAN5AAM7BA",
            caption=(
                "<b>                       THE NIGHT'22</b>\n"
                "<i>                    ◀︎ ALFA MUSIC ▶︎</i>\n\n\n"
                "✳︎━━━━━━TRACKLIST━━━━━━✳︎"
            ),
            parse_mode="HTML",
        )
        save_message(chat_id, msg.message_id)

        for song_id, title, file_id in songs:
            msg = await callback.message.answer_audio(audio=file_id, title=title)
            save_message(chat_id, msg.message_id, 'content')

    elif data == "album_nor":
        songs = get_songs_by_album("nor")

        msg = await callback.message.answer_photo(
            photo="AgACAgIAAxkBAAIDJmnWKQE6qAR-AS5EDSVJLuUwT4s4AAJ0FmsbJJexSgH742aoKVBeAQADAgADeQADOwQ",
            caption=(
                "<b>                                NOR</b>\n"
                "<i>                    ◀︎ ALFA MUSIC ▶︎</i>\n\n\n"
                "✳︎━━━━━━TRACKLIST━━━━━━✳︎"
            ),
            parse_mode="HTML",
        )
        save_message(chat_id, msg.message_id)

        for song_id, title, file_id in songs:
            msg = await callback.message.answer_audio(audio=file_id, title=title)
            save_message(chat_id, msg.message_id, 'content')

    await callback.answer()
# =======================================


# ===== SECRETROOM ======================
@dp.message(lambda message: message.text == "SECRETROOM")
async def random_playlist(message: types.Message):
    save_message(message.chat.id, message.message_id, "user")
    if not bot_active.get(message.chat.id, True):
        return
    chat_id = message.chat.id
    await clear_chat(chat_id)

    songs = get_random_songs(20)
    msg = await message.answer_photo(
        photo="AgACAgIAAxkBAAICCGnVZJ9kgPXJcEc64c5UxldvxC86AAJ9GWsblxmpSr0IwTMgp8DKAQADAgADeQADOwQ",
        caption=(
            "<b>                      SECRETROOM</b>\n"
            "<i>                         ◀︎ NORA ▶︎</i>\n\n\n"
            "✳︎━━━━━━TRACKLIST━━━━━━✳︎"
        ),
        parse_mode="HTML",
    )

    save_message(chat_id, msg.message_id, "content")

    for song_id, title, file_id in songs:
        song = get_song(song_id)

        if song:
            title, file_id, thumbnail = song

            msg = await message.answer_audio(
                audio=file_id,
                title=title
            )
            save_message(chat_id, msg.message_id, "content")
# =======================================


# ===== ADD =============================
@dp.message(lambda message: message.audio)
async def add_song_start(message: types.Message, state: FSMContext):
    if not bot_active.get(message.chat.id, True):
        return
    if get_user_role(message.from_user.id) != ROLE_ADMIN:
        await message.answer("🔐You don't have permission, only admin can add songs")
        try:
            await message.delete()
        except:
            pass
        return

    await clear_chat(message.chat.id)
    await state.update_data(
        file_id=message.audio.file_id,
        title=message.audio.title or "Без назви"
    )

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="LIVE", callback_data="add_live")],
        [InlineKeyboardButton(text="ACOUSTIC", callback_data="add_acoustic")],
        [InlineKeyboardButton(text="DELUXE", callback_data="add_deluxe")],
        [InlineKeyboardButton(text="THE NIGHT'22", callback_data="add_night22")]
    ])

    msg = await message.answer("📀 Обери альбом:", reply_markup=keyboard)
    save_message(message.chat.id, msg.message_id)
    await state.set_state(AddSong.waiting_for_album)


@dp.callback_query(lambda c: c.data.startswith("add_"))
async def choose_album(callback: types.CallbackQuery, state: FSMContext):
    album_id = callback.data.split("_")[1]

    data = await state.get_data()

    file_id = data["file_id"]
    title = data["title"]

    thumbnail = ALBUM_COVERS.get(album_id)

    song_id = str(uuid.uuid4())

    add_song(song_id, title, file_id, album_id, thumbnail)

    await callback.message.answer("Done!")

    await state.clear()
    await callback.answer()


@dp.message(lambda message: message.audio or message.photo or message.video or message.animation)
async def get_file_id(message: types.Message):
    if not bot_active.get(message.chat.id, True):
        return
    if get_user_role(message.from_user.id) != ROLE_ADMIN:
        await message.answer("🔐You don't have permission, only admin can get files")
        try:
            await message.delete()
        except:
            pass
        return
    if message.audio:
        await message.answer(f"Audio file_id:\n{message.audio.file_id}")

    elif message.photo:
        file_id = message.photo[-1].file_id
        await message.answer(f"Photo file_id:\n{file_id}")

    elif message.video:
        await message.answer(f"Video file_id:\n{message.video.file_id}")

    elif message.animation:
        await message.answer(f"GIF file_id:\n{message.animation.file_id}")
# =======================================


# ===== SONG ============================
@dp.callback_query(lambda c: c.data.startswith("play_song"))
async def play_song(callback: types.CallbackQuery):

    parts = callback.data.split("|")

    album_id = parts[2]
    song_id = parts[3]

    songs = get_songs_by_album(album_id)

    start_index = 0
    for i, (s_id, title, file_id) in enumerate(songs):
        if s_id == song_id:
            start_index = i
            break

    for s_id, title, file_id in songs[start_index:]:
        song = get_song(s_id)
        if song:
            title, file_id, thumbnail = song

            await callback.message.answer_audio(
                audio=file_id,
                title=title,
                thumbnail=thumbnail
            )

        await callback.answer()
# =======================================


# ===== USER MSSG =======================
@dp.message()
async def track_user_messages(message: types.Message):
    chat_id = message.chat.id

    save_message(chat_id, message.message_id, "user")
# =======================================


async def main():
    set_role(794485298, 'admin')  # admin | @Baster_Skrag
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
