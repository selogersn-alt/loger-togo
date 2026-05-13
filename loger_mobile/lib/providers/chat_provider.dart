import 'package:flutter/material.dart';
import '../data/models/chat_model.dart';
import '../core/utils/api_client.dart';

class ChatProvider with ChangeNotifier {
  final ApiClient _apiClient = ApiClient();
  List<Conversation> _conversations = [];
  List<ChatMessage> _messages = [];
  bool _isLoading = false;

  List<Conversation> get conversations => _conversations;
  List<ChatMessage> get messages => _messages;
  bool get isLoading => _isLoading;

  Future<void> fetchConversations() async {
    _isLoading = true;
    notifyListeners();
    try {
      final response = await _apiClient.dio.get('conversations/');
      if (response.statusCode == 200) {
        // Handle potential pagination
        final dynamic data = response.data;
        final List results = (data is Map && data.containsKey('results')) 
            ? data['results'] 
            : (data is List ? data : []);
            
        _conversations = results.map((json) => Conversation.fromJson(json)).toList();
      }
    } catch (e) {
      debugPrint('Error fetching conversations: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchMessages(String conversationId, String currentUserId) async {
    try {
      final response = await _apiClient.dio.get('conversations/$conversationId/messages/');
      if (response.statusCode == 200) {
        final dynamic data = response.data;
        // In DRF, custom actions might not be paginated unless explicitly configured
        final List results = (data is Map && data.containsKey('results')) 
            ? data['results'] 
            : (data is List ? data : []);
            
        _messages = results.map((json) => ChatMessage.fromJson(json, currentUserId)).toList();
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error fetching messages: $e');
    }
  }

  Future<void> sendMessage(String conversationId, String content, String currentUserId) async {
    try {
      final response = await _apiClient.dio.post(
        'conversations/$conversationId/send_message/', // Updated to match @action name
        data: {'content': content},
      );
      if (response.statusCode == 201 || response.statusCode == 200) {
        _messages.add(ChatMessage.fromJson(response.data, currentUserId));
        notifyListeners();
      }
    } catch (e) {
      debugPrint('Error sending message: $e');
    }
  }
}
