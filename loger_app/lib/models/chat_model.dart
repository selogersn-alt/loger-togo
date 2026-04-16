class Conversation {
  final String id;
  final String topic;
  final String topicDisplay;
  final String? relatedProperty;
  final DateTime updatedAt;
  final Message? lastMessage;
  final List<ChatUser> participants;

  Conversation({
    required this.id,
    required this.topic,
    required this.topicDisplay,
    this.relatedProperty,
    required this.updatedAt,
    this.lastMessage,
    required this.participants,
  });

  factory Conversation.fromJson(Map<String, dynamic> json) {
    return Conversation(
      id: json['id'],
      topic: json['topic'] ?? 'GENERAL',
      topicDisplay: json['topic_display'] ?? 'Général',
      relatedProperty: json['related_property'],
      updatedAt: DateTime.parse(json['updated_at']),
      lastMessage: json['last_message'] != null ? Message.fromJson(json['last_message']) : null,
      participants: (json['participants'] as List).map((p) => ChatUser.fromJson(p)).toList(),
    );
  }
}

class Message {
  final String id;
  final String content;
  final String senderName;
  final bool isMe;
  final DateTime createdAt;

  Message({
    required this.id,
    required this.content,
    required this.senderName,
    required this.isMe,
    required this.createdAt,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'],
      content: json['content'] ?? '',
      senderName: json['sender_name'] ?? 'Utilisateur',
      isMe: json['is_me'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

class ChatUser {
  final String id;
  final String displayName;
  final String? profilePicture;

  ChatUser({required this.id, required this.displayName, this.profilePicture});

  factory ChatUser.fromJson(Map<String, dynamic> json) {
    return ChatUser(
      id: json['id'].toString(),
      displayName: json['company_name'] ?? '${json['first_name']} ${json['last_name']}',
      profilePicture: json['profile_picture'],
    );
  }
}
