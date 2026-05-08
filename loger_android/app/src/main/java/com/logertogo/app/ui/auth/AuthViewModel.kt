package com.logertogo.app.ui.auth

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LiveData
import androidx.lifecycle.MutableLiveData
import androidx.lifecycle.viewModelScope
import com.logertogo.app.data.api.RetrofitClient
import com.logertogo.app.data.api.TokenManager
import com.logertogo.app.data.model.ApiResponse
import com.logertogo.app.data.model.AuthTokens
import com.logertogo.app.data.model.LoginRequest
import com.logertogo.app.data.model.User
import kotlinx.coroutines.launch

class AuthViewModel(application: Application) : AndroidViewModel(application) {

    private val api = RetrofitClient.getInstance()
    private val context = application.applicationContext

    private val _loginState = MutableLiveData<ApiResponse<AuthTokens>>()
    val loginState: LiveData<ApiResponse<AuthTokens>> = _loginState

    private val _profileState = MutableLiveData<ApiResponse<User>>()
    val profileState: LiveData<ApiResponse<User>> = _profileState

    private val _isLoggedIn = MutableLiveData<Boolean>()
    val isLoggedIn: LiveData<Boolean> = _isLoggedIn

    init {
        checkSession()
    }

    private fun checkSession() {
        viewModelScope.launch {
            val token = TokenManager.getAccessToken(context)
            _isLoggedIn.value = token != null
        }
    }

    private val _registerState = MutableLiveData<ApiResponse<User>>()
    val registerState: LiveData<ApiResponse<User>> = _registerState

    fun login(email: String, password: String) {
        _loginState.value = ApiResponse.loading()
        viewModelScope.launch {
            try {
                val response = api.login(LoginRequest(email, password))
                if (response.isSuccessful && response.body() != null) {
                    val tokens = response.body()!!
                    TokenManager.saveTokens(context, tokens.access, tokens.refresh)
                    _isLoggedIn.value = true
                    _loginState.value = ApiResponse.success(tokens)
                } else {
                    val errorMsg = when (response.code()) {
                        401 -> "Email ou mot de passe incorrect"
                        403 -> "Compte désactivé. Contactez le support."
                        429 -> "Trop de tentatives. Réessayez dans 1 minute."
                        else -> "Erreur de connexion (${response.code()})"
                    }
                    _loginState.value = ApiResponse.error(errorMsg)
                }
            } catch (e: Exception) {
                _loginState.value = ApiResponse.error(
                    "Impossible de se connecter. Vérifiez votre connexion internet."
                )
            }
        }
    }

    fun register(userData: Map<String, String>) {
        _registerState.value = ApiResponse.loading()
        viewModelScope.launch {
            try {
                val response = api.register(userData)
                if (response.isSuccessful && response.body() != null) {
                    _registerState.value = ApiResponse.success(response.body()!!)
                } else {
                    _registerState.value = ApiResponse.error("Échec de l'inscription. L'email est peut-être déjà utilisé.")
                }
            } catch (e: Exception) {
                _registerState.value = ApiResponse.error("Erreur réseau : ${e.localizedMessage}")
            }
        }
    }

    fun loadProfile() {
        viewModelScope.launch {
            try {
                val token = TokenManager.getAccessToken(context) ?: return@launch
                val response = api.getProfile(TokenManager.bearerHeader(token))
                if (response.isSuccessful && response.body() != null) {
                    _profileState.value = ApiResponse.success(response.body()!!)
                } else if (response.code() == 401) {
                    // Token expiré → tentative de refresh
                    refreshToken()
                }
            } catch (e: Exception) {
                _profileState.value = ApiResponse.error(e.localizedMessage ?: "Erreur réseau")
            }
        }
    }

    private fun refreshToken() {
        viewModelScope.launch {
            try {
                val refreshToken = TokenManager.getRefreshTokenFlow(context)
                // Si refresh token disponible, tenter de renouveler
                // Sinon déconnecter
                logout()
            } catch (e: Exception) {
                logout()
            }
        }
    }

    fun logout() {
        viewModelScope.launch {
            TokenManager.clearTokens(context)
            _isLoggedIn.value = false
        }
    }
}
