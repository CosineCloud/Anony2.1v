import telebot
import sqlite3
import logging
import random
import string
import anony_number
import random_connection
import controls_anonybot
import uuid

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Bot configuration and state management can be added here if needed

# Dictionary of nickname components for anonymous name generation
NICKNAME_PARTS = {
    'adjectives': [
        'Amazing', 'Brave', 'Clever', 'Daring', 'Eager', 'Fierce', 'Gentle', 'Happy', 
        'Innocent', 'Jolly', 'Kind', 'Lively', 'Mighty', 'Noble', 'Polite', 'Quick', 
        'Radiant', 'Silent', 'Tough', 'Unique', 'Vibrant', 'Wise', 'Zealous'
    ],
    'animals': [
        'Ant', 'Bear', 'Cat', 'Dog', 'Eagle', 'Fox', 'Goat', 'Hawk', 'Ibex', 
        'Jaguar', 'Koala', 'Lion', 'Mouse', 'Newt', 'Owl', 'Panda', 'Quail', 
        'Rabbit', 'Snake', 'Tiger', 'Unicorn', 'Viper', 'Wolf', 'Yak', 'Zebra'
    ],
    'colors': [
        'Amber', 'Blue', 'Crimson', 'Diamond', 'Emerald', 'Fuchsia', 'Gold', 
        'Hazel', 'Indigo', 'Jade', 'Khaki', 'Lavender', 'Magenta', 'Navy', 
        'Orange', 'Purple', 'Quartz', 'Ruby', 'Silver', 'Teal', 'Umber', 
        'Violet', 'White', 'Yellow'
    ]
}

def ANONY_NAME():
    """
    Generate a random anonymous name by combining parts from three categories.
    Each part has 1-3 characters taken from the beginning to ensure uniqueness.
    
    Returns:
        A unique anonymous name string
    """
    # Select random parts from each category
    adjective = random.choice(NICKNAME_PARTS['adjectives'])
    animal = random.choice(NICKNAME_PARTS['animals'])
    color = random.choice(NICKNAME_PARTS['colors'])
    
    # Take random length (1-3) prefix from each part
    adj_len = random.randint(1, 3)
    animal_len = random.randint(1, 3)
    color_len = random.randint(1, 3)
    
    adj_part = adjective[:adj_len]
    animal_part = animal[:animal_len]
    color_part = color[:color_len]
    
    # Add a random number for additional uniqueness
    random_num = random.randint(10, 999)
    
    # Combine all parts to form the anonymous name
    anony_name = f"{adj_part}{animal_part}{color_part}{random_num}"
    
    logger.info(f"Generated anonymous name: {anony_name}")
    return anony_name

def generate_anony_name():
    """
    Generate a unique anonymous name for Anony Number feature.
    Uses a short UUID to ensure uniqueness.
    
    Returns:
        A unique anonymous name string
    """
    # Generate a short UUID (first 8 characters)
    short_uuid = str(uuid.uuid4())[:8]
    
    logger.info(f"Generated anonymous number ID: {short_uuid}")
    return short_uuid

def MEMBERSHIP_ID():
    """
    Generate a membership ID consisting of 9 digits starting with '92'.
    
    Returns:
        A string representing the membership ID
    """
    # Start with '92'
    prefix = "92"
    
    # Generate 7 more random digits
    random_digits = ''.join(random.choices(string.digits, k=7))
    
    # Combine to form the 9-digit membership ID
    membership_id = f"{prefix}{random_digits}"
    
    logger.info(f"Generated membership ID: {membership_id}")
    return membership_id

# Initialize the bot with the provided API key
bot = telebot.TeleBot("5768243722:AAGuPYWlGCH9x7I-N5bJ3u6royTuEfQ5ZFw")

# Dictionary to track user transitions (e.g., from connected to AI chat)
user_transitions = {}

# Update existing users with ANONY_NAME if they don't have one
try:
    conn = sqlite3.connect('user_db.db')
    cursor = conn.cursor()
    
    # Find users without ANONY_NAME
    cursor.execute("SELECT USER_ID FROM users WHERE ANONY_NAME IS NULL OR ANONY_NAME = ''")
    users_without_anony_name = cursor.fetchall()
    
    for user_row in users_without_anony_name:
        user_id = user_row[0]
        anony_name = generate_anony_name()
        
        # Update the user with a new ANONY_NAME
        cursor.execute("UPDATE users SET ANONY_NAME = ? WHERE USER_ID = ?", (anony_name, user_id))
        logger.info(f"Updated user {user_id} with new ANONY_NAME: {anony_name}")
    
    conn.commit()
    conn.close()
    logger.info(f"Updated {len(users_without_anony_name)} users with new ANONY_NAME values")
