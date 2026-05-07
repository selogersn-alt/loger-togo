package com.digitalh.logertogo.ui.screens.chat

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.digitalh.logertogo.data.remote.ApiService
import com.digitalh.logertogo.domain.model.Conversation
import com.digitalh.logertogo.domain.model.Message
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ChatViewModel @Inject constructor(
    private val apiService: ApiService
) : ViewModel() {

    private val _conversations = MutableStateFlow<List<Conversation>>(emptyList())
    val conversations: StateFlow<List<Conversation>> = _conversations

    private val _messages = MutableStateFlow<List<Message>>(emptyList())
    val messages: StateFlow<List<Message>> = _messages

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    init {
        loadConversations()
    }

    fun loadConversations() {
        viewModelScope.launch {
            try {
                _conversations.value = apiService.getConversations()
            } catch (e: Exception) {
                // Gérer l'erreur
            }
        }
    }

    fun loadMessages(conversationId: String) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                _messages.value = apiService.getMessages(conversationId)
            } catch (e: Exception) {
                // Gérer l'erreur
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun sendMessage(conversationId: String, content: String) {
        viewModelScope.launch {
            try {
                val newMessage = apiService.sendMessage(conversationId, content)
                _messages.value = _messages.value + newMessage
            } catch (e: Exception) {
                // Gérer l'erreur
            }
        }
    }

    // Polling simulation (temps réel)
    fun startPolling(conversationId: String) {
        viewModelScope.launch {
            while (true) {
                delay(5000)
                try {
                    _messages.value = apiService.getMessages(conversationId)
                } catch (e: Exception) {}
            }
        }
    }
}
