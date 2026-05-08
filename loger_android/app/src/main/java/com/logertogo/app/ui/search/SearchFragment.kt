package com.logertogo.app.ui.search

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ArrayAdapter
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.GridLayoutManager
import com.logertogo.app.R
import com.logertogo.app.databinding.FragmentSearchBinding
import com.logertogo.app.ui.home.PropertyListAdapter

class SearchFragment : Fragment() {

    private var _binding: FragmentSearchBinding? = null
    private val binding get() = _binding!!

    private val viewModel: SearchViewModel by viewModels()
    private lateinit var resultsAdapter: PropertyListAdapter

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentSearchBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupSpinners()
        setupRecyclerView()
        observeViewModel()

        binding.btnApply.setOnClickListener {
            updateFiltersAndSearch()
        }

        binding.btnOpenMap.setOnClickListener {
            findNavController().navigate(R.id.action_search_to_map)
        }

        // Lancer une recherche initiale (vide)
        viewModel.performSearch()
    }

    private fun setupSpinners() {
        // Villes du Togo
        val cities = arrayOf("Toutes les villes", "Lomé", "Aného", "Kpalimé", "Atakpamé", "Sokodé", "Kara", "Dapaong")
        binding.spinnerCity.adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, cities)

        // Types de biens
        val types = arrayOf("Tous les types", "Villa", "Appartement", "Terrain", "Bureaux", "Boutique", "Chambre")
        binding.spinnerType.adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, types)

        // Catégories
        val categories = arrayOf("Toutes catégories", "Location", "Vente", "Nuitée")
        binding.spinnerCategory.adapter = ArrayAdapter(requireContext(), android.R.layout.simple_spinner_dropdown_item, categories)
    }

    private fun setupRecyclerView() {
        resultsAdapter = PropertyListAdapter(
            onClick = { property ->
                val action = SearchFragmentDirections.actionSearchToPropertyDetail(property.id)
                findNavController().navigate(action)
            },
            onFavoriteClick = { property ->
                // On peut utiliser un ViewModel partagé ou ajouter la méthode au SearchViewModel
                viewModel.toggleFavorite(property.id)
            }
        )
        binding.recyclerResults.apply {
            layoutManager = GridLayoutManager(context, 2)
            adapter = resultsAdapter
        }
    }

    private fun updateFiltersAndSearch() {
        viewModel.query = binding.etQuery.text.toString().takeIf { it.isNotEmpty() }
        viewModel.city = binding.spinnerCity.selectedItem.toString()
        viewModel.propertyType = binding.spinnerType.selectedItem.toString()
        viewModel.listingCategory = binding.spinnerCategory.selectedItem.toString()
        viewModel.minPrice = binding.etMin_price.text.toString().toIntOrNull()
        viewModel.maxPrice = binding.etMax_price.text.toString().toIntOrNull()

        viewModel.performSearch()
    }

    private fun observeViewModel() {
        viewModel.searchResults.observe(viewLifecycleOwner) { state ->
            when {
                state.data != null -> resultsAdapter.submitList(state.data)
                state.error != null -> Toast.makeText(context, state.error, Toast.LENGTH_SHORT).show()
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