except sqlite3.Error as e:
    logger.error(f"Database error when updating users with ANONY_NAME: {e}")

# Database functions
def setup_database():
    """Initialize the database connection and create tables if needed."""
    try:
        # Connect to the main user database
        conn = sqlite3.connect('user_db.db', check_same_thread=False)
        cursor = conn.cursor()
        
        # Create the user table if it doesn't exist with TYPE set to R48 and OTP_EXP field
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            USER_ID INTEGER PRIMARY KEY,
            PEER_ID TEXT,
            TYPE TEXT DEFAULT 'R48',
            STATUS TEXT DEFAULT 'OPEN',
            TIMER INTEGER DEFAULT 120,
            OTP TEXT,
            OTP_EXP DATETIME,
            ANONY_NAME TEXT,
            ANONY_PEER TEXT,
            CREATED_AT DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        conn.commit()
        logger.info("Database setup completed successfully")
        return conn, cursor
    except sqlite3.Error as e:
        logger.error(f"Database setup error: {e}")
        raise

# Function to ensure user_def.db exists
def setup_user_def_database():
    """Initialize the user_def database connection and create tables if needed."""
    try:
        user_def_db_path = 'user_def.db'
        
        # Check if file exists
        import os
        if not os.path.exists(user_def_db_path):
            logger.info(f"Creating new user_def database at {user_def_db_path}")
            
            # Try to create the directory if it doesn't exist
            os.makedirs(os.path.dirname(user_def_db_path), exist_ok=True)
        
        # Connect to the user_def database with explicit file creation
        user_def_conn = sqlite3.connect(user_def_db_path)
        user_def_cursor = user_def_conn.cursor()
        
        # Create the user_def table if it doesn't exist - with only the required fields
        user_def_cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_def (
            USER_ID INTEGER PRIMARY KEY,
            MEMBERSHIP_ID TEXT UNIQUE,
            MEMBERSHIP_TYPE TEXT DEFAULT 'SILVER',
            CREDIT INTEGER DEFAULT 300
        )
        ''')
        
        # Verify the table was created
        user_def_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_def'")
        table_exists = user_def_cursor.fetchone() is not None
        
        if table_exists:
            logger.info("user_def table created/verified successfully")
        else:
            logger.error("Failed to create user_def table")
        
        user_def_conn.commit()
        
        # Check if the file was created
        if os.path.exists(user_def_db_path):
            file_size = os.path.getsize(user_def_db_path)
            logger.info(f"user_def.db created successfully, size: {file_size} bytes")
        else:
            logger.error("Failed to create user_def.db file")
        
        # Close the connection
        user_def_conn.close()
        return True
    except Exception as e:
        logger.error(f"User_def database setup error: {e}")
        return False

# Create database connections
conn, cursor = setup_database()
setup_user_def_database()

def insert_user(user_id):
    """Add a new user to the database if they don't already exist."""
    # First check if user already exists in users table
    try:
        cursor.execute("SELECT USER_ID FROM users WHERE USER_ID = ?", (user_id,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # Check if the user has an ANONY_NAME, if not, generate one
            cursor.execute("SELECT ANONY_NAME FROM users WHERE USER_ID = ?", (user_id,))
            anony_name_data = cursor.fetchone()
            
            if not anony_name_data or not anony_name_data[0]:
                # Generate a random ANONY_NAME
                anony_name = generate_anony_name()
                
                # Update the user with the new ANONY_NAME
                cursor.execute("UPDATE users SET ANONY_NAME = ? WHERE USER_ID = ?", (anony_name, user_id))
                conn.commit()
                logger.info(f"Generated ANONY_NAME '{anony_name}' for existing user {user_id}")
            else:
                logger.info(f"User {user_id} already exists with ANONY_NAME '{anony_name_data[0]}'")
        else:
            # Generate a random ANONY_NAME for the new user
            anony_name = generate_anony_name()
            
            # Insert into users table in user_db.db with TYPE set to R48 and the generated ANONY_NAME
            cursor.execute('''
            INSERT INTO users (USER_ID, PEER_ID, TYPE, STATUS, TIMER, OTP, ANONY_NAME)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, '', 'R48', 'OPEN', 120, '', anony_name))
            conn.commit()
            logger.info(f"User {user_id} inserted into users table with ANONY_NAME '{anony_name}'")
    except sqlite3.Error as e:
        logger.error(f"Database error when checking/inserting user {user_id} into users table: {e}")
    
    # Now handle user_def.db separately with a direct approach
    try:
        # Ensure the user_def database exists and is properly set up
        setup_user_def_database()
        
        # Connect directly to user_def.db
        user_def_db_path = 'user_def.db'
        user_def_conn = sqlite3.connect(user_def_db_path)
        user_def_cursor = user_def_conn.cursor()
        
        # Check if user already exists in user_def table
        user_def_cursor.execute("SELECT USER_ID FROM user_def WHERE USER_ID = ?", (user_id,))
        existing_user = user_def_cursor.fetchone()
        
        if existing_user:
            logger.info(f"User {user_id} already exists in user_def.db, skipping insert")
        else:
            # Generate membership ID
            membership_id = MEMBERSHIP_ID()
            
            # Insert user into user_def table with only the required fields
            user_def_cursor.execute('''
            INSERT INTO user_def (USER_ID, MEMBERSHIP_ID, MEMBERSHIP_TYPE, CREDIT)
            VALUES (?, ?, ?, ?)
            ''', (user_id, membership_id, 'SILVER', 300))
            user_def_conn.commit()
            logger.info(f"User {user_id} inserted into user_def.db with membership ID {membership_id}")
        
        # Verify the data exists in the table
        user_def_cursor.execute("SELECT * FROM user_def WHERE USER_ID = ?", (user_id,))
        user_data = user_def_cursor.fetchone()
        if user_data:
            logger.info(f"Verified user {user_id} exists in user_def.db: {user_data}")
        else:
            logger.error(f"Failed to verify user {user_id} in user_def.db")
        
        user_def_conn.close()
    except Exception as e:
        logger.error(f"Error handling user_def.db for user {user_id}: {e}")

