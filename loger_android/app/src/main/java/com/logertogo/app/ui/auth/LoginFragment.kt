package com.logertogo.app.ui.auth

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import com.google.android.material.snackbar.Snackbar
import com.logertogo.app.R
import com.logertogo.app.databinding.FragmentLoginBinding

/**
 * ════════════════════════════════════════════
 * Fragment de Connexion JWT
 * - Email + Mot de passe
 * - Navigation vers l'accueil après succès
 * - Affichage des erreurs
 * ════════════════════════════════════════════
 */
class LoginFragment : Fragment() {

    private var _binding: FragmentLoginBinding? = null
    private val binding get() = _binding!!

    private val viewModel: AuthViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentLoginBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupClickListeners()
        observeViewModel()
    }

    private fun setupClickListeners() {
        binding.btnLogin.setOnClickListener {
            val email = binding.etEmail.text.toString().trim()
            val password = binding.etPassword.text.toString().trim()

            if (email.isEmpty() || password.isEmpty()) {
                Snackbar.make(binding.root, "Veuillez remplir tous les champs", Snackbar.LENGTH_SHORT).show()
                return@setOnClickListener
            }

            if (!android.util.Patterns.EMAIL_ADDRESS.matcher(email).matches()) {
                binding.tilEmail.error = "Email invalide"
                return@setOnClickListener
            }

            binding.tilEmail.error = null
            viewModel.login(email, password)
        }

        binding.tvGoToRegister.setOnClickListener {
            findNavController().navigate(R.id.action_loginFragment_to_registerFragment)
        }
    }

    private fun observeViewModel() {
        viewModel.loginState.observe(viewLifecycleOwner) { state ->
            binding.btnLogin.isEnabled = !state.isLoading
            binding.progressBar.visibility = if (state.isLoading) View.VISIBLE else View.GONE

            if (state.data != null) {
                // Connexion réussie → Navigation vers l'accueil
                findNavController().navigate(R.id.action_loginFragment_to_homeFragment)
            }

            state.error?.let { error ->
                Snackbar.make(binding.root, error, Snackbar.LENGTH_LONG)
                    .setBackgroundTint(requireContext().getColor(R.color.error))
                    .show()
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
