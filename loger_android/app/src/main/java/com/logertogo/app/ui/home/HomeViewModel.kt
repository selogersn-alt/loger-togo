package com.logertogo.app.ui.home

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.logertogo.app.data.api.RetrofitClient
import com.logertogo.app.data.api.TokenManager
import com.logertogo.app.data.model.ApiResponse
import com.logertogo.app.data.model.Property
import kotlinx.coroutines.launch

/**
 * ViewModel du HomeFragment - Architecture MVVM
 * Gère les appels API et le cycle de vie des données
 */
class HomeViewModel(application: Application) : AndroidViewModel(application) {

    private val api = RetrofitClient.getInstance()
    private val context = application.applicationContext

    // ─── Annonces boostées (carousel) ─────────────────────
    private val _boostedProperties = MutableLiveData<ApiResponse<List<Property>>>()
    val boostedProperties: LiveData<ApiResponse<List<Property>>> = _boostedProperties

    // ─── Annonces récentes (grille) ────────────────────────
    private val _recentProperties = MutableLiveData<ApiResponse<List<Property>>>()
    val recentProperties: LiveData<ApiResponse<List<Property>>> = _recentProperties

    fun loadBoostedProperties() {
        _boostedProperties.value = ApiResponse.loading()
        viewModelScope.launch {
            try {
                val response = api.getBoostedProperties()
                if (response.isSuccessful && response.body() != null) {
                    _boostedProperties.value = ApiResponse.success(response.body()!!.results)
                } else {
                    _boostedProperties.value = ApiResponse.error("Erreur chargement annonces boostées")
                }
            } catch (e: Exception) {
                _boostedProperties.value = ApiResponse.error(e.localizedMessage ?: "Erreur réseau")
            }
        }
    }

    fun loadRecentProperties(city: String? = null, propertyType: String? = null) {
        _recentProperties.value = ApiResponse.loading()
        viewModelScope.launch {
            try {
                val token = TokenManager.getAccessToken(context)?.let {
                    TokenManager.bearerHeader(it)
                } ?: ""

                val response = api.getProperties(
                    token = token,
                    city = city,
                    propertyType = propertyType
                )

                if (response.isSuccessful && response.body() != null) {
                    _recentProperties.value = ApiResponse.success(response.body()!!.results)
                } else {
                    _recentProperties.value = ApiResponse.error("Erreur chargement annonces")
                }
            } catch (e: Exception) {
                _recentProperties.value = ApiResponse.error(e.localizedMessage ?: "Erreur réseau")
            }
        }
    }

    fun searchProperties(query: String) {
        if (query.isBlank()) {
            loadRecentProperties()
            return
        }
        _recentProperties.value = ApiResponse.loading()
        viewModelScope.launch {
            try {
                val token = TokenManager.getAccessToken(context)?.let {
                    TokenManager.bearerHeader(it)
                } ?: ""

                val response = api.getProperties(token = token, query = query)
                if (response.isSuccessful && response.body() != null) {
                    _recentProperties.value = ApiResponse.success(response.body()!!.results)
                } else {
                    _recentProperties.value = ApiResponse.error("Aucun résultat pour \"$query\"")
                }
            } catch (e: Exception) {
                _recentProperties.value = ApiResponse.error(e.localizedMessage ?: "Erreur réseau")
            }
        }
    }
}