# Menu creation functions
def create_main_menu():
    """Create the main menu markup with all primary options."""
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("🔐 Private Connection", callback_data="private_connection"))
    markup.row(telebot.types.InlineKeyboardButton("🔀 Random Connection", callback_data="random_connection"))
    markup.row(
        telebot.types.InlineKeyboardButton("⏏️", callback_data="eject"),
        telebot.types.InlineKeyboardButton("⏹️", callback_data="stop"),
        telebot.types.InlineKeyboardButton("⏩️", callback_data="forward")
    )
    markup.row(telebot.types.InlineKeyboardButton("📲 Anony Number", callback_data="anony_number"))
    markup.row(telebot.types.InlineKeyboardButton("🔊 Broadcasting", callback_data="broadcasting"))
    markup.row(telebot.types.InlineKeyboardButton("✨AI Chat bot", callback_data="ai_chat_bot"))
    markup.row(
        telebot.types.InlineKeyboardButton("🚹 About", callback_data="about"),
        telebot.types.InlineKeyboardButton("📝 Privacy", callback_data="privacy")
    )
    markup.row(telebot.types.InlineKeyboardButton("More >>", callback_data="more"))
    return markup

def create_more_menu():
    """Create the secondary 'More' menu markup."""
    markup = telebot.types.InlineKeyboardMarkup()
    markup.row(telebot.types.InlineKeyboardButton("Membership", callback_data="membership"))
    markup.row(
        telebot.types.InlineKeyboardButton("Help", callback_data="help_contact"),
        telebot.types.InlineKeyboardButton("Contact Us", callback_data="help_contact")
    )
    markup.row(telebot.types.InlineKeyboardButton("<< Back", callback_data="back"))
    return markup

# Settings menu functionality has been removed

# Command handlers
# Import the database manager functions
try:
    from telegram_db_manager import register_new_user
except ImportError:
    # Define a fallback function if import fails
    def register_new_user(user_id):
        logger.error(f"Failed to import register_new_user function, using fallback for user {user_id}")
        return {
            "status": "error",
            "message": "Database module not available"
        }

# Import private connection handler
try:
    from private_connection import handle_private_connection_request
except ImportError:
    # Define a fallback function if import fails
    def handle_private_connection_request(user_id):
        logger.error(f"Failed to import handle_private_connection_request function, using fallback for user {user_id}")
        return "Private connection feature is currently unavailable. Please try again later."

# Import message sender
try:
    from message_sender import handle_message
except ImportError:
    # Define a fallback function if import fails
    def handle_message(bot, message, user_id=None):
        logger.error(f"Failed to import handle_message function, using fallback for user {message.from_user.id}")
        return False

# Import private link verifier
try:
    from private_link_verifier import verify_private_link
