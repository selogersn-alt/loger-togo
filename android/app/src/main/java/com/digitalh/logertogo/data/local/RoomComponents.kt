package com.digitalh.logertogo.data.local

import androidx.room.*
import kotlinx.coroutines.flow.Flow

@Entity(tableName = "properties")
data class PropertyEntity(
    @PrimaryKey val id: String,
    val title: String,
    val description: String,
    val price: Double,
    val city: String,
    val neighborhood: String,
    val latitude: Double?,
    val longitude: Double?,
    val main_image: String?,
    val property_type: String,
    val is_boosted: Boolean
)

@Dao
interface PropertyDao {
    @Query("SELECT * FROM properties ORDER BY is_boosted DESC")
    fun getAllProperties(): Flow<List<PropertyEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertProperties(properties: List<PropertyEntity>)

    @Query("DELETE FROM properties")
    suspend fun clearAll()
}

@Database(entities = [PropertyEntity::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun propertyDao(): PropertyDao
}
