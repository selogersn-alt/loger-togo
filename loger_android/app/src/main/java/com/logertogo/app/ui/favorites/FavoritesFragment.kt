package com.logertogo.app.ui.favorites

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.GridLayoutManager
import com.logertogo.app.databinding.FragmentFavoritesBinding
import com.logertogo.app.ui.home.PropertyListAdapter

class FavoritesFragment : Fragment() {

    private var _binding: FragmentFavoritesBinding? = null
    private val binding get() = _binding!!

    private val viewModel: FavoritesViewModel by viewModels()
    private lateinit var adapter: PropertyListAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentFavoritesBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupRecyclerView()
        observeViewModel()

        binding.swipeRefresh.setOnRefreshListener {
            viewModel.loadFavorites()
        }

        viewModel.loadFavorites()
    }

    private fun setupRecyclerView() {
        adapter = PropertyListAdapter(
            onClick = { property ->
                // Aller au détail (on réutilise l'action globale ou on définit une spécifique)
                val action = FavoritesFragmentDirections.actionFavoritesToPropertyDetail(property.id)
                findNavController().navigate(action)
            },
            onFavoriteClick = { property ->
                viewModel.toggleFavorite(property.id)
            }
        )
        binding.recyclerFavorites.apply {
            layoutManager = GridLayoutManager(context, 2)
            adapter = this@FavoritesFragment.adapter
        }
    }

    private fun observeViewModel() {
        viewModel.favorites.observe(viewLifecycleOwner) { state ->
            binding.swipeRefresh.isRefreshing = state.isLoading
            
            if (state.data != null) {
                adapter.submitList(state.data)
                binding.layoutEmpty.visibility = if (state.data.isEmpty()) View.VISIBLE else View.GONE
                binding.recyclerFavorites.visibility = if (state.data.isEmpty()) View.GONE else View.VISIBLE
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
