import random
from telegram import Update, ForceReply, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext
from googletrans import Translator

translator = Translator()
words = ["hello", "world", "apple", "banana", "cat", "dog", "house", "car", "book", "computer"]
supported_languages = {
    'spanish': 'es',
    'french': 'fr',
    'german': 'de',
    'italian': 'it',
    'portuguese': 'pt',
    'telugu': 'te'
}

basic_language_info = {
    'spanish': 'Spanish Alphabet: A, B, C, D, E, F, G, H, I, J, K, L, M, N, Ñ, O, P, Q, R, S, T, U, V, W, X, Y, Z\nCommon Phrases: Hola (Hello), Adiós (Goodbye), Por favor (Please), Gracias (Thank you)',
    'french': 'French Alphabet: A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z\nCommon Phrases: Bonjour (Hello), Au revoir (Goodbye), S\'il vous plaît (Please), Merci (Thank you)',
    'german': 'German Alphabet: A, Ä, B, C, D, E, F, G, H, I, J, K, L, M, N, O, Ö, P, Q, R, S, T, U, Ü, V, W, X, Y, Z\nCommon Phrases: Hallo (Hello), Auf Wiedersehen (Goodbye), Bitte (Please), Danke (Thank you)',
    'italian': 'Italian Alphabet: A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z\nCommon Phrases: Ciao (Hello), Arrivederci (Goodbye), Per favore (Please), Grazie (Thank you)',
    'portuguese': 'Portuguese Alphabet: A, B, C, D, E, F, G, H, I, J, K, L, M, N, O, P, Q, R, S, T, U, V, W, X, Y, Z\nCommon Phrases: Olá (Hello), Adeus (Goodbye), Por favor (Please), Obrigado/Obrigada (Thank you)',
    'telugu': 'Telugu Alphabet: అ, ఆ, ఇ, ఈ, ఉ, ఊ, ఋ, ౠ, ఎ, ఏ, ఐ, ఒ, ఓ, ఔ, అం, అః, క, ఖ, గ, ఘ, ఙ, చ, ఛ, జ, ఝ, ఞ, ట, ఠ, డ, ఢ, ణ, త, థ, ద, ధ, న, ప, ఫ, బ, భ, మ, య, ర, ల, వ, శ, ష, స, హ, ళ, క్ష, ఱ\nCommon Phrases: నమస్తే (Namaste - Hello), వీడ్కోలు (Veedkolu - Goodbye), దయచేసి (Dayachesi - Please), ధన్యవాదాలు (Danyavadalu - Thank you)'
}


def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    update.message.reply_html(
        rf'Hi {user.mention_html()}! I am your language learning bot. You can send me a word or sentence to translate, use /quiz to start a quiz, or use /language to select a language.',
        reply_markup=ForceReply(selective=True),
    )


def set_language(update: Update, context: CallbackContext) -> None:
    user_input = update.message.text.split()
    if len(user_input) < 2 or user_input[1].lower() not in supported_languages:
        update.message.reply_text(
            f'Please specify a language from the following: {", ".join(supported_languages.keys())}')
        return
    language = user_input[1].lower()
    context.user_data['language'] = supported_languages[language]
    context.user_data['asked_words'] = set()  # Reset asked words for the new language
    update.message.reply_text(f'Language set to {language.capitalize()}.\n\n{basic_language_info[language]}')


def translate(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    target_language = context.user_data.get('language', 'es')
    translation = translator.translate(text, dest=target_language)
    update.message.reply_text(f'Translation: {translation.text}')


def quiz(update: Update, context: CallbackContext) -> None:
    target_language = context.user_data.get('language', 'es')
    asked_words = context.user_data.get('asked_words', set())

    # Get a list of unasked words
    unasked_words = list(set(words) - asked_words)

    if not unasked_words:
        update.message.reply_text('You have answered all available questions. Resetting the quiz.')
        context.user_data['asked_words'] = set()
        unasked_words = words

    word = random.choice(unasked_words)
    translation = translator.translate(word, dest=target_language).text.lower()
    options = [translation] + [translator.translate(random.choice(words), dest=target_language).text.lower() for _ in
                               range(3)]
    random.shuffle(options)
    context.user_data['quiz_word'] = word
    context.user_data['quiz_answer'] = translation
    context.user_data['asked_words'].add(word)  # Mark the word as asked

    keyboard = [[InlineKeyboardButton(option, callback_data=option) for option in options]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        f'What is the {list(supported_languages.keys())[list(supported_languages.values()).index(target_language)]} word for "{word}"?',
        reply_markup=reply_markup)


def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    selected_option = query.data
    correct_answer = context.user_data.get('quiz_answer')
    quiz_word = context.user_data.get('quiz_word')

    if selected_option == correct_answer:
        score = context.user_data.get('score', 0) + 1
        context.user_data['score'] = score
        query.edit_message_text(
            text=f'Correct! "{quiz_word}" in {list(supported_languages.keys())[list(supported_languages.values()).index(context.user_data.get("language", "es"))]} is "{correct_answer}". Well done! Your score is {score}.')
    else:
        query.edit_message_text(
            text=f'Incorrect. "{quiz_word}" in {list(supported_languages.keys())[list(supported_languages.values()).index(context.user_data.get("language", "es"))]} is "{correct_answer}". Try again!')

    context.user_data['quiz_word'] = None
    context.user_data['quiz_answer'] = None


def handle_message(update: Update, context: CallbackContext) -> None:
    if context.user_data.get('quiz_word'):
        check_answer(update, context)
    else:
        translate(update, context)


def main() -> None:
    try:
        print("Initializing the bot...")
        updater = Updater("6655528740:AAGXj-VFwNtzWRsMm4mLmYRTUuUqR-xPw44")
        dispatcher = updater.dispatcher
        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(CommandHandler("language", set_language))
        dispatcher.add_handler(CommandHandler("quiz", quiz))
        dispatcher.add_handler(CallbackQueryHandler(button))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
        print("Bot started. Waiting for commands...")
        updater.start_polling()
        print("Polling started...")
        updater.idle()
        print("Bot is idle...")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
