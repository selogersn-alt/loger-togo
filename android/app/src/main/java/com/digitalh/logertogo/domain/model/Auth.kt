package com.digitalh.logertogo.domain.model

data class LoginRequest(
    val username: String, // Souvent le numéro de téléphone ou email
    val password: String
)

data class RegisterRequest(
    val phone_number: String,
    val first_name: String,
    val last_name: String,
    val password: String
)

data class AuthResponse(
    val access: String,
    val refresh: String,
    val user: User? = null
)

data class User(
    val id: String,
    val first_name: String,
    val last_name: String,
    val phone_number: String,
    val role: String,
    val avatar_url: String?
)
