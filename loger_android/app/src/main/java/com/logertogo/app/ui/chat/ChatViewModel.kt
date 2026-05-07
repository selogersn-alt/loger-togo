package com.logertogo.app.ui.chat

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.logertogo.app.data.api.RetrofitClient
import com.logertogo.app.data.api.TokenManager
import com.logertogo.app.data.model.ApiResponse
import com.logertogo.app.data.model.Conversation
import com.logertogo.app.data.model.Message
import kotlinx.coroutines.Job
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import okhttp3.MultipartBody
import okhttp3.RequestBody.Companion.toRequestBody

class ChatViewModel(application: Application) : AndroidViewModel(application) {

    private val api = RetrofitClient.getInstance()
    private val context = application.applicationContext
    private var pollingJob: Job? = null

    private val _conversations = MutableLiveData<ApiResponse<List<Conversation>>>()
    val conversations: LiveData<ApiResponse<List<Conversation>>> = _conversations

    private val _conversation = MutableLiveData<Conversation?>()
    val conversation: LiveData<Conversation?> = _conversation

    private val _messages = MutableLiveData<List<Message>>(emptyList())
    val messages: LiveData<List<Message>> = _messages

    private val _sendState = MutableLiveData<ApiResponse<Message>>()
    val sendState: LiveData<ApiResponse<Message>> = _sendState

    fun loadConversations() {
        _conversations.value = ApiResponse.loading()
        viewModelScope.launch {
            try {
                val token = TokenManager.getAccessToken(context) ?: run {
                    _conversations.value = ApiResponse.error("Non connecté")
                    return@launch
                }
                val response = api.getConversations(TokenManager.bearerHeader(token))
                if (response.isSuccessful && response.body() != null) {
                    _conversations.value = ApiResponse.success(response.body()!!)
                } else {
                    _conversations.value = ApiResponse.error("Erreur chargement discussions")
                }
            } catch (e: Exception) {
                _conversations.value = ApiResponse.error(e.localizedMessage ?: "Erreur réseau")
            }
        }
    }

    fun loadConversation(conversationId: String) {
        viewModelScope.launch {
            try {
                val token = TokenManager.getAccessToken(context) ?: return@launch
                val response = api.getConversations(TokenManager.bearerHeader(token))
                if (response.isSuccessful) {
                    val conv = response.body()?.find { it.id == conversationId }
                    _conversation.value = conv
                }
            } catch (e: Exception) { /* Silencieux */ }
        }
    }

    fun loadMessages(conversationId: String) {
        viewModelScope.launch {
            try {
                val token = TokenManager.getAccessToken(context) ?: return@launch
                val response = api.getMessages(TokenManager.bearerHeader(token), conversationId)
                if (response.isSuccessful && response.body() != null) {
                    _messages.value = response.body()!!
                }
            } catch (e: Exception) { /* Silencieux */ }
        }
    }

    /**
     * Polling toutes les 3 secondes pour simuler le temps réel
     * (Alternative légère à WebSocket)
     */
    fun startPolling(conversationId: String) {
        stopPolling()
        pollingJob = viewModelScope.launch {
            while (isActive) {
                delay(3000)
                try {
                    val token = TokenManager.getAccessToken(context) ?: break
                    val response = api.getMessages(TokenManager.bearerHeader(token), conversationId)
                    if (response.isSuccessful && response.body() != null) {
                        val newMessages = response.body()!!
                        // Mettre à jour seulement si il y a de nouveaux messages
                        if (newMessages.size != (_messages.value?.size ?: 0)) {
                            _messages.postValue(newMessages)
                        }
                    }
                } catch (e: Exception) { /* Silencieux */ }
            }
        }
    }

    fun stopPolling() {
        pollingJob?.cancel()
        pollingJob = null
    }

    fun sendMessage(conversationId: String, content: String, attachment: MultipartBody.Part?) {
        _sendState.value = ApiResponse.loading()
        viewModelScope.launch {
            try {
                val token = TokenManager.getAccessToken(context) ?: run {
                    _sendState.value = ApiResponse.error("Non connecté")
                    return@launch
                }
                val contentBody = content.toRequestBody()
                val response = api.sendMessage(
                    token = TokenManager.bearerHeader(token),
                    conversationId = conversationId,
                    content = contentBody,
                    attachment = attachment
                )
                if (response.isSuccessful && response.body() != null) {
                    _sendState.value = ApiResponse.success(response.body()!!)
                    // Ajouter le message localement immédiatement (optimistic update)
                    val currentMessages = _messages.value.orEmpty().toMutableList()
                    currentMessages.add(response.body()!!)
                    _messages.value = currentMessages
                } else {
                    _sendState.value = ApiResponse.error("Impossible d'envoyer le message")
                }
            } catch (e: Exception) {
                _sendState.value = ApiResponse.error(e.localizedMessage ?: "Erreur réseau")
            }
        }
    }

    fun updateStatus(conversationId: String, status: String) {
        viewModelScope.launch {
            try {
                val token = TokenManager.getAccessToken(context) ?: return@launch
                val response = api.updateConversationStatus(
                    token = TokenManager.bearerHeader(token),
                    conversationId = conversationId,
                    body = mapOf("status" to status)
                )
                if (response.isSuccessful && response.body() != null) {
                    _conversation.value = response.body()
                }
            } catch (e: Exception) { /* Silencieux */ }
        }
    }

    override fun onCleared() {
        super.onCleared()
        stopPolling()
    }
}
