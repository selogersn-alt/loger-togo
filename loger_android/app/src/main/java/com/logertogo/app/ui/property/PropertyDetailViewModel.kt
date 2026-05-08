package com.logertogo.app.ui.property

import android.app.Application
import androidx.lifecycle.*
import com.logertogo.app.data.api.RetrofitClient
import com.logertogo.app.data.api.TokenManager
import com.logertogo.app.data.model.ApiResponse
import com.logertogo.app.data.model.Conversation
import com.logertogo.app.data.model.Property
import kotlinx.coroutines.launch

class PropertyDetailViewModel(application: Application) : AndroidViewModel(application) {

    private val api = RetrofitClient.getInstance()

    private val _propertyDetail = MutableLiveData<ApiResponse<Property>>()
    val propertyDetail: LiveData<ApiResponse<Property>> = _propertyDetail

    private val _contactResult = MutableLiveData<ApiResponse<Conversation>>()
    val contactResult: LiveData<ApiResponse<Conversation>> = _contactResult

    /**
     * Charge les détails d'une annonce
     */
    fun loadPropertyDetail(propertyId: String) {
        viewModelScope.launch {
            _propertyDetail.value = ApiResponse.loading()
            try {
                // On récupère le token si l'utilisateur est connecté (optionnel pour le détail)
                val token = TokenManager.getAccessToken(getApplication()) ?: ""
                val response = api.getPropertyDetail(TokenManager.bearerHeader(token), propertyId)
                
                if (response.isSuccessful && response.body() != null) {
                    _propertyDetail.value = ApiResponse.success(response.body()!!)
                } else {
                    _propertyDetail.value = ApiResponse.error("Impossible de charger les détails")
                }
            } catch (e: Exception) {
                _propertyDetail.value = ApiResponse.error(e.message ?: "Erreur réseau")
            }
        }
    }

    /**
     * Initie le contact avec le propriétaire
     */
    fun contactOwner(propertyId: String) {
        viewModelScope.launch {
            _contactResult.value = ApiResponse.loading()
            try {
                val token = TokenManager.getAccessToken(getApplication())
                if (token == null) {
                    _contactResult.value = ApiResponse.error("Veuillez vous connecter pour contacter le propriétaire")
                    return@launch
                }

                val response = api.startConversation(TokenManager.bearerHeader(token), propertyId)
                if (response.isSuccessful && response.body() != null) {
                    _contactResult.value = ApiResponse.success(response.body()!!)
                } else {
                    _contactResult.value = ApiResponse.error("Échec de l'ouverture de la discussion")
                }
            } catch (e: Exception) {
                _contactResult.value = ApiResponse.error(e.message ?: "Erreur lors du contact")
            }
        }
    }
}
