package com.logertogo.app.ui.profile

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import com.bumptech.glide.Glide
import com.logertogo.app.R
import com.logertogo.app.databinding.FragmentProfileBinding
import com.logertogo.app.ui.auth.AuthViewModel

class ProfileFragment : Fragment() {

    private var _binding: FragmentProfileBinding? = null
    private val binding get() = _binding!!

    private val viewModel: AuthViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentProfileBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        observeViewModel()
        setupClickListeners()

        viewModel.loadProfile()
    }

    private fun setupClickListeners() {
        binding.btnLogout.setOnClickListener {
            viewModel.logout()
            // Retour au login
            findNavController().navigate(R.id.loginFragment)
        }
        
        binding.btnEditProfile.setOnClickListener {
            // Future fonctionnalité : Modification du profil
        }
        
        binding.btnFavorites.setOnClickListener {
            findNavController().navigate(R.id.action_profile_to_favorites)
        }
    }

    private fun observeViewModel() {
        viewModel.profileState.observe(viewLifecycleOwner) { state ->
            if (state.data != null) {
                val user = state.data
                binding.tvName.text = "${user.firstName} ${user.lastName}"
                binding.tvRoleBadge.text = user.role.uppercase()
                
                Glide.with(this)
                    .load(user.avatar)
                    .placeholder(R.drawable.ic_logo_placeholder)
                    .circleCrop()
                    .into(binding.ivAvatar)
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