except ImportError:
    # Define a fallback function if import fails
    def verify_private_link(link_text, user_id):
        logger.error(f"Failed to import verify_private_link function, using fallback for user {user_id}")
        return {
            "status": "error",
            "message": "Private link verification is currently unavailable. Please try again later."
        }

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handle the /start command by registering the user and showing the main menu."""
    user_id = message.from_user.id
    
    # Register user in both database tables
    user_data = register_new_user(user_id)
    
    # Create welcome message based on registration status
    if user_data["status"] == "success":
        welcome_text = (
            f"||             𝓐𝓷𝓸𝓷𝔂𝓶𝓸𝓾𝓼 𝓒𝓱𝓪𝓽𝓼\n\n"
            f"Your anonymous name: {user_data['anony_name']}\n"
            f"Your membership ID: {user_data['membership_id']}\n"
            f"Membership type: {user_data['membership_type']}\n"
            f"Available credits: {user_data['credit']}"
        )
    else:
        # Fallback to original message and use the old insert_user function
        insert_user(user_id)
        
        # Try to get user information from both databases after insertion
        try:
            # Get data from users table in user_db.db
            cursor.execute("SELECT ANONY_NAME FROM users WHERE USER_ID = ?", (user_id,))
            user_data = cursor.fetchone()
            anony_name = user_data[0] if user_data and user_data[0] else "Anonymous"
            
            # Get membership info from user_def.db
            user_def_db_path = 'user_def.db'
            
            # Make sure user_def.db exists and is set up
            setup_user_def_database()
            
            # Connect to user_def.db
            user_def_conn = sqlite3.connect(user_def_db_path)
            user_def_cursor = user_def_conn.cursor()
            
            # Get user data from user_def table
            user_def_cursor.execute("SELECT MEMBERSHIP_ID, MEMBERSHIP_TYPE, CREDIT FROM user_def WHERE USER_ID = ?", (user_id,))
            membership_data = user_def_cursor.fetchone()
            
            if membership_data:
                membership_id, membership_type, credit = membership_data
                welcome_text = (
                    f"||             𝓐𝓷𝓸𝓷𝔂𝓶𝓸𝓾𝓼 𝓒𝓱𝓪𝓽𝓼\n\n"
                    f"Your anonymous name: {anony_name}\n"
                    f"Your membership ID: {membership_id}\n"
                    f"Membership type: {membership_type}\n"
                    f"Available credits: {credit}"
                )
                logger.info(f"Retrieved user data from both databases for user {user_id}")
            else:
                welcome_text = f"||             𝓐𝓷𝓸𝓷𝔂𝓶𝓸𝓾𝓼 𝓒𝓱𝓪𝓽𝓼\n\nYour anonymous name: {anony_name}"
                logger.warning(f"Could not retrieve membership data for user {user_id} from user_def.db")
            user_def_conn.close()
        except Exception as e:
            logger.error(f"Error retrieving user data after fallback insertion: {e}")
            welcome_text = "||             𝓐𝓷𝓸𝓷𝔂𝓶𝓸𝓾𝓼 𝓒𝓱𝓪𝓽𝓼."
    
    # Send welcome message with main menu
    markup = create_main_menu()
    bot.send_message(message.chat.id, welcome_text, reply_markup=markup)
    logger.info(f"Welcome message sent to user {user_id}")

# Message handlers
@bot.message_handler(func=lambda message: message.text == "🚹\nAbout")
def handle_about_text(message):
    """Handle text message for About."""
    bot.reply_to(message, "Hey")
    logger.info(f"About info sent to user {message.from_user.id} via text message")

# Callback handlers
@bot.callback_query_handler(func=lambda call: call.data == "more")
def handle_more_callback(call):
    """Handle the 'More' button callback."""
    bot.answer_callback_query(call.id)
    markup = create_more_menu()
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    logger.info(f"More menu shown to user {call.from_user.id}")

@bot.callback_query_handler(func=lambda call: call.data == "back")
def handle_back_callback(call):
    """Handle the 'Back' button callback to return to main menu."""
    bot.answer_callback_query(call.id)
    markup = create_main_menu()
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
    logger.info(f"User {call.from_user.id} returned to main menu")

@bot.callback_query_handler(func=lambda call: call.data == "private_connection")
def handle_private_connection_callback(call):
    """Handle the 'Private Connection' button callback."""
    bot.answer_callback_query(call.id)
    user_id = call.from_user.id
    
    # Process the private connection request
    response = handle_private_connection_request(user_id)
    
    # Send the response to the user
    bot.send_message(call.message.chat.id, response)
    logger.info(f"Private connection request processed for user {user_id}")

@bot.callback_query_handler(func=lambda call: call.data == "about")
def handle_about_callback(call):
    """Handle the 'About' button callback."""
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, "Hey")
    logger.info(f"About info sent to user {call.from_user.id}")

@bot.callback_query_handler(func=lambda call: call.data == "anony_number")
def handle_anony_number_callback(call):
    """Handle the 'Anony Number' button callback."""
    bot.answer_callback_query(call.id)
    
    try:
        # Get user ID
        user_id = int(call.from_user.id)
        logger.info(f"Anony Number requested by user {user_id}")
        
        # Create a message object with the correct user ID
        # This ensures we're not passing the bot's ID by mistake
        class UserMessage:
            def __init__(self, user_id, chat_id):
                self.from_user = type('obj', (object,), {'id': user_id})
                self.chat = type('obj', (object,), {'id': chat_id})
        
        # Create a message with the user's ID
        user_message = UserMessage(user_id, call.message.chat.id)
        
        # Call the anony_number module's handler with the correct user ID
        anony_number.handle_anony_number_command(bot, user_message)
    except Exception as e:
        logger.error(f"Error handling anony_number request: {e}")
        bot.send_message(call.message.chat.id, "Sorry, there was an error processing your request. Please try again later.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("share_"))
def handle_share_decision(call):
    """Handle the decision to share an anonymous number."""
    bot.answer_callback_query(call.id)
    
    # Get user ID
    user_id = call.from_user.id
    logger.info(f"Share decision from user {user_id}: {call.data}")
    
    # Call the anony_number module's handler
    anony_number.handle_share_decision(bot, call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("save_"))
def handle_save_decision(call):
    """Handle the decision to save an anonymous number."""
    bot.answer_callback_query(call.id)
    
    # Get user ID
    user_id = call.from_user.id
    logger.info(f"Save decision from user {user_id}: {call.data}")
    
    # Call the anony_number module's handler
    anony_number.handle_save_decision(bot, call)

@bot.callback_query_handler(func=lambda call: call.data.startswith("accept_an_") or call.data.startswith("decline_an_"))
def handle_an_connection_response(call):
    """Handle the response to an Anonymous Number connection request."""
    bot.answer_callback_query(call.id)
    
    # Get user ID
    user_id = call.from_user.id
    logger.info(f"AN connection response from user {user_id}: {call.data}")
    
    # Call the anony_number module's handler
    anony_number.handle_an_connection_response(bot, call)

@bot.callback_query_handler(func=lambda call: call.data == "random_connection")
def handle_random_connection_callback(call):
    """Handle the Random Connection button callback."""
    bot.answer_callback_query(call.id)
    
    try:
        # Create a message object with the user's ID for the random_connection module
        class UserMessage:
            def __init__(self, user_id, chat_id):
                self.from_user = type('obj', (object,), {'id': user_id})
                self.chat = type('obj', (object,), {'id': chat_id})
        
        # Create a message with the user's ID
        user_message = UserMessage(int(call.from_user.id), call.message.chat.id)
        
        # Call the random_connection module's handler
        logger.info(f"Random connection requested by user {call.from_user.id}")
        random_connection.handle_random_connection(bot, user_message)
    except Exception as e:
        logger.error(f"Error handling random connection request: {e}")
        bot.send_message(call.message.chat.id, "Sorry, there was an error processing your request. Please try again later.")

@bot.callback_query_handler(func=lambda call: call.data == "eject")
def handle_eject_callback(call):
    """Handle the ⏏️ (Eject) button callback."""
    try:
        logger.info(f"Eject button clicked by user {call.from_user.id}")
        # Don't answer the callback query here, let the module handle it
        controls_anonybot.handle_eject_callback(bot, call)
    except Exception as e:
        logger.error(f"Error handling eject button: {e}")
        bot.answer_callback_query(call.id, text="Error processing request", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "stop")
def handle_stop_callback(call):
    """Handle the ⏹️ (Stop) button callback."""
    try:
        logger.info(f"Stop button clicked by user {call.from_user.id}")
        # Don't answer the callback query here, let the module handle it
        controls_anonybot.handle_stop_callback(bot, call)
    except Exception as e:
        logger.error(f"Error handling stop button: {e}")
        bot.answer_callback_query(call.id, text="Error processing request", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "forward")
def handle_forward_callback(call):
    """Handle the ⏩️ (Forward) button callback."""
    try:
        logger.info(f"Forward button clicked by user {call.from_user.id}")
        # Don't answer the callback query here, let the module handle it
        controls_anonybot.handle_forward_callback(bot, call)
    except Exception as e:
        logger.error(f"Error handling forward button: {e}")
        bot.answer_callback_query(call.id, text="Error processing request", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "broadcasting")
def handle_broadcasting_callback(call):
    """Handle the 🔊 Broadcasting button callback."""
    try:
        logger.info(f"Broadcasting button clicked by user {call.from_user.id}")
        # Show message that the feature is unavailable
        bot.answer_callback_query(
            call.id,
            text="This feature is unavailable for you",
            show_alert=True
        )
    except Exception as e:
        logger.error(f"Error handling broadcasting button: {e}")
        bot.answer_callback_query(call.id, text="Error processing request", show_alert=True)

def get_user_membership_info(user_id):
    """
    Get a user's membership information from the user_def database.
    
    Args:
        user_id: The Telegram user ID
        
    Returns:
        A dictionary with membership information or None if not found
    """
    try:
        # Define user_def database path
        user_def_db_path = 'user_def.db'
        
        # Connect to the user_def database
        conn = sqlite3.connect(user_def_db_path)
        cursor = conn.cursor()
        
        # Get user data
        cursor.execute("SELECT MEMBERSHIP_ID, MEMBERSHIP_TYPE, CREDIT FROM user_def WHERE USER_ID = ?", (user_id,))
        membership_data = cursor.fetchone()
        
        conn.close()
        
        if not membership_data:
            logger.error(f"User {user_id} not found in user_def database")
            return None
        
        membership_id, membership_type, credit = membership_data
        
        return {
            "membership_id": membership_id,
            "membership_type": membership_type,
            "credit": credit
        }
    except Exception as e:
        logger.error(f"Error getting membership info for user {user_id}: {e}")
        return None

@bot.callback_query_handler(func=lambda call: call.data == "membership")
def handle_membership_callback(call):
    """Handle the Membership button callback."""
    try:
        user_id = call.from_user.id
        logger.info(f"Membership button clicked by user {user_id}")
        
        # Get membership information
        membership_info = get_user_membership_info(user_id)
        
        if membership_info:
            # Show membership information
            bot.answer_callback_query(
                call.id,
                text=f"Membership ID: {membership_info['membership_id']}\n"
                     f"Membership Type: {membership_info['membership_type']}\n"
                     f"Credit: {membership_info['credit']}",
                show_alert=True
            )
        else:
            # Show error message
            bot.answer_callback_query(
                call.id,
                text="Could not retrieve membership information. Please try again later.",
                show_alert=True
            )
    except Exception as e:
        logger.error(f"Error handling membership button: {e}")
        bot.answer_callback_query(call.id, text="Error processing request", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "ai_chat_bot")
def handle_ai_chat_bot_callback(call):
    """Handle the ✨AI Chat bot button callback."""
    try:
        user_id = call.from_user.id
        logger.info(f"AI Chat bot button clicked by user {user_id}")
        
        # Get current user status
        conn = sqlite3.connect('user_db.db')
        cursor = conn.cursor()
        cursor.execute("SELECT STATUS FROM users WHERE USER_ID = ?", (user_id,))
        status_data = cursor.fetchone()
        conn.close()
        
        if not status_data:
            bot.answer_callback_query(
                call.id,
                text="User not found in database. Please try again later.",
                show_alert=True
            )
            return
        
        current_status = status_data[0]
        
        # Check if user is already connected to someone
        if current_status in ["CONNECTED", "PRIVATE", "RANDOM"]:
            # Create confirmation keyboard
            markup = telebot.types.InlineKeyboardMarkup()
            markup.row(
                telebot.types.InlineKeyboardButton("YES", callback_data="ai_chat_confirm_yes"),
                telebot.types.InlineKeyboardButton("NO", callback_data="ai_chat_confirm_no")
            )
            
            # Send confirmation message
            bot.send_message(
                call.message.chat.id,
                "You are connected with a partner. Do you want to close the connection to continue with the AI chat?",
                reply_markup=markup
            )
        else:
            # User is not connected, start AI chat directly
            # Update user status in database
            conn = sqlite3.connect('user_db.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET STATUS = 'AI', PEER_ID = NULL WHERE USER_ID = ?", (user_id,))
            conn.commit()
            conn.close()
            logger.info(f"Updated user {user_id} status to AI")
            
            # Start AI chat
            from ai_integration import start_ai_chat
            if start_ai_chat(bot, call.message):
                logger.info(f"Started AI chat for user {user_id} directly")
            else:
                logger.error(f"Failed to start AI chat for user {user_id} directly")
    except Exception as e:
        logger.error(f"Error handling AI Chat bot button: {e}")
        bot.answer_callback_query(call.id, text="Error processing request", show_alert=True)

@bot.callback_query_handler(func=lambda call: call.data == "ai_chat_confirm_yes")
def handle_ai_chat_confirm_yes(call):
    """Handle the YES confirmation for AI Chat."""
    try:
        user_id = call.from_user.id
        logger.info(f"User {user_id} confirmed switching to AI chat")
        
        # Delete the confirmation message
        bot.delete_message(call.message.chat.id, call.message.message_id)
        
        # Update user status in database directly
        conn = sqlite3.connect('user_db.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET STATUS = 'AI', PEER_ID = NULL WHERE USER_ID = ?", (user_id,))
        conn.commit()
        conn.close()
        logger.info(f"Updated user {user_id} status to AI")
        
        # Start AI chat
        from ai_integration import start_ai_chat
        if start_ai_chat(bot, call.message):
            logger.info(f"Started AI chat for user {user_id}")
        else:
            logger.error(f"Failed to start AI chat for user {user_id}")
    except Exception as e:
        logger.error(f"Error handling AI Chat confirmation: {e}")
        bot.send_message(call.message.chat.id, "Error processing request. Please try again later.")

@bot.callback_query_handler(func=lambda call: call.data == "ai_chat_confirm_no")
def handle_ai_chat_confirm_no(call):
    """Handle the NO confirmation for AI Chat."""
    try:
        user_id = call.from_user.id
        logger.info(f"User {user_id} declined switching to AI chat")
        
        # Delete the confirmation message
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        logger.error(f"Error handling AI Chat decline: {e}")
        bot.send_message(call.message.chat.id, "Error processing request. Please try again later.")

@bot.callback_query_handler(func=lambda call: call.data == "share_an_yes")
def handle_share_an_yes(call):
    """Handle the YES confirmation for sharing anonymous number."""
    try:
        user_id = call.from_user.id
        logger.info(f"User {user_id} confirmed sharing anonymous number")
        
        # Check if user is transitioning to AI chat
        if user_id in user_transitions and user_transitions[user_id]["transitioning_to"] == "AI":
            peer_id = user_transitions[user_id]["peer_id"]
            
            # Share anonymous number with peer
            try:
                # Get user's anonymous number
                conn = sqlite3.connect('user_def.db')
                cursor = conn.cursor()
                cursor.execute("SELECT ANONY_NUMBER FROM user_def WHERE USER_ID = ?", (user_id,))
                an_data = cursor.fetchone()
                conn.close()
                
                if an_data and an_data[0]:
                    anony_number = an_data[0]
                    
                    # Send anonymous number to peer
                    bot.send_message(
                        peer_id,
                        f"Your partner has shared their anonymous number with you: /AN{anony_number}"
                    )
                    
                    # Notify user that number was shared
                    bot.send_message(
                        call.message.chat.id,
                        "Your anonymous number has been shared with your partner."
                    )
                else:
                    # User doesn't have an anonymous number
                    bot.send_message(
                        call.message.chat.id,
                        "You don't have an anonymous number to share."
                    )
            except Exception as e:
                logger.error(f"Error sharing anonymous number: {e}")
                bot.send_message(
                    call.message.chat.id,
                    "Error sharing anonymous number. Please try again later."
                )
            
            # Now transition to AI chat
            # Update user status in database
            conn = sqlite3.connect('user_db.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET STATUS = 'AI', PEER_ID = NULL WHERE USER_ID = ?", (user_id,))
            conn.commit()
            conn.close()
            logger.info(f"Updated user {user_id} status to AI after sharing anonymous number")
            
            # Start AI chat
            from ai_integration import start_ai_chat
            if start_ai_chat(bot, call.message):
                logger.info(f"Started AI chat for user {user_id} after sharing anonymous number")
            else:
                logger.error(f"Failed to start AI chat for user {user_id} after sharing anonymous number")
            
            # Clean up transition data
            del user_transitions[user_id]
        else:
            # Not transitioning to AI chat, just handle normal anonymous number sharing
            bot.send_message(
                call.message.chat.id,
                "Anonymous number sharing is only available when transitioning to AI chat."
            )
        
        # Delete the confirmation message
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        logger.error(f"Error handling anonymous number sharing: {e}")
        bot.send_message(call.message.chat.id, "Error processing request. Please try again later.")

@bot.callback_query_handler(func=lambda call: call.data == "share_an_no")
def handle_share_an_no(call):
    """Handle the NO confirmation for sharing anonymous number."""
    try:
        user_id = call.from_user.id
        logger.info(f"User {user_id} declined sharing anonymous number")
        
        # Check if user is transitioning to AI chat
        if user_id in user_transitions and user_transitions[user_id]["transitioning_to"] == "AI":
            # Just transition to AI chat without sharing anonymous number
            # Update user status in database
            conn = sqlite3.connect('user_db.db')
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET STATUS = 'AI', PEER_ID = NULL WHERE USER_ID = ?", (user_id,))
            conn.commit()
            conn.close()
            logger.info(f"Updated user {user_id} status to AI without sharing anonymous number")
            
            # Start AI chat
            from ai_integration import start_ai_chat
            if start_ai_chat(bot, call.message):
                logger.info(f"Started AI chat for user {user_id} without sharing anonymous number")
            else:
                logger.error(f"Failed to start AI chat for user {user_id} without sharing anonymous number")
            
            # Clean up transition data
            del user_transitions[user_id]
        
        # Delete the confirmation message
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        logger.error(f"Error handling anonymous number sharing decline: {e}")
        bot.send_message(call.message.chat.id, "Error processing request. Please try again later.")

# Handler for Anonymous Number connection (/AN...)
@bot.message_handler(func=lambda message: message.content_type == 'text' and message.text.startswith('/AN'))
def handle_an_command(message):
    """Handle Anonymous Number connection requests."""
    user_id = message.from_user.id
    an_text = message.text
    logger.info(f"Received Anonymous Number connection request from user {user_id}: {an_text}")
    
    # Call the anony_number module's handler
    anony_number.handle_an_command(bot, message)

# Handler for private link verification (/92...)
@bot.message_handler(func=lambda message: message.content_type == 'text' and message.text.startswith('/92'))
def handle_private_link(message):
    """Handle private link verification messages."""
    user_id = message.from_user.id
    link_text = message.text
    
    logger.info(f"Received private link verification request from user {user_id}: {link_text}")
    
    # Send initial verification message
    bot.send_message(user_id, "Verifying Private Link...")
    
    # Verify the private link
    result = verify_private_link(link_text, user_id)
    
    # Send the result message
    bot.send_message(user_id, result["message"])
    
    if result["status"] == "success":
        logger.info(f"Private link verified for user {user_id}, connected to peer {result.get('peer_id')}")
    else:
        logger.warning(f"Private link verification failed for user {user_id}: {result['message']}")

# Message handler for regular messages (without commands)
@bot.message_handler(func=lambda message: True, content_types=['text', 'sticker', 'voice', 'photo', 'video', 'animation', 'audio', 'document'])
def handle_all_messages(message):
    """Handle all regular messages (without commands) and forward them to peers if appropriate."""
    # Skip command messages (they start with '/')
    if message.content_type == 'text' and message.text.startswith('/'):
        return
    
    user_id = message.from_user.id
    logger.info(f"Received {message.content_type} message from user {user_id}")
    
    # Check if user is in AI chat mode
    conn = sqlite3.connect('user_db.db')
    cursor = conn.cursor()
    cursor.execute("SELECT STATUS FROM users WHERE USER_ID = ?", (user_id,))
    user_data = cursor.fetchone()
    conn.close()
    
    if user_data and user_data[0] == 'AI':
        # User is in AI chat mode, handle with AI
        if message.content_type == 'text':
            logger.info(f"Handling AI chat message from user {user_id}")
            try:
                # Show typing indicator
                bot.send_chat_action(message.chat.id, 'typing')
                
                # Process the message
                from ai_integration import handle_ai_message
                ai_response = handle_ai_message(bot, message, user_id)
                
                # Show typing indicator again before sending response
                bot.send_chat_action(message.chat.id, 'typing')
                
                # Send the response
                bot.send_message(message.chat.id, ai_response)
                logger.info(f"Sent AI response to user {user_id}")
                return
            except Exception as e:
                logger.error(f"Error handling AI chat message: {e}")
                bot.send_message(
                    message.chat.id,
                    "Sorry, I'm having trouble connecting to the AI. Please try again later."
                )
                return
        else:
            # AI chat only supports text messages
            bot.send_message(
                message.chat.id,
                "Not Allowed"
            )
            return
    
    # Not in AI chat mode, try to handle and forward the message
    result = handle_message(bot, message)
    
    if not result:
        # If message wasn't forwarded (no valid peer), inform the user
        bot.send_message(
            user_id, 
            "You are not currently connected to anyone. Please use the menu to start a connection."
        )
        logger.info(f"User {user_id} tried to send a message but is not connected")

# Main function
def main():
    """Main function to start the bot with error handling and retry mechanism."""
    logger.info("Starting bot...")
    
    # Ensure databases are set up properly
    logger.info("Setting up databases...")
    setup_database()
    setup_user_def_database()
    logger.info("Database setup complete")
    
    # Reset webhook to avoid conflicts
    bot.remove_webhook()
    
    retry_count = 0
    max_retries = 5
    retry_delay = 5  # seconds
    
    while retry_count < max_retries:
        try:
            logger.info("Bot started successfully!")
            # Handle the 409 conflict error
            bot.polling(none_stop=True, interval=1, timeout=20)
            # If polling exits without exception, break the loop
            break
            
        except telebot.apihelper.ApiTelegramException as telegram_error:
            if "Conflict: terminated by other getUpdates request" in str(telegram_error):
                logger.warning("Conflict with another bot instance. Resetting connection...")
                bot.stop_polling()
                time.sleep(retry_delay)
                retry_count += 1
            else:
                logger.error(f"Telegram API error: {telegram_error}")
                break
                
        except Exception as e:
            logger.error(f"Bot error: {e}")
            retry_count += 1
            logger.info(f"Retrying in {retry_delay} seconds... (Attempt {retry_count}/{max_retries})")
            time.sleep(retry_delay)
    
    if retry_count >= max_retries:
        logger.error("Maximum retry attempts reached. Bot stopped.")

if __name__ == "__main__":
    import time  # Add time module for sleep functionality
    main()
