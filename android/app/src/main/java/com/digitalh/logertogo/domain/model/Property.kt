package com.digitalh.logertogo.domain.model

data class Property(
    val id: String,
    val title: String,
    val description: String,
    val price: Double,
    val city: String,
    val neighborhood: String,
    val latitude: Double?,
    val longitude: Double?,
    val main_image: String?,
    val property_type: String,
    val is_boosted: Boolean = false
)
