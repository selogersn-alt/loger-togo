package com.logertogo.app.data.api

import com.logertogo.app.data.model.*
import okhttp3.MultipartBody
import okhttp3.RequestBody
import retrofit2.Response
import retrofit2.http.*

// ═══════════════════════════════════════════════════════════
// Interface API Retrofit2 → Consomme le backend Django DRF
// BASE_URL : https://www.logertogo.com/api/v1/
// ═══════════════════════════════════════════════════════════

interface LogerTogoApi {

    // ── AUTHENTIFICATION (JWT via SimpleJWT) ──────────────
    @POST("auth/token/")
    suspend fun login(@Body request: LoginRequest): Response<AuthTokens>

    @POST("auth/token/refresh/")
    suspend fun refreshToken(@Body body: Map<String, String>): Response<AuthTokens>

    @POST("auth/register/")
    suspend fun register(@Body body: Map<String, String>): Response<User>

    @GET("auth/me/")
    suspend fun getProfile(
        @Header("Authorization") token: String
    ): Response<User>

    // ── ANNONCES IMMOBILIÈRES ──────────────────────────────
    @GET("properties/")
    suspend fun getProperties(
        @Header("Authorization") token: String = "",
        @Query("page") page: Int = 1,
        @Query("city") city: String? = null,
        @Query("property_type") propertyType: String? = null,
        @Query("listing_category") listingCategory: String? = null,
        @Query("query") query: String? = null,
        @Query("min_price") minPrice: Int? = null,
        @Query("max_price") maxPrice: Int? = null
    ): Response<PaginatedProperties>

    @GET("properties/boosted/")
    suspend fun getBoostedProperties(
        @Query("page") page: Int = 1
    ): Response<PaginatedProperties>

    @GET("properties/{id}/")
    suspend fun getPropertyDetail(
        @Header("Authorization") token: String = "",
        @Path("id") id: String
    ): Response<Property>

    @Multipart
    @POST("properties/")
    suspend fun createProperty(
        @Header("Authorization") token: String,
        @Part("title") title: RequestBody,
        @Part("description") description: RequestBody,
        @Part("price") price: RequestBody,
        @Part("city") city: RequestBody,
        @Part("neighborhood") neighborhood: RequestBody,
        @Part("property_type") propertyType: RequestBody,
        @Part("listing_category") listingCategory: RequestBody,
        @Part images: List<MultipartBody.Part>
    ): Response<Property>

    @Multipart
    @PATCH("properties/{id}/")
    suspend fun updateProperty(
        @Header("Authorization") token: String,
        @Path("id") id: String,
        @PartMap fields: Map<String, @JvmSuppressWildcards RequestBody>
    ): Response<Property>

    @DELETE("properties/{id}/")
    suspend fun deleteProperty(
        @Header("Authorization") token: String,
        @Path("id") id: String
    ): Response<Unit>

    // ── MESSAGERIE SOCIALE ─────────────────────────────────
    @GET("chat/conversations/")
    suspend fun getConversations(
        @Header("Authorization") token: String
    ): Response<List<Conversation>>

    @GET("chat/conversations/{id}/messages/")
    suspend fun getMessages(
        @Header("Authorization") token: String,
        @Path("id") conversationId: String
    ): Response<List<Message>>

    @Multipart
    @POST("chat/conversations/{id}/messages/")
    suspend fun sendMessage(
        @Header("Authorization") token: String,
        @Path("id") conversationId: String,
        @Part("content") content: RequestBody,
        @Part attachment: MultipartBody.Part? = null
    ): Response<Message>

    @POST("chat/conversations/start/{property_id}/")
    suspend fun startConversation(
        @Header("Authorization") token: String,
        @Path("property_id") propertyId: String
    ): Response<Conversation>

    @PATCH("chat/conversations/{id}/status/")
    suspend fun updateConversationStatus(
        @Header("Authorization") token: String,
        @Path("id") conversationId: String,
        @Body body: Map<String, String>
    ): Response<Conversation>

    // ── FAVORIS ───────────────────────────────────────────
    @POST("properties/{id}/favorite/")
    suspend fun toggleFavorite(
        @Header("Authorization") token: String,
        @Path("id") propertyId: String
    ): Response<Map<String, Any>>

    @GET("properties/favorites/")
    suspend fun getFavorites(
        @Header("Authorization") token: String
    ): Response<List<Property>>
}
