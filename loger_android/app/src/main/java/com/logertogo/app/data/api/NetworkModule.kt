package com.logertogo.app.data.api

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.logertogo.app.BuildConfig
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

// ─── DataStore pour JWT Tokens ───────────────────────────
val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "loger_togo_prefs")

object TokenManager {
    private val ACCESS_TOKEN_KEY = stringPreferencesKey("access_token")
    private val REFRESH_TOKEN_KEY = stringPreferencesKey("refresh_token")

    suspend fun saveTokens(context: Context, access: String, refresh: String) {
        context.dataStore.edit { prefs ->
            prefs[ACCESS_TOKEN_KEY] = access
            prefs[REFRESH_TOKEN_KEY] = refresh
        }
    }

    fun getAccessTokenFlow(context: Context): Flow<String?> =
        context.dataStore.data.map { it[ACCESS_TOKEN_KEY] }

    fun getRefreshTokenFlow(context: Context): Flow<String?> =
        context.dataStore.data.map { it[REFRESH_TOKEN_KEY] }

    suspend fun getAccessToken(context: Context): String? =
        getAccessTokenFlow(context).first()

    suspend fun clearTokens(context: Context) {
        context.dataStore.edit { it.clear() }
    }

    fun bearerHeader(token: String) = "Bearer $token"
}

// ─── Client HTTP avec logging ────────────────────────────
object RetrofitClient {
    private var instance: LogerTogoApi? = null

    fun getInstance(): LogerTogoApi {
        if (instance == null) {
            val loggingInterceptor = HttpLoggingInterceptor().apply {
                level = if (BuildConfig.DEBUG)
                    HttpLoggingInterceptor.Level.BODY
                else
                    HttpLoggingInterceptor.Level.NONE
            }

            val client = OkHttpClient.Builder()
                .addInterceptor(loggingInterceptor)
                .connectTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(60, TimeUnit.SECONDS) // Plus long pour upload image R2
                .build()

            instance = Retrofit.Builder()
                .baseUrl(BuildConfig.BASE_URL)
                .client(client)
                .addConverterFactory(GsonConverterFactory.create())
                .build()
                .create(LogerTogoApi::class.java)
        }
        return instance!!
    }
}
