package com.logertogo.app.ui.home

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.ImageView
import android.widget.TextView
import androidx.core.widget.addTextChangedListener
import androidx.fragment.app.Fragment
import androidx.fragment.app.viewModels
import androidx.navigation.fragment.findNavController
import androidx.recyclerview.widget.GridLayoutManager
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import androidx.viewpager2.widget.ViewPager2
import com.bumptech.glide.Glide
import com.google.android.material.tabs.TabLayoutMediator
import com.logertogo.app.R
import com.logertogo.app.data.model.Property
import com.logertogo.app.databinding.FragmentHomeBinding
import kotlinx.coroutines.*

/**
 * ═══════════════════════════════════════════
 * Fragment principal : Page d'Accueil
 * - Carousel ViewPager2 des annonces boostées
 * - RecyclerView Grid des annonces récentes
 * - Barre de recherche avec debounce
 * ═══════════════════════════════════════════
 */
class HomeFragment : Fragment() {

    private var _binding: FragmentHomeBinding? = null
    private val binding get() = _binding!!

    private val viewModel: HomeViewModel by viewModels()

    private lateinit var boostedAdapter: BoostedCarouselAdapter
    private lateinit var propertiesAdapter: PropertyListAdapter

    // Auto-scroll du carousel
    private var autoScrollJob: Job? = null
    private var isUserScrolling = false

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        _binding = FragmentHomeBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        setupBoostedCarousel()
        setupPropertiesList()
        setupSearch()
        observeViewModel()

        // Charger les données
        viewModel.loadBoostedProperties()
        viewModel.loadRecentProperties()
    }

    private fun setupBoostedCarousel() {
        boostedAdapter = BoostedCarouselAdapter { property ->
            // Navigation vers le détail de l'annonce
            val action = HomeFragmentDirections.actionHomeToPropertyDetail(property.id)
            findNavController().navigate(action)
        }

        binding.viewPagerBoosted.apply {
            adapter = boostedAdapter
            offscreenPageLimit = 3
            // Effet de profondeur
            val transform = CompositePageTransformer()
            transform.addTransformer(MarginPageTransformer(40))
            transform.addTransformer { page, position ->
                val r = 1 - Math.abs(position)
                page.scaleY = 0.85f + r * 0.15f
                page.alpha = 0.7f + r * 0.3f
            }
            setPageTransformer(transform)
        }

        // Dots indicator
        TabLayoutMediator(binding.tabLayoutDots, binding.viewPagerBoosted) { _, _ -> }.attach()

        // Pause auto-scroll au toucher
        binding.viewPagerBoosted.registerOnPageChangeCallback(object : ViewPager2.OnPageChangeCallback() {
            override fun onPageScrollStateChanged(state: Int) {
                isUserScrolling = state != ViewPager2.SCROLL_STATE_IDLE
            }
        })

        binding.viewPagerBoosted.setOnTouchListener { _, _ ->
            stopAutoScroll()
            false
        }
    }

    private fun startAutoScroll() {
        stopAutoScroll()
        autoScrollJob = viewLifecycleOwner.lifecycleScope.launch {
            while (isActive) {
                delay(3500)
                if (!isUserScrolling && boostedAdapter.itemCount > 0) {
                    val nextItem = (binding.viewPagerBoosted.currentItem + 1) % boostedAdapter.itemCount
                    binding.viewPagerBoosted.setCurrentItem(nextItem, true)
                }
            }
        }
    }

    private fun stopAutoScroll() {
        autoScrollJob?.cancel()
        autoScrollJob = null
    }

    private fun setupPropertiesList() {
        propertiesAdapter = PropertyListAdapter { property ->
            val action = HomeFragmentDirections.actionHomeToPropertyDetail(property.id)
            findNavController().navigate(action)
        }

        binding.recyclerProperties.apply {
            layoutManager = GridLayoutManager(requireContext(), 2)
            adapter = propertiesAdapter
            setHasFixedSize(true)
        }
    }

    private fun setupSearch() {
        var searchJob: Job? = null
        binding.etSearch.addTextChangedListener { text ->
            searchJob?.cancel()
            searchJob = viewLifecycleOwner.lifecycleScope.launch {
                delay(400) // Debounce 400ms
                viewModel.searchProperties(text.toString())
            }
        }

        binding.btnSearch.setOnClickListener {
            viewModel.searchProperties(binding.etSearch.text.toString())
        }
    }

    private fun observeViewModel() {
        viewModel.boostedProperties.observe(viewLifecycleOwner) { state ->
            when {
                state.isLoading -> binding.shimmerBoosted.startShimmer()
                state.data != null -> {
                    binding.shimmerBoosted.stopShimmer()
                    binding.shimmerBoosted.visibility = View.GONE
                    binding.viewPagerBoosted.visibility = View.VISIBLE
                    binding.cardBoostedSection.visibility = if (state.data.isEmpty()) View.GONE else View.VISIBLE
                    boostedAdapter.submitList(state.data)
                    startAutoScroll()
                }
                state.error != null -> {
                    binding.shimmerBoosted.stopShimmer()
                    binding.cardBoostedSection.visibility = View.GONE
                }
            }
        }

        viewModel.recentProperties.observe(viewLifecycleOwner) { state ->
            when {
                state.isLoading -> {
                    binding.shimmerProperties.startShimmer()
                    binding.shimmerProperties.visibility = View.VISIBLE
                    binding.recyclerProperties.visibility = View.GONE
                }
                state.data != null -> {
                    binding.shimmerProperties.stopShimmer()
                    binding.shimmerProperties.visibility = View.GONE
                    binding.recyclerProperties.visibility = View.VISIBLE
                    propertiesAdapter.submitList(state.data)
                }
                state.error != null -> {
                    binding.shimmerProperties.stopShimmer()
                }
            }
        }
    }

    override fun onResume() {
        super.onResume()
        if (boostedAdapter.itemCount > 0) startAutoScroll()
    }

    override fun onPause() {
        super.onPause()
        stopAutoScroll()
    }

    override fun onDestroyView() {
        super.onDestroyView()
        stopAutoScroll()
        _binding = null
    }
}
