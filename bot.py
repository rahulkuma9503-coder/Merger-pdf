import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
from pdf_handler import PDFHandler
from session_manager import SessionManager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize handlers
pdf_handler = PDFHandler()
session_manager = SessionManager()

# Constants
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB

class PDFBot:
    @staticmethod
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user_id = update.effective_user.id
        session_manager.clear_session(user_id)
        
        keyboard = [
            [InlineKeyboardButton("📄 Merge PDFs", callback_data='merge')],
            [InlineKeyboardButton("✏️ Rename PDF", callback_data='rename')],
            [InlineKeyboardButton("💧 Add Watermark", callback_data='watermark')],
            [InlineKeyboardButton("ℹ️ Help", callback_data='help')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        welcome_text = (
            "🤖 *Welcome to PDF Utility Bot!*\n\n"
            "I can help you with:\n"
            "• Merge multiple PDF files\n"
            "• Rename PDF files\n"
            "• Add text watermarks to PDFs\n\n"
            "Choose an option below to get started:"
        )
        
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

    @staticmethod
    async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        action = query.data
        
        if action == 'merge':
            session_manager.set_state(user_id, 'MERGE_UPLOAD')
            await query.edit_message_text(
                "📄 *Merge PDFs*\n\n"
                "Send me the PDF files you want to merge (one by one).\n"
                "When done, click the button below.\n\n"
                "⚠️ Max file size: 20 MB",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("✅ Done Uploading", callback_data='merge_complete'),
                    InlineKeyboardButton("🔙 Cancel", callback_data='cancel')
                ]])
            )
        
        elif action == 'rename':
            session_manager.set_state(user_id, 'RENAME_UPLOAD')
            await query.edit_message_text(
                "✏️ *Rename PDF*\n\n"
                "Send me the PDF file you want to rename.\n\n"
                "⚠️ Max file size: 20 MB",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Cancel", callback_data='cancel')
                ]])
            )
        
        elif action == 'watermark':
            session_manager.set_state(user_id, 'WATERMARK_UPLOAD')
            await query.edit_message_text(
                "💧 *Add Watermark*\n\n"
                "Send me the PDF file you want to add a watermark to.\n\n"
                "⚠️ Max file size: 20 MB",
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Cancel", callback_data='cancel')
                ]])
            )
        
        elif action == 'merge_complete':
            await PDFBot.process_merge(query, user_id)
        
        elif action.startswith('watermark_pos_'):
            position = action.replace('watermark_pos_', '')
            session_manager.update_session(user_id, 'watermark_position', position)
            
            keyboard = [
                [InlineKeyboardButton("10%", callback_data='watermark_opacity_0.1')],
                [InlineKeyboardButton("30%", callback_data='watermark_opacity_0.3')],
                [InlineKeyboardButton("50%", callback_data='watermark_opacity_0.5')],
                [InlineKeyboardButton("70%", callback_data='watermark_opacity_0.7')],
                [InlineKeyboardButton("100% (Default)", callback_data='watermark_opacity_1.0')]
            ]
            await query.edit_message_text(
                "Select watermark opacity:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        
        elif action.startswith('watermark_opacity_'):
            opacity = float(action.replace('watermark_opacity_', ''))
            await PDFBot.process_watermark(query, user_id, opacity)
        
        elif action == 'help':
            help_text = (
                "📖 *How to use this bot:*\n\n"
                "*Merge PDFs:*\n"
                "1. Click 'Merge PDFs'\n"
                "2. Send multiple PDF files\n"
                "3. Click 'Done Uploading'\n"
                "4. Receive merged PDF\n\n"
                "*Rename PDF:*\n"
                "1. Click 'Rename PDF'\n"
                "2. Send one PDF file\n"
                "3. Type new filename\n"
                "4. Receive renamed PDF\n\n"
                "*Add Watermark:*\n"
                "1. Click 'Add Watermark'\n"
                "2. Send one PDF file\n"
                "3. Type watermark text\n"
                "4. Select position & opacity\n"
                "5. Receive watermarked PDF\n\n"
                "⚠️ Max file size: 20 MB per file"
            )
            await query.edit_message_text(
                help_text,
                parse_mode='Markdown',
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back to Menu", callback_data='back_to_menu')
                ]])
            )
        
        elif action == 'back_to_menu' or action == 'cancel':
            session_manager.clear_session(user_id)
            keyboard = [
                [InlineKeyboardButton("📄 Merge PDFs", callback_data='merge')],
                [InlineKeyboardButton("✏️ Rename PDF", callback_data='rename')],
                [InlineKeyboardButton("💧 Add Watermark", callback_data='watermark')],
                [InlineKeyboardButton("ℹ️ Help", callback_data='help')]
            ]
            await query.edit_message_text(
                "Choose an option:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    @staticmethod
    async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle PDF file uploads"""
        user_id = update.effective_user.id
        state = session_manager.get_state(user_id)
        
        if not state:
            await update.message.reply_text(
                "Please use /start to begin and select an operation."
            )
            return
        
        document = update.message.document
        
        # Validate file type
        if not document.file_name.lower().endswith('.pdf'):
            await update.message.reply_text(
                "⚠️ Please send only PDF files."
            )
            return
        
        # Validate file size
        if document.file_size > MAX_FILE_SIZE:
            await update.message.reply_text(
                f"⚠️ File is too large. Maximum size is {MAX_FILE_SIZE // (1024*1024)} MB."
            )
            return
        
        # Download file
        await update.message.reply_text("⏳ Downloading file...")
        file = await context.bot.get_file(document.file_id)
        file_path = f"temp/{user_id}_{document.file_name}"
        os.makedirs("temp", exist_ok=True)
        await file.download_to_drive(file_path)
        
        if state == 'MERGE_UPLOAD':
            session_manager.add_pdf(user_id, file_path)
            count = len(session_manager.get_session(user_id).get('pdf_files', []))
            await update.message.reply_text(
                f"✅ File added! Total files: {count}\n"
                "Send more files or click 'Done Uploading' when ready."
            )
        
        elif state == 'RENAME_UPLOAD':
            session_manager.add_pdf(user_id, file_path)
            session_manager.set_state(user_id, 'RENAME_WAIT_NAME')
            await update.message.reply_text(
                "✏️ Now send me the new filename (without .pdf extension):"
            )
        
        elif state == 'WATERMARK_UPLOAD':
            session_manager.add_pdf(user_id, file_path)
            session_manager.set_state(user_id, 'WATERMARK_WAIT_TEXT')
            await update.message.reply_text(
                "💧 Now send me the watermark text:"
            )

    @staticmethod
    async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        state = session_manager.get_state(user_id)
        text = update.message.text
        
        if state == 'RENAME_WAIT_NAME':
            session_manager.update_session(user_id, 'new_name', text)
            await PDFBot.process_rename(update, user_id)
        
        elif state == 'WATERMARK_WAIT_TEXT':
            session_manager.update_session(user_id, 'watermark_text', text)
            session_manager.set_state(user_id, 'WATERMARK_WAIT_POSITION')
            
            keyboard = [
                [InlineKeyboardButton("Center", callback_data='watermark_pos_center')],
                [InlineKeyboardButton("Top", callback_data='watermark_pos_top')],
                [InlineKeyboardButton("Bottom", callback_data='watermark_pos_bottom')],
                [InlineKeyboardButton("Diagonal", callback_data='watermark_pos_diagonal')]
            ]
            await update.message.reply_text(
                "Select watermark position:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

    @staticmethod
    async def process_merge(query, user_id):
        """Process PDF merge operation"""
        session = session_manager.get_session(user_id)
        pdf_files = session.get('pdf_files', [])
        
        if len(pdf_files) < 2:
            await query.edit_message_text(
                "⚠️ Please upload at least 2 PDF files to merge.",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🔙 Back", callback_data='merge')
                ]])
            )
            return
        
        await query.edit_message_text("⏳ Merging PDFs...")
        
        try:
            output_path = f"temp/{user_id}_merged.pdf"
            pdf_handler.merge_pdfs(pdf_files, output_path)
            
            await query.message.reply_document(
                document=open(output_path, 'rb'),
                filename='merged.pdf',
                caption=f"✅ Successfully merged {len(pdf_files)} PDFs!"
            )
            
            # Cleanup
            for file in pdf_files:
                if os.path.exists(file):
                    os.remove(file)
            if os.path.exists(output_path):
                os.remove(output_path)
            
            session_manager.clear_session(user_id)
            await query.edit_message_text(
                "✅ Merge completed! Use /start for more operations."
            )
        
        except Exception as e:
            logger.error(f"Merge error: {e}")
            await query.edit_message_text(
                "❌ An error occurred while merging PDFs. Please try again."
            )

    @staticmethod
    async def process_rename(update, user_id):
        """Process PDF rename operation"""
        session = session_manager.get_session(user_id)
        pdf_file = session.get('pdf_files', [])[0]
        new_name = session.get('new_name', 'renamed')
        
        await update.message.reply_text("⏳ Renaming PDF...")
        
        try:
            output_path = f"temp/{user_id}_{new_name}.pdf"
            pdf_handler.rename_pdf(pdf_file, output_path)
            
            await update.message.reply_document(
                document=open(output_path, 'rb'),
                filename=f"{new_name}.pdf",
                caption=f"✅ File renamed to: {new_name}.pdf"
            )
            
            # Cleanup
            if os.path.exists(pdf_file):
                os.remove(pdf_file)
            if os.path.exists(output_path):
                os.remove(output_path)
            
            session_manager.clear_session(user_id)
            await update.message.reply_text(
                "✅ Rename completed! Use /start for more operations."
            )
        
        except Exception as e:
            logger.error(f"Rename error: {e}")
            await update.message.reply_text(
                "❌ An error occurred while renaming PDF. Please try again."
            )

    @staticmethod
    async def process_watermark(query, user_id, opacity):
        """Process PDF watermark operation"""
        session = session_manager.get_session(user_id)
        pdf_file = session.get('pdf_files', [])[0]
        watermark_text = session.get('watermark_text', '')
        position = session.get('watermark_position', 'center')
        
        await query.edit_message_text("⏳ Adding watermark...")
        
        try:
            output_path = f"temp/{user_id}_watermarked.pdf"
            pdf_handler.add_watermark(pdf_file, output_path, watermark_text, position, opacity)
            
            await query.message.reply_document(
                document=open(output_path, 'rb'),
                filename='watermarked.pdf',
                caption=f"✅ Watermark added: '{watermark_text}'"
            )
            
            # Cleanup
            if os.path.exists(pdf_file):
                os.remove(pdf_file)
            if os.path.exists(output_path):
                os.remove(output_path)
            
            session_manager.clear_session(user_id)
            await query.edit_message_text(
                "✅ Watermark completed! Use /start for more operations."
            )
        
        except Exception as e:
            logger.error(f"Watermark error: {e}")
            await query.edit_message_text(
                "❌ An error occurred while adding watermark. Please try again."
            )

def main():
    """Start the bot"""
    # Get token from environment
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")
    
    # Create application
    application = Application.builder().token(token).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", PDFBot.start))
    application.add_handler(CallbackQueryHandler(PDFBot.button_handler))
    application.add_handler(MessageHandler(filters.Document.PDF, PDFBot.handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, PDFBot.handle_text))
    
    # Start bot
    port = int(os.getenv('PORT', 8443))
    webhook_url = os.getenv('WEBHOOK_URL')
    
    if webhook_url:
        logger.info("Starting webhook mode")
        application.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=f"{webhook_url}/{token}",
            url_path=token
        )
    else:
        logger.info("Starting polling mode")
        application.run_polling()

if __name__ == '__main__':
    main()
