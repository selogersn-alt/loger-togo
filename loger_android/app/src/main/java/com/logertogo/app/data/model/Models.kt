package com.logertogo.app.data.model

import com.google.gson.annotations.SerializedName

// ═══════════════════════════════════════════
// Modèles de données (mappent les API Django)
// ═══════════════════════════════════════════

data class AuthTokens(
    @SerializedName("access") val access: String,
    @SerializedName("refresh") val refresh: String
)

data class LoginRequest(
    @SerializedName("email") val email: String,
    @SerializedName("password") val password: String
)

data class User(
    @SerializedName("id") val id: String,
    @SerializedName("email") val email: String,
    @SerializedName("first_name") val firstName: String,
    @SerializedName("last_name") val lastName: String,
    @SerializedName("phone") val phone: String?,
    @SerializedName("role") val role: String,
    @SerializedName("is_verified_pro") val isVerifiedPro: Boolean,
    @SerializedName("avatar") val avatar: String?
)

data class PropertyImage(
    @SerializedName("id") val id: String,
    @SerializedName("image") val image: String,
    @SerializedName("is_primary") val isPrimary: Boolean
)

data class Property(
    @SerializedName("id") val id: String,
    @SerializedName("title") val title: String,
    @SerializedName("description") val description: String,
    @SerializedName("price") val price: Double,
    @SerializedName("city") val city: String,
    @SerializedName("neighborhood") val neighborhood: String,
    @SerializedName("property_type") val propertyType: String,
    @SerializedName("listing_category") val listingCategory: String,
    @SerializedName("rooms") val rooms: Int?,
    @SerializedName("bathrooms") val bathrooms: Int?,
    @SerializedName("area") val area: Double?,
    @SerializedName("is_published") val isPublished: Boolean,
    @SerializedName("is_boosted") val isBoosted: Boolean,
    @SerializedName("views_count") val viewsCount: Int,
    @SerializedName("images") val images: List<PropertyImage>,
    @SerializedName("owner") val owner: User?,
    @SerializedName("created_at") val createdAt: String,
    // Équipements
    @SerializedName("wifi") val wifi: Boolean,
    @SerializedName("air_conditioning") val airConditioning: Boolean,
    @SerializedName("swimming_pool") val swimmingPool: Boolean,
    @SerializedName("generator") val generator: Boolean,
    @SerializedName("water_tank") val waterTank: Boolean,
    @SerializedName("latitude") val latitude: Double?,
    @SerializedName("longitude") val longitude: Double?
) {
    val mainImage: String
        get() = images.firstOrNull { it.isPrimary }?.image
            ?: images.firstOrNull()?.image
            ?: ""
}

data class PaginatedProperties(
    @SerializedName("count") val count: Int,
    @SerializedName("next") val next: String?,
    @SerializedName("previous") val previous: String?,
    @SerializedName("results") val results: List<Property>
)

data class Conversation(
    @SerializedName("id") val id: String,
    @SerializedName("topic") val topic: String,
    @SerializedName("status") val status: String,
    @SerializedName("participants") val participants: List<User>,
    @SerializedName("related_property") val relatedProperty: Property?,
    @SerializedName("updated_at") val updatedAt: String
)

data class Message(
    @SerializedName("id") val id: String,
    @SerializedName("conversation") val conversation: String,
    @SerializedName("sender") val sender: User,
    @SerializedName("content") val content: String,
    @SerializedName("attachment_url") val attachmentUrl: String?,
    @SerializedName("created_at") val createdAt: String,
    @SerializedName("is_read") val isRead: Boolean
)

data class ApiError(
    @SerializedName("detail") val detail: String?,
    @SerializedName("message") val message: String?
)

data class ApiResponse<T>(
    val data: T? = null,
    val error: String? = null,
    val isLoading: Boolean = false
) {
    companion object {
        fun <T> loading() = ApiResponse<T>(isLoading = true)
        fun <T> success(data: T) = ApiResponse(data = data)
        fun <T> error(msg: String) = ApiResponse<T>(error = msg)
    }
}
