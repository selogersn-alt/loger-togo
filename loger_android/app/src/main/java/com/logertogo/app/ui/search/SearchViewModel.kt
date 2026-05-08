package com.logertogo.app.ui.search

import android.app.Application
import androidx.lifecycle.*
import com.logertogo.app.data.api.RetrofitClient
import com.logertogo.app.data.api.TokenManager
import com.logertogo.app.data.model.ApiResponse
import com.logertogo.app.data.model.Property
import kotlinx.coroutines.launch

class SearchViewModel(application: Application) : AndroidViewModel(application) {

    private val api = RetrofitClient.getInstance()
    private val context = application.applicationContext

    private val _searchResults = MutableLiveData<ApiResponse<List<Property>>>()
    val searchResults: LiveData<ApiResponse<List<Property>>> = _searchResults

    // Paramètres de recherche
    var query: String? = null
    var city: String? = null
    var propertyType: String? = null
    var listingCategory: String? = null
    var minPrice: Int? = null
    var maxPrice: Int? = null

    /**
     * Exécute la recherche avec tous les filtres actuels
     */
    fun performSearch() {
        viewModelScope.launch {
            _searchResults.value = ApiResponse.loading()
            try {
                val token = TokenManager.getAccessToken(context)?.let {
                    TokenManager.bearerHeader(it)
                } ?: ""

                val response = api.getProperties(
                    token = token,
                    query = query,
                    city = if (city == "Toutes les villes") null else city,
                    propertyType = if (propertyType == "Tous les types") null else propertyType,
                    listingCategory = if (listingCategory == "Toutes catégories") null else listingCategory,
                    minPrice = minPrice,
                    maxPrice = maxPrice
                )

                if (response.isSuccessful && response.body() != null) {
                    _searchResults.value = ApiResponse.success(response.body()!!.results)
                } else {
                    _searchResults.value = ApiResponse.error("Aucun résultat trouvé")
                }
            } catch (e: Exception) {
                _searchResults.value = ApiResponse.error(e.message ?: "Erreur réseau")
            }
        }
    }

    fun toggleFavorite(propertyId: String) {
        viewModelScope.launch {
            try {
                val token = TokenManager.getAccessToken(context) ?: return@launch
                api.toggleFavorite(TokenManager.bearerHeader(token), propertyId)
            } catch (e: Exception) { /* Silencieux */ }
        }
    }
}
