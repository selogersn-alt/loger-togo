package com.digitalh.logertogo.domain.model

data class Conversation(
    val id: String,
    val topic: String,
    val status: String,
    val last_message: String?,
    val updated_at: String,
    val is_expired: Boolean = false
)

data class Message(
    val id: String,
    val sender_name: String,
    val content: String,
    val timestamp: String,
    val is_me: Boolean
)
