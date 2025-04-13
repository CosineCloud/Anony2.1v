#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import sqlite3
import random_connection

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database path
DB_PATH = 'user_db.db'

def connect_database():
    """Connect to the SQLite database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        return conn, cursor
    except sqlite3.Error as e:
        logger.error(f"Database connection error: {e}")
        return None, None

def get_user_status(user_id):
    """Get the current status of a user."""
    conn, cursor = connect_database()
    if not conn or not cursor:
        return None
    
    try:
        cursor.execute("SELECT STATUS FROM users WHERE USER_ID = ?", (user_id,))
        result = cursor.fetchone()
        if result:
            return result[0]
        return None
    except sqlite3.Error as e:
        logger.error(f"Database error in get_user_status: {e}")
        return None
    finally:
        if conn:
            conn.close()

def update_user_status(user_id, new_status):
    """Update the status of a user."""
    conn, cursor = connect_database()
    if not conn or not cursor:
        return False
    
    try:
        cursor.execute("UPDATE users SET STATUS = ? WHERE USER_ID = ?", (new_status, user_id))
        conn.commit()
        logger.info(f"Updated status of user {user_id} to {new_status}")
        return True
    except sqlite3.Error as e:
        logger.error(f"Database error in update_user_status: {e}")
        return False
    finally:
        if conn:
            conn.close()

def handle_eject_button(bot, call):
    """
    Handle the ⏏️ (Eject) button click.
    
    Args:
        bot: The Telegram bot instance
        call: The callback query from the user
    """
    user_id = int(call.from_user.id)
    logger.info(f"Eject button clicked by user {user_id}")
    
    # Show service error message
    bot.answer_callback_query(
        call.id,
        text="Service Error",
        show_alert=True
    )

def handle_stop_button(bot, call):
    """
    Handle the ⏹️ (Stop) button click.
    
    Args:
        bot: The Telegram bot instance
        call: The callback query from the user
    """
    user_id = int(call.from_user.id)
    logger.info(f"Stop button clicked by user {user_id}")
    
    # Get current status
    current_status = get_user_status(user_id)
    
    # If status is already CLOSED, show message
    if current_status == "CLOSED":
        bot.answer_callback_query(
            call.id,
            text="Your connection is already closed!!",
            show_alert=True
        )
        return
    
    # Update status to CLOSED
    success = update_user_status(user_id, "CLOSED")
    
    if success:
        # Show success message
        bot.answer_callback_query(
            call.id,
            text="Connection Closed",
            show_alert=True
        )
        
        # Also send a message to the chat
        bot.send_message(
            call.message.chat.id,
            "⏹️ Your connection has been closed."
        )
        
        # If the user was connected to someone, notify the peer
        conn, cursor = connect_database()
        if conn and cursor:
            try:
                cursor.execute("SELECT PEER_ID FROM users WHERE USER_ID = ?", (user_id,))
                result = cursor.fetchone()
                if result and result[0]:
                    peer_id = result[0]
                    # Update peer's status and notify them
                    cursor.execute("UPDATE users SET STATUS = 'CLOSED', PEER_ID = NULL WHERE USER_ID = ?", (peer_id,))
                    conn.commit()
                    
                    # Notify the peer
                    bot.send_message(
                        peer_id,
                        "⏹️ Your partner has ended the connection."
                    )
                
                # Clear the user's peer_id
                cursor.execute("UPDATE users SET PEER_ID = NULL WHERE USER_ID = ?", (user_id,))
                conn.commit()
            except sqlite3.Error as e:
                logger.error(f"Database error in handle_stop_button: {e}")
            finally:
                conn.close()
    else:
        # Show error message
        bot.answer_callback_query(
            call.id,
            text="Error closing connection. Please try again.",
            show_alert=True
        )

def handle_forward_button(bot, call):
    """
    Handle the ⏩️ (Forward) button click.
    
    Args:
        bot: The Telegram bot instance
        call: The callback query from the user
    """
    user_id = int(call.from_user.id)
    logger.info(f"Forward button clicked by user {user_id}")
    
    # Get current status
    current_status = get_user_status(user_id)
    
    # If status is already OPEN, show message
    if current_status == "OPEN":
        bot.answer_callback_query(
            call.id,
            text="Please wait, you are in queue...",
            show_alert=True
        )
        return
    
    # Update status to OPEN
    success = update_user_status(user_id, "OPEN")
    
    if success:
        # Show searching message
        bot.answer_callback_query(
            call.id,
            text="Searching for Partner...",
            show_alert=True
        )
        
        # Also send a message to the chat
        bot.send_message(
            call.message.chat.id,
            "⏩️ Searching for a partner..."
        )
        
        # Create a message object for random_connection
        class UserMessage:
            def __init__(self, user_id, chat_id):
                self.from_user = type('obj', (object,), {'id': user_id})
                self.chat = type('obj', (object,), {'id': chat_id})
        
        # Trigger random_connection.py
        user_message = UserMessage(user_id, call.message.chat.id)
        random_connection.handle_random_connection(bot, user_message)
    else:
        # Show error message
        bot.answer_callback_query(
            call.id,
            text="Error starting search. Please try again.",
            show_alert=True
        )

# Handler functions to be called from telegram_bot.py
def handle_eject_callback(bot, call):
    """Handler for the ⏏️ button callback."""
    # Show alert directly instead of just acknowledging the callback
    bot.answer_callback_query(
        call.id,
        text="Service Error",
        show_alert=True
    )
    # No need to call handle_eject_button since it does the same thing

def handle_stop_callback(bot, call):
    """Handler for the ⏹️ button callback."""
    # Don't answer the callback query here, let handle_stop_button do it with the appropriate message
    handle_stop_button(bot, call)

def handle_forward_callback(bot, call):
    """Handler for the ⏩️ button callback."""
    # Don't answer the callback query here, let handle_forward_button do it with the appropriate message
    handle_forward_button(bot, call)

if __name__ == "__main__":
    print("This module is designed to be imported, not run directly.")