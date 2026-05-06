import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:animate_do/animate_do.dart';
import '../models/chat_model.dart';
import '../services/api_service.dart';
import 'chat_detail_screen.dart';

class ConversationListScreen extends StatefulWidget {
  const ConversationListScreen({super.key});

  @override
  State<ConversationListScreen> createState() => _ConversationListScreenState();
}

class _ConversationListScreenState extends State<ConversationListScreen> {
  final ApiService _apiService = ApiService();
  late Future<List<dynamic>> _conversationsFuture;

  @override
  void initState() {
    super.initState();
    _refreshConversations();
  }

  void _refreshConversations() {
    setState(() {
      _conversationsFuture = _apiService.fetchConversations();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Messages', style: TextStyle(fontWeight: FontWeight.w900, color: Colors.black)),
        centerTitle: true,
        backgroundColor: Colors.white,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: Color(0xFF004D40)),
            onPressed: _refreshConversations,
          ),
        ],
      ),
      body: FutureBuilder<List<dynamic>>(
        future: _conversationsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator(color: Color(0xFF004D40)));
          }

          if (snapshot.hasError) {
            return _buildErrorState();
          }

          final conversations = (snapshot.data ?? [])
              .map((json) => Conversation.fromJson(json))
              .toList();

          if (conversations.isEmpty) {
            return _buildEmptyState();
          }

          return ListView.builder(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            itemCount: conversations.length,
            itemBuilder: (context, index) {
              final conv = conversations[index];
              return FadeInUp(
                delay: Duration(milliseconds: index * 100),
                child: _buildConversationTile(conv),
              );
            },
          );
        },
      ),
    );
  }

  Widget _buildConversationTile(Conversation conv) {
    // Determine the other participant
    final otherParticipant = conv.participants.firstWhere(
      (p) => true, // In a real app, filter out 'me'
      orElse: () => ChatUser(id: '0', displayName: 'Support'),
    );

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.03),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ListTile(
        contentPadding: const EdgeInsets.all(12),
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => ChatDetailScreen(conversation: conv),
            ),
          ).then((_) => _refreshConversations());
        },
        leading: Stack(
          children: [
            CircleAvatar(
              radius: 28,
              backgroundColor: const Color(0xFF004D40).withValues(alpha: 0.1),
              backgroundImage: otherParticipant.profilePicture != null
                  ? NetworkImage(otherParticipant.profilePicture!)
                  : null,
              child: otherParticipant.profilePicture == null
                  ? Text(
                      otherParticipant.displayName[0],
                      style: const TextStyle(fontWeight: FontWeight.bold, color: Color(0xFF004D40)),
                    )
                  : null,
            ),
            Positioned(
              right: 0,
              bottom: 0,
              child: Container(
                width: 12,
                height: 12,
                decoration: BoxDecoration(
                  color: Colors.green,
                  shape: BoxShape.circle,
                  border: Border.all(color: Colors.white, width: 2),
                ),
              ),
            ),
          ],
        ),
        title: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Expanded(
              child: Text(
                otherParticipant.displayName,
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
              ),
            ),
            Text(
              DateFormat('HH:mm').format(conv.updatedAt),
              style: TextStyle(fontSize: 12, color: Colors.grey.shade400),
            ),
          ],
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 4),
          child: Row(
            children: [
              Expanded(
                child: Text(
                  conv.lastMessage?.content ?? 'Pas de message',
                  style: TextStyle(
                    color: Colors.blueGrey.shade400,
                    fontSize: 13,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              if (conv.topic != 'GENERAL')
                Container(
                  margin: const EdgeInsets.only(left: 8),
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.amber.shade50,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Text(
                    'BIEN',
                    style: TextStyle(fontSize: 9, color: Colors.amber, fontWeight: FontWeight.bold),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.forum_outlined, size: 80, color: Colors.grey.shade200),
          const SizedBox(height: 20),
          const Text(
            'Aucune conversation',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.blueGrey),
          ),
          const SizedBox(height: 8),
          const Text(
            'Vos messages avec les bailleurs s\'afficheront ici.',
            style: TextStyle(color: Colors.grey),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline_rounded, size: 60, color: Colors.redAccent),
          const SizedBox(height: 16),
          const Text('Impossible de charger les messages'),
          TextButton(
            onPressed: _refreshConversations,
            child: const Text('Réessayer'),
          ),
        ],
      ),
    );
  }
}
