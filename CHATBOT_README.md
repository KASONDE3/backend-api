# 🤖 IT FAQ Chatbot with Database Storage

This chatbot system provides IT support FAQ functionality while storing all conversations in a MySQL database for analysis and tracking.

## 🚀 Features

### Chatbot Capabilities
- **IT Support FAQ**: Provides basic troubleshooting guidance for common IT issues
- **Safety Restrictions**: Automatically refers complex issues to IT support
- **Confidence Levels**: Each response includes confidence rating (high/medium/low)
- **Recommendations**: Always provides next steps for users

### Database Storage
- **Complete History**: Stores all user queries, bot responses, and metadata
- **User Tracking**: Links conversations to specific users (optional)
- **Timestamps**: Records when each conversation occurred
- **Analytics**: Provides conversation statistics and insights

## 📊 Database Schema

The chatbot creates a `chatbot_conversations` table with the following structure:

```sql
CREATE TABLE chatbot_conversations (
    conversation_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id VARCHAR(255) NULL,  -- Can be null for anonymous users
    message TEXT NOT NULL,       -- User's question/message
    response TEXT NOT NULL,      -- Bot's response
    confidence VARCHAR(20) NOT NULL,  -- high/medium/low
    recommendation TEXT NULL,    -- Bot's recommendation
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_time (user_id, created_at),
    INDEX idx_time (created_at)
);
```

## 🔌 API Endpoints

### Main Chat Endpoint
- **POST** `/chatbot/chat`
  - Send user messages and receive IT support guidance
  - Automatically stores conversation in database

### Database Query Endpoints
- **GET** `/chatbot/conversations` - Get conversation history with pagination
- **GET** `/chatbot/conversations/summary` - Get conversation statistics
- **GET** `/chatbot/conversations/{id}` - Get specific conversation by ID

### Utility Endpoints
- **GET** `/chatbot/health` - Service health check
- **GET** `/chatbot/capabilities` - What the chatbot can/cannot do

## 🛠️ Setup Instructions

### 1. Environment Variables
Ensure your `.env` file contains:
```env
GEMINI_API_KEY=your_gemini_api_key_here
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=your_database_name
```

### 2. Database Migration
The chatbot table will be automatically created when you start the application, as the model is registered in `db.py`.

### 3. Install Dependencies
```bash
pip install -r requirements_chatbot.txt
```

## 📱 Usage Examples

### Using the Chatbot API
```bash
# Send a message to the chatbot
curl -X POST "http://localhost:8000/chatbot/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "My printer is not working",
    "user_id": "user123"
  }'
```

### Response Format
```json
{
  "response": "Let's try some basic troubleshooting steps for your printer...",
  "confidence": "high",
  "recommendation": "Contact IT support if this doesn't resolve your issue"
}
```

## 🗄️ Database Client

Use the included `chatbot_db_client.py` script to interact with the database:

```bash
python chatbot_db_client.py
```

### Client Features
- View total conversation count
- Browse recent conversations
- Get conversation statistics
- Search conversations by content
- Filter conversations by user
- Export conversations to JSON
- Interactive menu interface

## 📈 Analytics & Insights

### Conversation Statistics
- Total conversations
- Conversations by user
- Confidence level distribution
- Recent activity (last 24 hours)

### Use Cases
- **IT Support Analytics**: Track common issues and bot effectiveness
- **User Behavior**: Understand what users ask about most
- **Quality Assurance**: Monitor bot confidence levels
- **Training Data**: Use conversations to improve bot responses

## 🔒 Security & Privacy

- **User ID Optional**: Users can remain anonymous
- **No Sensitive Data**: Only stores conversation content, not personal information
- **Database Security**: Follows your existing database security practices
- **API Protection**: Integrate with your existing authentication system

## 🚨 Troubleshooting

### Common Issues
1. **Gemini API Key Missing**: Ensure `GEMINI_API_KEY` is set in `.env`
2. **Database Connection**: Check database credentials and connectivity
3. **Table Creation**: Verify the model is imported in `db.py`

### Logs
The chatbot logs all activities including:
- User requests
- API responses
- Database operations
- Errors and exceptions

## 🔄 Future Enhancements

- **Conversation Threading**: Link related conversations
- **User Feedback**: Allow users to rate bot responses
- **Advanced Analytics**: Machine learning insights
- **Integration**: Connect with ticket system for escalation
- **Multi-language Support**: Support for different languages

## 📞 Support

For technical support or questions about the chatbot system, contact your IT development team.
