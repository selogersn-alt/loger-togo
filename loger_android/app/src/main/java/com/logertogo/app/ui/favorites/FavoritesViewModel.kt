package com.logertogo.app.ui.favorites

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

class FavoritesViewModel(application: Application) : AndroidViewModel(application) {

    private val api = RetrofitClient.getInstance()
    private val context = application.applicationContext

    private val _favorites = MutableLiveData<ApiResponse<List<Property>>>()
    val favorites: LiveData<ApiResponse<List<Property>>> = _favorites

    fun loadFavorites() {
        _favorites.value = ApiResponse.loading()
        viewModelScope.launch {
            try {
                val token = TokenManager.getAccessToken(context) ?: return@launch
                val response = api.getFavorites(TokenManager.bearerHeader(token))
                
                if (response.isSuccessful) {
                    _favorites.value = ApiResponse.success(response.body() ?: emptyList())
                } else {
                    _favorites.value = ApiResponse.error("Impossible de charger vos favoris")
                }
            } catch (e: Exception) {
                _favorites.value = ApiResponse.error(e.localizedMessage ?: "Erreur réseau")
            }
        }
    }

    fun toggleFavorite(propertyId: String) {
        viewModelScope.launch {
            try {
                val token = TokenManager.getAccessToken(context) ?: return@launch
                api.toggleFavorite(TokenManager.bearerHeader(token), propertyId)
                // Rafraîchir la liste après modification
                loadFavorites()
            } catch (e: Exception) { /* ... */ }
        }
    }
}
