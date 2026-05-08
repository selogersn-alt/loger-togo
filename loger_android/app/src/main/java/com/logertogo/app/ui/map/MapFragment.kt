package com.logertogo.app.ui.map

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import com.bumptech.glide.Glide
import com.logertogo.app.R
import com.logertogo.app.data.model.Property
import com.logertogo.app.databinding.FragmentMapBinding
import com.logertogo.app.ui.home.HomeViewModel
import org.osmdroid.config.Configuration
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.CustomZoomButtonsDisplay
import org.osmdroid.views.overlay.Marker

class MapFragment : Fragment() {

    private var _binding: FragmentMapBinding? = null
    private val binding get() = _binding!!

    private val viewModel: HomeViewModel by viewModels()

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        // Configuration indispensable pour Osmdroid
        Configuration.getInstance().userAgentValue = "LogerTogo_Android"
        
        _binding = FragmentMapBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupMap()
        setupUI()
        observeViewModel()
        
        viewModel.loadRecentProperties()
    }

    private fun setupMap() {
        binding.mapView.setTileSource(TileSourceFactory.MAPNIK)
        binding.mapView.setMultiTouchControls(true)
        binding.mapView.zoomController.setVisibility(org.osmdroid.views.CustomZoomButtonsController.Visibility.NEVER)
        
        val mapController = binding.mapView.controller
        mapController.setZoom(12.0)
        // Lomé, Togo
        val startPoint = GeoPoint(6.1375, 1.2125)
        mapController.setCenter(startPoint)
    }

    private fun setupUI() {
        binding.btnClosePreview.setOnClickListener {
            binding.cardPropertyPreview.visibility = View.GONE
        }
        
        binding.fabMyLocation.setOnClickListener {
            // Ici, vous pourriez ajouter la logique pour zoomer sur la position GPS réelle
            val lome = GeoPoint(6.1375, 1.2125)
            binding.mapView.controller.animateTo(lome)
        }
    }

    private fun observeViewModel() {
        viewModel.recentProperties.observe(viewLifecycleOwner) { state ->
            if (state.data != null) {
                addMarkers(state.data)
            }
        }
    }

    private fun addMarkers(properties: List<Property>) {
        binding.mapView.overlays.clear()
        
        properties.forEach { property ->
            if (property.latitude != null && property.longitude != null) {
                val marker = Marker(binding.mapView)
                marker.position = GeoPoint(property.latitude, property.longitude)
                marker.title = property.title
                marker.setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_BOTTOM)
                
                marker.setOnMarkerClickListener { m, _ ->
                    showPropertyPreview(property)
                    true
                }
                
                binding.mapView.overlays.add(marker)
            }
        }
        binding.mapView.invalidate() // Rafraîchir la carte
    }

    private fun showPropertyPreview(property: Property) {
        binding.cardPropertyPreview.visibility = View.VISIBLE
        binding.tvPropertyTitle.text = property.title
        binding.tvPropertyPrice.text = getString(R.string.price_format, String.format("%,.0f", property.price))
        binding.tvPropertyType.text = property.propertyType

        Glide.with(this)
            .load(property.mainImage)
            .placeholder(R.color.grey_light)
            .into(binding.ivPropertyThumb)

        binding.cardPropertyPreview.setOnClickListener {
            val action = MapFragmentDirections.actionMapToPropertyDetail(property.id)
            findNavController().navigate(action)
        }
    }

    override fun onResume() {
        super.onResume()
        binding.mapView.onResume()
    }

    override fun onPause() {
        super.onPause()
        binding.mapView.onPause()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null
    }
}
