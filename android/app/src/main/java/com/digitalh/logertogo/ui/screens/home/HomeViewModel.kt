package com.digitalh.logertogo.ui.screens.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.digitalh.logertogo.data.remote.ApiService
import com.digitalh.logertogo.domain.model.Property
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class HomeViewModel @Inject constructor(
    private val apiService: ApiService
) : ViewModel() {

    private val _properties = MutableStateFlow<List<Property>>(emptyList())
    val properties: StateFlow<List<Property>> = _properties

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading

    private val _error = MutableStateFlow<String?>(null)
    val error: StateFlow<String?> = _error

    init {
        loadProperties()
    }

    fun loadProperties() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                val result = apiService.getProperties()
                _properties.value = result
                _error.value = null
            } catch (e: Exception) {
                _error.value = "Erreur de connexion : ${e.message}"
            } finally {
                _isLoading.value = false
            }
        }
    }
}
