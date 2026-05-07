package com.digitalh.logertogo.data.remote

import com.digitalh.logertogo.domain.model.*
import retrofit2.http.*

interface ApiService {
    // --- AUTH ---
    @POST("api/users/token/")
    suspend fun login(@Body request: LoginRequest): AuthResponse

    @POST("api/users/register/")
    suspend fun register(@Body request: RegisterRequest): AuthResponse

    @GET("api/users/me/")
    suspend fun getMe(@Header("Authorization") token: String): User

    // --- PROPERTIES ---
    @GET("api/logersn/properties/")
    suspend fun getProperties(
        @Query("city") city: String? = null,
        @Query("property_type") type: String? = null
    ): List<Property>

    @GET("api/geo/nearby/")
    suspend fun getNearbyProperties(
        @Query("lat") lat: Double,
        @Query("lng") lng: Double,
        @Query("radius") radius: Int = 5000
    ): List<Property>

    // --- MESSAGING ---
    @GET("api/conversations/")
    suspend fun getConversations(): List<Conversation>

    @GET("api/conversations/{id}/messages/")
    suspend fun getMessages(@Path("id") conversationId: String): List<Message>

    @POST("api/conversations/{id}/send_message/")
    suspend fun sendMessage(
        @Path("id") conversationId: String,
        @Query("content") content: String
    ): Message
}
