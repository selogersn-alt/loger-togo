class Conversation {
  final String id;
  final String topic;
  final String status;
  final String? relatedPropertyTitle;
  final String lastMessage;
  final DateTime updatedAt;
  final String otherUserName; // Added for UI

  Conversation({
    required this.id,
    required this.topic,
    required this.status,
    this.relatedPropertyTitle,
    required this.lastMessage,
    required this.updatedAt,
    this.otherUserName = 'Utilisateur',
  });

  factory Conversation.fromJson(Map<String, dynamic> json) {
    return Conversation(
      id: json['id'],
      topic: json['topic_display'] ?? json['topic'],
      status: json['status'],
      relatedPropertyTitle: json['related_property_title'],
      lastMessage: json['last_message_content'] ?? 'Nouvelle conversation',
      updatedAt: DateTime.parse(json['updated_at']),
      otherUserName: json['other_user_name'] ?? 'Agent Loger Togo',
    );
  }
}

class ChatMessage {
  final String id;
  final String content;
  final String senderId;
  final DateTime createdAt;
  final bool isRead;
  final bool isMe; // Helper for UI

  ChatMessage({
    required this.id,
    required this.content,
    required this.senderId,
    required this.createdAt,
    this.isRead = false,
    this.isMe = false,
  });

  factory ChatMessage.fromJson(Map<String, dynamic> json, String currentUserId) {
    return ChatMessage(
      id: json['id'],
      content: json['content'],
      senderId: json['sender'].toString(),
      createdAt: DateTime.parse(json['created_at']),
      isRead: json['is_read'] ?? false,
      isMe: json['sender'].toString() == currentUserId,
    );
  }
}
