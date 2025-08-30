#!/usr/bin/env python3
"""
Chatbot Database Client
A MySQL client script to interact with the chatbot conversations database.
"""

import mysql.connector
import os
from datetime import datetime
from dotenv import load_dotenv
import json
from typing import List, Dict, Any

load_dotenv()

class ChatbotDBClient:
    def __init__(self):
        """Initialize database connection using environment variables."""
        self.connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_USER"),
            database=os.getenv("DB_NAME")
        )
        self.cursor = self.connection.cursor(dictionary=True)
        print("✅ Connected to MySQL database")
    
    def close(self):
        """Close database connection."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        print("🔌 Database connection closed")
    
    def get_conversation_count(self) -> int:
        """Get total number of conversations."""
        query = "SELECT COUNT(*) as count FROM chatbot_conversations"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result['count'] if result else 0
    
    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent conversations."""
        query = """
        SELECT conversation_id, user_id, message, response, confidence, 
               recommendation, created_at
        FROM chatbot_conversations 
        ORDER BY created_at DESC 
        LIMIT %s
        """
        self.cursor.execute(query, (limit,))
        return self.cursor.fetchall()
    
    def get_conversations_by_user(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all conversations for a specific user."""
        query = """
        SELECT conversation_id, message, response, confidence, 
               recommendation, created_at
        FROM chatbot_conversations 
        WHERE user_id = %s
        ORDER BY created_at DESC
        """
        self.cursor.execute(query, (user_id,))
        return self.cursor.fetchall()
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get conversation statistics."""
        # Total conversations
        total_query = "SELECT COUNT(*) as count FROM chatbot_conversations"
        self.cursor.execute(total_query)
        total = self.cursor.fetchone()['count']
        
        # Conversations by user
        user_stats_query = """
        SELECT user_id, COUNT(*) as count 
        FROM chatbot_conversations 
        GROUP BY user_id
        """
        self.cursor.execute(user_stats_query)
        user_stats = {row['user_id'] or 'anonymous': row['count'] for row in self.cursor.fetchall()}
        
        # Confidence distribution
        confidence_query = """
        SELECT confidence, COUNT(*) as count 
        FROM chatbot_conversations 
        GROUP BY confidence
        """
        self.cursor.execute(confidence_query)
        confidence_stats = {row['confidence']: row['count'] for row in self.cursor.fetchall()}
        
        # Recent activity (last 24 hours)
        recent_query = """
        SELECT COUNT(*) as count 
        FROM chatbot_conversations 
        WHERE created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
        """
        self.cursor.execute(recent_query)
        last_24h = self.cursor.fetchone()['count']
        
        return {
            'total_conversations': total,
            'conversations_by_user': user_stats,
            'confidence_distribution': confidence_stats,
            'last_24h_conversations': last_24h
        }
    
    def search_conversations(self, search_term: str) -> List[Dict[str, Any]]:
        """Search conversations by message or response content."""
        query = """
        SELECT conversation_id, user_id, message, response, confidence, 
               recommendation, created_at
        FROM chatbot_conversations 
        WHERE message LIKE %s OR response LIKE %s
        ORDER BY created_at DESC
        """
        search_pattern = f"%{search_term}%"
        self.cursor.execute(query, (search_pattern, search_pattern))
        return self.cursor.fetchall()
    
    def get_conversation_by_id(self, conversation_id: int) -> Dict[str, Any]:
        """Get a specific conversation by ID."""
        query = """
        SELECT conversation_id, user_id, message, response, confidence, 
               recommendation, created_at
        FROM chatbot_conversations 
        WHERE conversation_id = %s
        """
        self.cursor.execute(query, (conversation_id,))
        return self.cursor.fetchone()
    
    def export_conversations(self, filename: str = None) -> str:
        """Export all conversations to a JSON file."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chatbot_conversations_{timestamp}.json"
        
        query = """
        SELECT conversation_id, user_id, message, response, confidence, 
               recommendation, created_at
        FROM chatbot_conversations 
        ORDER BY created_at DESC
        """
        self.cursor.execute(query)
        conversations = self.cursor.fetchall()
        
        # Convert datetime objects to strings for JSON serialization
        for conv in conversations:
            if conv['created_at']:
                conv['created_at'] = conv['created_at'].isoformat()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(conversations, f, indent=2, ensure_ascii=False)
        
        return filename

def print_conversation(conv: Dict[str, Any]):
    """Pretty print a conversation."""
    print(f"\n{'='*80}")
    print(f"Conversation ID: {conv['conversation_id']}")
    print(f"User ID: {conv['user_id'] or 'Anonymous'}")
    print(f"Time: {conv['created_at']}")
    print(f"Confidence: {conv['confidence']}")
    print(f"\nUser Message:")
    print(f"  {conv['message']}")
    print(f"\nBot Response:")
    print(f"  {conv['response']}")
    if conv['recommendation']:
        print(f"\nRecommendation:")
        print(f"  {conv['recommendation']}")
    print(f"{'='*80}")

def main():
    """Main interactive menu."""
    client = None
    try:
        client = ChatbotDBClient()
        
        while True:
            print("\n" + "="*50)
            print("🤖 CHATBOT DATABASE CLIENT")
            print("="*50)
            print("1. View total conversation count")
            print("2. View recent conversations")
            print("3. View conversation statistics")
            print("4. Search conversations")
            print("5. View conversations by user")
            print("6. View specific conversation")
            print("7. Export conversations to JSON")
            print("8. Exit")
            print("-"*50)
            
            choice = input("Enter your choice (1-8): ").strip()
            
            if choice == '1':
                count = client.get_conversation_count()
                print(f"\n📊 Total conversations: {count}")
                
            elif choice == '2':
                limit = input("Number of conversations to show (default 10): ").strip()
                limit = int(limit) if limit.isdigit() else 10
                conversations = client.get_recent_conversations(limit)
                print(f"\n📝 Recent {len(conversations)} conversations:")
                for conv in conversations:
                    print_conversation(conv)
                    
            elif choice == '3':
                stats = client.get_conversation_stats()
                print("\n📈 CONVERSATION STATISTICS:")
                print(f"Total conversations: {stats['total_conversations']}")
                print(f"Last 24 hours: {stats['last_24h_conversations']}")
                print("\nBy User:")
                for user, count in stats['conversations_by_user'].items():
                    print(f"  {user}: {count}")
                print("\nBy Confidence:")
                for confidence, count in stats['confidence_distribution'].items():
                    print(f"  {confidence}: {count}")
                    
            elif choice == '4':
                search_term = input("Enter search term: ").strip()
                if search_term:
                    conversations = client.search_conversations(search_term)
                    print(f"\n🔍 Found {len(conversations)} conversations matching '{search_term}':")
                    for conv in conversations:
                        print_conversation(conv)
                else:
                    print("❌ Please enter a search term")
                    
            elif choice == '5':
                user_id = input("Enter user ID: ").strip()
                if user_id:
                    conversations = client.get_conversations_by_user(user_id)
                    print(f"\n👤 Conversations for user '{user_id}': {len(conversations)} found")
                    for conv in conversations:
                        print_conversation(conv)
                else:
                    print("❌ Please enter a user ID")
                    
            elif choice == '6':
                conv_id = input("Enter conversation ID: ").strip()
                if conv_id.isdigit():
                    conv = client.get_conversation_by_id(int(conv_id))
                    if conv:
                        print_conversation(conv)
                    else:
                        print(f"❌ Conversation {conv_id} not found")
                else:
                    print("❌ Please enter a valid conversation ID")
                    
            elif choice == '7':
                filename = input("Enter filename (or press Enter for auto-generated): ").strip()
                if not filename:
                    filename = None
                exported_file = client.export_conversations(filename)
                print(f"✅ Conversations exported to: {exported_file}")
                
            elif choice == '8':
                print("👋 Goodbye!")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-8.")
                
            input("\nPress Enter to continue...")
            
    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        if client:
            client.close()

if __name__ == "__main__":
    main()
