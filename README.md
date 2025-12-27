# Telegram PDF Utility Bot

A powerful Telegram bot for PDF operations including merge, rename, and watermarking capabilities.

## Features

✨ **Merge PDFs** - Combine multiple PDF files into one  
✏️ **Rename PDFs** - Rename PDF files easily  
💧 **Add Watermarks** - Add customizable text watermarks to PDFs

## Tech Stack

- **Python 3.9+**
- **python-telegram-bot** - Telegram Bot API wrapper
- **PyPDF2** - PDF manipulation
- **ReportLab** - PDF watermark generation
- **MongoDB** (Optional) - Session management
- **Render.com** - Hosting platform

## Project Structure

```
telegram-pdf-bot/
├── bot.py                 # Main bot application
├── pdf_handler.py         # PDF operations (merge, rename, watermark)
├── session_manager.py     # User session management
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # Documentation
```

## Installation

### Local Development

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd telegram-pdf-bot
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your values
```

5. **Create a Telegram Bot**
   - Open Telegram and search for [@BotFather](https://t.me/botfather)
   - Send `/newbot` and follow the instructions
   - Copy the bot token
   - Paste it in your `.env` file

6. **Run the bot (polling mode)**
```bash
python bot.py
```

### MongoDB Setup (Optional)

MongoDB is optional. The bot will work with in-memory storage if MongoDB is not configured.

**To use MongoDB:**

1. Create a free cluster at [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Get your connection string
3. Add it to your `.env` file as `MONGODB_URI`

## Deployment on Render.com

### Step 1: Prepare Your Repository

1. Push your code to GitHub/GitLab
2. Make sure all files are committed

### Step 2: Create Web Service on Render

1. Go to [Render.com](https://render.com) and sign in
2. Click "New +" → "Web Service"
3. Connect your repository
4. Configure:
   - **Name**: `pdf-bot` (or your choice)
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`

### Step 3: Set Environment Variables

In Render dashboard, add these environment variables:

- `TELEGRAM_BOT_TOKEN` - Your bot token from BotFather
- `WEBHOOK_URL` - Your Render app URL (e.g., `https://pdf-bot.onrender.com`)
- `MONGODB_URI` - (Optional) Your MongoDB connection string
- `PORT` - Will be set automatically by Render

### Step 4: Deploy

1. Click "Create Web Service"
2. Wait for deployment to complete
3. Your bot is now live!

### Step 5: Set Webhook

The bot will automatically set up the webhook when it starts. No manual configuration needed!

## Usage

### Start the Bot
1. Open Telegram and search for your bot
2. Send `/start`

### Merge PDFs
1. Click "📄 Merge PDFs"
2. Send multiple PDF files (one by one)
3. Click "✅ Done Uploading"
4. Receive your merged PDF

### Rename PDF
1. Click "✏️ Rename PDF"
2. Send one PDF file
3. Type the new filename (without .pdf)
4. Receive your renamed PDF

### Add Watermark
1. Click "💧 Add Watermark"
2. Send one PDF file
3. Type watermark text
4. Select position (center/top/bottom/diagonal)
5. Select opacity (10%-100%)
6. Receive your watermarked PDF

## Configuration

### Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | Bot token from @BotFather |
| `WEBHOOK_URL` | Yes (Render) | Your app URL for webhook |
| `MONGODB_URI` | No | MongoDB connection string |
| `PORT` | No | Server port (auto-set by Render) |

### Limits

- **Max file size**: 20 MB per PDF
- **Merge**: Minimum 2 PDFs required
- **Session timeout**: 1 hour of inactivity

## Features Details

### PDF Merge
- Supports unlimited number of PDFs (within size limits)
- Maintains original page order
- Preserves PDF metadata
- Automatic cleanup of temporary files

### PDF Rename
- Simple and fast renaming
- Preserves PDF structure and quality
- No metadata modification

### PDF Watermark
- **Positions**: Center, Top, Bottom, Diagonal
- **Opacity**: 10%, 30%, 50%, 70%, 100%
- **Coverage**: Applied to all pages
- **Customizable text**: Any text supported

## Error Handling

The bot includes comprehensive error handling:
- Invalid file type detection
- File size validation
- Graceful failure messages
- Automatic session cleanup
- Temporary file management

## Troubleshooting

### Bot not responding
- Check if `TELEGRAM_BOT_TOKEN` is correct
- Verify Render service is running
- Check Render logs for errors

### Webhook issues
- Ensure `WEBHOOK_URL` matches your Render URL
- Check if HTTPS is enabled
- Verify PORT is correctly set

### MongoDB connection failed
- Bot will automatically fallback to in-memory storage
- Check your `MONGODB_URI` format
- Verify MongoDB cluster is accessible

### PDF processing errors
- Ensure PDFs are not corrupted
- Check file size is under 20 MB
- Verify PDF is not password-protected

## Development

### Running Tests
```bash
# Add your test commands here
python -m pytest tests/
```

### Code Structure

**bot.py** - Main application
- Telegram bot handlers
- User interface logic
- Command routing

**pdf_handler.py** - PDF operations
- Merge functionality
- Rename functionality
- Watermark generation

**session_manager.py** - Session management
- MongoDB integration
- In-memory fallback
- Automatic cleanup

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## License

MIT License - feel free to use this project for any purpose.

## Support

For issues and questions:
- Open a GitHub issue
- Check existing issues for solutions
- Review Render logs for deployment issues

## Roadmap

Potential future features:
- [ ] PDF compression
- [ ] Image to PDF conversion
- [ ] PDF splitting
- [ ] Password protection
- [ ] PDF metadata editing
- [ ] OCR support
- [ ] Batch processing

## Credits

Built with:
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [PyPDF2](https://github.com/py-pdf/PyPDF2)
- [ReportLab](https://www.reportlab.com/)
- [MongoDB](https://www.mongodb.com/)

---

Made with ❤️ for the Telegram community
