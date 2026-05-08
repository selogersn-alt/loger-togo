package com.logertogo.app.ui.property

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.Toast
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.navigation.fragment.navArgs
import com.bumptech.glide.Glide
import com.logertogo.app.R
import com.logertogo.app.data.model.Property
import com.logertogo.app.databinding.FragmentPropertyDetailBinding

class PropertyDetailFragment : Fragment() {

    private var _binding: FragmentPropertyDetailBinding? = null
    private val binding get() = _binding!!

    private val viewModel: PropertyDetailViewModel by viewModels()
    private val args: PropertyDetailFragmentArgs by navArgs()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentPropertyDetailBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupToolbar()
        observeViewModel()

        // On charge les données via l'ID passé en argument par la navigation
        viewModel.loadPropertyDetail(args.propertyId)

        binding.btnContact.setOnClickListener {
            viewModel.contactOwner(args.propertyId)
        }
    }

    private fun setupToolbar() {
        binding.toolbar.setNavigationOnClickListener {
            findNavController().navigateUp()
        }
    }

    private fun observeViewModel() {
        viewModel.propertyDetail.observe(viewLifecycleOwner) { state ->
            when {
                state.data != null -> populateUi(state.data)
                state.error != null -> Toast.makeText(context, state.error, Toast.LENGTH_SHORT).show()
            }
        }

        viewModel.contactResult.observe(viewLifecycleOwner) { state ->
            when {
                state.data != null -> {
                    // Si le contact est réussi, on pourrait naviguer vers la messagerie
                    Toast.makeText(context, "Discussion ouverte !", Toast.LENGTH_SHORT).show()
                    // findNavController().navigate(...) 
                }
                state.error != null -> {
                    Toast.makeText(context, state.error, Toast.LENGTH_SHORT).show()
                }
            }
        }
    }

    private fun populateUi(property: Property) {
        binding.apply {
            tvTitle.text = property.title
            tvPrice.text = getString(R.string.price_format, String.format("%,.0f", property.price))
            tvLocation.text = "${property.neighborhood}, ${property.city}"
            tvDescription.text = property.description
            
            chipType.text = property.propertyType
            chipCategory.text = property.listingCategory

            // Statistiques
            tvRooms.text = getString(R.string.rooms_format, property.rooms ?: 0)
            tvBathrooms.text = "${property.bathrooms ?: 0} sdb."
            tvArea.text = getString(R.string.area_format, property.area ?: 0.0)

            // Masquer les stats si null/0
            layoutRooms.visibility = if (property.rooms != null) View.VISIBLE else View.GONE
            layoutArea.visibility = if (property.area != null) View.VISIBLE else View.GONE

            // Équipements (visibilité)
            tvWifi.visibility = if (property.wifi) View.VISIBLE else View.GONE
            tvAc.visibility = if (property.airConditioning) View.VISIBLE else View.GONE
            tvPool.visibility = if (property.swimmingPool) View.VISIBLE else View.GONE

            // Carousel d'images
            val imageAdapter = PropertyImageAdapter(property.images)
            vpImages.adapter = imageAdapter
            
            // Liaison des points (dots) indicateurs
            com.google.android.material.tabs.TabLayoutMediator(tabDots, vpImages) { _, _ -> }.attach()
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
