package com.digitalh.logertogo.data.repository

import com.digitalh.logertogo.data.local.PropertyDao
import com.digitalh.logertogo.data.local.PropertyEntity
import com.digitalh.logertogo.data.remote.ApiService
import com.digitalh.logertogo.domain.model.Property
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject

class PropertyRepository @Inject constructor(
    private val apiService: ApiService,
    private val propertyDao: PropertyDao
) {
    // Flux de données locales
    val properties: Flow<List<Property>> = propertyDao.getAllProperties().map { entities ->
        entities.map { it.toDomain() }
    }

    // Synchronisation avec l'API
    suspend fun refreshProperties() {
        try {
            val remoteProperties = apiService.getProperties()
            propertyDao.clearAll()
            propertyDao.insertProperties(remoteProperties.map { it.toEntity() })
        } catch (e: Exception) {
            // En cas d'erreur réseau, on garde les données locales
        }
    }
}

// Mappers
fun PropertyEntity.toDomain() = Property(id, title, description, price, city, neighborhood, latitude, longitude, main_image, property_type, is_boosted)
fun Property.toEntity() = PropertyEntity(id, title, description, price, city, neighborhood, latitude, longitude, main_image, property_type, is_boosted)
