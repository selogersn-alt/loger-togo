package com.digitalh.logertogo.ui.screens.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.digitalh.logertogo.data.remote.ApiService
import com.digitalh.logertogo.domain.model.LoginRequest
import com.digitalh.logertogo.domain.model.RegisterRequest
import com.digitalh.logertogo.domain.model.User
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val apiService: ApiService
) : ViewModel() {

    private val _currentUser = MutableStateFlow<User?>(null)
    val currentUser: StateFlow<User?> = _currentUser

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error

    fun login(phone: String, pass: String, onSuccess: () -> Unit) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val response = apiService.login(LoginRequest(phone, pass))
                // Sauvegarder le token (Access/Refresh) ici
                onSuccess()
            } catch (e: Exception) {
                _error.value = "Identifiants incorrects"
            } finally {
                _isLoading.value = false
            }
        }
    }

    fun register(firstName: String, lastName: String, phone: String, pass: String, onSuccess: () -> Unit) {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                apiService.register(RegisterRequest(phone, firstName, lastName, pass))
                onSuccess()
            } catch (e: Exception) {
                _error.value = "Erreur lors de l'inscription"
            } finally {
                _isLoading.value = false
            }
        }
    }
}
