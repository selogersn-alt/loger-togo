import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/colors.dart';
import '../../data/models/chat_model.dart';
import '../../providers/chat_provider.dart';
import '../../providers/auth_provider.dart';

class ConversationScreen extends StatefulWidget {
  final Conversation conversation;
  const ConversationScreen({super.key, required this.conversation});

  @override
  State<ConversationScreen> createState() => _ConversationScreenState();
}

class _ConversationScreenState extends State<ConversationScreen> {
  final TextEditingController _msgController = TextEditingController();

  @override
  void initState() {
    super.initState();
    final auth = context.read<AuthProvider>();
    if (auth.user != null) {
      context.read<ChatProvider>().fetchMessages(widget.conversation.id, auth.user!.id.toString());
    }
  }

  void _sendMessage() {
    if (_msgController.text.trim().isEmpty) return;
    final auth = context.read<AuthProvider>();
    if (auth.user != null) {
      context.read<ChatProvider>().sendMessage(widget.conversation.id, _msgController.text, auth.user!.id.toString());
    }
    _msgController.clear();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        foregroundColor: AppColors.primaryGreen,
        elevation: 0,
        title: Row(
          children: [
            CircleAvatar(
              radius: 18, 
              backgroundColor: AppColors.primaryGreen, 
              child: Text(widget.conversation.otherUserName[0], style: const TextStyle(fontSize: 14, color: Colors.white))
            ),
            const SizedBox(width: 12),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(widget.conversation.otherUserName, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  Text(widget.conversation.topic, style: const TextStyle(fontSize: 10, color: Colors.grey)),
                ],
              ),
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: Consumer<ChatProvider>(
              builder: (context, provider, child) {
                return ListView.builder(
                  padding: const EdgeInsets.all(20),
                  reverse: false,
                  itemCount: provider.messages.length,
                  itemBuilder: (context, index) {
                    final msg = provider.messages[index];
                    return Align(
                      alignment: msg.isMe ? Alignment.centerRight : Alignment.centerLeft,
                      child: Container(
                        margin: const EdgeInsets.only(bottom: 12),
                        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
                        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
                        decoration: BoxDecoration(
                          color: msg.isMe ? AppColors.primaryGreen : AppColors.backgroundLight,
                          borderRadius: BorderRadius.circular(20).copyWith(
                            bottomRight: msg.isMe ? const Radius.circular(0) : const Radius.circular(20),
                            bottomLeft: msg.isMe ? const Radius.circular(20) : const Radius.circular(0),
                          ),
                        ),
                        child: Text(
                          msg.content, 
                          style: TextStyle(color: msg.isMe ? Colors.white : AppColors.textDark, fontSize: 14)
                        ),
                      ),
                    );
                  },
                );
              },
            ),
          ),
          
          // Input Section
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
            decoration: BoxDecoration(
              color: Colors.white, 
              boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, -5))]
            ),
            child: SafeArea(
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _msgController,
                      decoration: InputDecoration(
                        hintText: 'Votre message...',
                        hintStyle: const TextStyle(color: Colors.grey, fontSize: 14),
                        fillColor: AppColors.backgroundLight,
                        filled: true,
                        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(30), borderSide: BorderSide.none),
                      ),
                    ),
                  ),
                  const SizedBox(width: 12),
                  InkWell(
                    onTap: _sendMessage,
                    child: const CircleAvatar(
                      backgroundColor: AppColors.primaryGreen,
                      radius: 24,
                      child: Icon(Icons.send, color: Colors.white, size: 20),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
