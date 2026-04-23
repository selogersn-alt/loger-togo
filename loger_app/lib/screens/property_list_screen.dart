import 'dart:async';
import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:intl/intl.dart';
import 'package:shimmer/shimmer.dart';
import 'package:flutter_staggered_animations/flutter_staggered_animations.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:animate_do/animate_do.dart';
import '../models/property_model.dart';
import '../services/api_service.dart';
import 'package:infinite_scroll_pagination/infinite_scroll_pagination.dart';
import 'search_results_screen.dart';
import 'package:timeago/timeago.dart' as timeago;

class PropertyListScreen extends StatefulWidget {
  final Function(Property) onPropertyTap;
  const PropertyListScreen({super.key, required this.onPropertyTap});

  @override
  State<PropertyListScreen> createState() => _PropertyListScreenState();
}

class _PropertyListScreenState extends State<PropertyListScreen> {
  final ApiService _apiService = ApiService();
  static const _pageSize = 10;
  final PagingController<int, Property> _pagingController = PagingController(firstPageKey: 1);
  final TextEditingController _searchController = TextEditingController();
  
  String _selectedCity = 'TOUT';
  String _selectedType = 'TOUT';
  String _selectedNeighborhood = 'TOUT';
  Timer? _refreshTimer;
  
  final Map<String, String> _cityMap = {
    'TOUT': 'TOUT',
    'LOME': 'LOME',
    'KARA': 'KARA',
    'SOKODE': 'SOKODE',
    'ATAKPAME': 'ATAKPAME',
    'KPALIME': 'KPALIME',
    'TSEVIE': 'TSEVIE',
    'ANEHO': 'ANEHO',
    'DAPAONG': 'DAPAONG'
  };

  final Map<String, String> _typeMap = {
    'TOUT': 'TOUT',
    'STUDIO': 'STUDIO',
    'APPARTEMENT': 'APPARTEMENT',
    'CHAMBRE': 'CHAMBRE',
    'IMMEUBLE': 'IMMEUBLE',
    'TERRAIN': 'TERRAIN',
    'PARCELLES': 'PARCELLES',
    'VILLA': 'VILLA',
    'MAISON': 'MAISON'
  };

  late final List<String> _cities = _cityMap.keys.toList();
  late final List<String> _types = _typeMap.keys.toList();
  final List<String> _neighborhoods = [
    'TOUT', 'Adidogomé', 'Agoè', 'Bè', 'Tokoin', 'Kégué', 'Baguida', 'Avédji', 'Nyékonakpoé', 'Kodjoviakopé'
  ];

  @override
  void initState() {
    super.initState();
    // Load cached properties first
    final cached = _apiService.getCachedProperties();
    if (cached.isNotEmpty) {
      _pagingController.itemList = cached;
    }
    
    _pagingController.addPageRequestListener((pageKey) {
      _fetchPage(pageKey);
    });
  }

  Future<void> _fetchPage(int pageKey) async {
    try {
      final newItems = await _apiService.fetchProperties(
        page: pageKey,
        city: _selectedCity == 'TOUT' ? null : _cityMap[_selectedCity],
        propertyType: _selectedType == 'TOUT' ? null : _typeMap[_selectedType],
        neighborhood: _selectedNeighborhood == 'TOUT' ? null : _selectedNeighborhood,
        search: _searchController.text.isNotEmpty ? _searchController.text : null,
      );
      final isLastPage = !newItems['next'];
      if (isLastPage) {
        _pagingController.appendLastPage(newItems['properties'] as List<Property>);
      } else {
        final nextPageKey = pageKey + 1;
        _pagingController.appendPage(newItems['properties'] as List<Property>, nextPageKey);
      }
    } catch (error) {
      _pagingController.error = error;
    }
  }

  @override
  void dispose() {
    _pagingController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  void _refresh() {
    _pagingController.refresh();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: CustomScrollView(
        physics: const BouncingScrollPhysics(),
        slivers: [
          // CUSTOM APP BAR LIKE IMAGE
          SliverAppBar(
            backgroundColor: Colors.white,
            elevation: 0,
            pinned: true,
            leading: Padding(
              padding: const EdgeInsets.all(12.0),
              child: Image.asset('assets/img/logo.png', fit: BoxFit.contain),
            ),
            title: RichText(
              text: const TextSpan(
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.black),
                children: [
                  TextSpan(text: 'Loger'),
                  TextSpan(text: 'Togo', style: TextStyle(color: Color(0xFF27C66E))),
                ],
              ),
            ),
            actions: const [],
          ),

          // HERO SECTION WITH SEARCH CARD
          SliverToBoxAdapter(
            child: SizedBox(
              height: 560, // Hauteur totale pour inclure le débordement de la carte
              child: Stack(
                clipBehavior: Clip.none,
                children: [
                  // Background Image Container
                  Container(
                    height: 480,
                  width: double.infinity,
                  margin: const EdgeInsets.symmetric(horizontal: 16),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(30),
                    color: const Color(0xFF004D40), // Couleur thème Loger
                    image: const DecorationImage(
                      image: AssetImage('assets/img/logo.png'),
                      fit: BoxFit.contain,
                      opacity: 0.4, // Plus visible comme demandé
                    ),
                  ),
                  child: Container(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        FadeInDown(
                          child: const Text(
                            "L'excellence immobilière au Togo.",
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.white, fontSize: 32, fontWeight: FontWeight.w900, height: 1.1),
                          ),
                        ),
                        const SizedBox(height: 16),
                        FadeInUp(
                          child: const Text(
                            "Découvrez des propriétés exclusives à Lomé, Kara et partout au Togo.",
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.white70, fontSize: 14, fontWeight: FontWeight.w500),
                          ),
                        ),
                        const SizedBox(height: 80), // Space for the card
                      ],
                    ),
                  ),
                ),
                
                // Floating Search Card
                Positioned(
                  bottom: -60,
                  left: 32,
                  right: 32,
                  child: FadeInUp(
                    delay: const Duration(milliseconds: 300),
                    child: Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(24),
                        boxShadow: [
                          BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 30, offset: const Offset(0, 15)),
                        ],
                      ),
                      child: Column(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          _buildSearchInput(),
                          const Divider(height: 1),
                          _buildCitySelector(),
                          const Divider(height: 1),
                          _buildNeighborhoodSelector(),
                          const Divider(height: 1),
                          _buildTypeSelector(),
                          const SizedBox(height: 20),
                          ElevatedButton.icon(
                              onPressed: () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) => SearchResultsScreen(
                                      city: _selectedCity == 'TOUT' ? null : _cityMap[_selectedCity],
                                      type: _selectedType == 'TOUT' ? null : _typeMap[_selectedType],
                                      neighborhood: _selectedNeighborhood == 'TOUT' ? null : _selectedNeighborhood,
                                      search: _searchController.text.isNotEmpty ? _searchController.text : null,
                                    ),
                                  ),
                                );
                              },
                              icon: const Icon(Icons.search_rounded, color: Colors.white),
                              label: const Text('Rechercher', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF27C66E),
                                padding: const EdgeInsets.symmetric(vertical: 20), // Plus haut
                                minimumSize: const Size(double.infinity, 60), // Plus large
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                                elevation: 4,
                              ),
                            ),
                        ],
                      ),
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),

          const SliverToBoxAdapter(child: SizedBox(height: 100)),

          // FEATURED SECTION HEADER
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: const [
                      Text('À la Une', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900)),
                      Text('Sélection de prestige', style: TextStyle(color: Colors.blueGrey, fontWeight: FontWeight.w500)),
                    ],
                  ),
                  TextButton(
                    onPressed: () {},
                    child: Row(
                      children: const [
                        Text('Voir tout', style: TextStyle(color: Color(0xFF27C66E), fontWeight: FontWeight.bold)),
                        Icon(Icons.chevron_right_rounded, color: Color(0xFF27C66E)),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),

          PagedSliverList<int, Property>(
            pagingController: _pagingController,
            builderDelegate: PagedChildBuilderDelegate<Property>(
              itemBuilder: (context, item, index) => AnimationConfiguration.staggeredList(
                position: index,
                duration: const Duration(milliseconds: 600),
                child: SlideAnimation(
                  verticalOffset: 50.0,
                  child: FadeInAnimation(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24),
                      child: _buildPropertyCard(item),
                    ),
                  ),
                ),
              ),
              firstPageProgressIndicatorBuilder: (_) => _buildSkeletonLoader(),
              newPageProgressIndicatorBuilder: (_) => const Center(child: Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator())),
              noItemsFoundIndicatorBuilder: (_) => Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text('Aucun bien trouvé'),
                    TextButton(onPressed: () => _refresh(), child: const Text('Recharger')),
                  ],
                ),
              ),
              firstPageErrorIndicatorBuilder: (context) => Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Text('Erreur lors du chargement des annonces'),
                    const SizedBox(height: 10),
                    ElevatedButton(onPressed: () => _refresh(), child: const Text('Réessayer')),
                  ],
                ),
              ),
            ),
          ),
          const SliverToBoxAdapter(child: SizedBox(height: 100)),
        ],
      ),
    );
  }

  Widget _buildSearchInput() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          const Icon(Icons.search_rounded, color: Color(0xFF27C66E), size: 22),
          const SizedBox(width: 16),
          Expanded(
            child: TextField(
              controller: _searchController,
              decoration: const InputDecoration(
                hintText: 'Mots-clés (Villa, piscine...)',
                hintStyle: TextStyle(color: Colors.blueGrey, fontSize: 15, fontWeight: FontWeight.w500),
                border: InputBorder.none,
              ),
              onSubmitted: (_) => _refresh(),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCitySelector() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          const Icon(Icons.location_on_outlined, color: Color(0xFF27C66E), size: 22),
          const SizedBox(width: 16),
          Expanded(
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: _selectedCity,
                isExpanded: true,
                dropdownColor: Colors.white,
                borderRadius: BorderRadius.circular(16),
                hint: const Text('Où cherchez-vous ?', style: TextStyle(color: Colors.blueGrey)),
                icon: const Icon(Icons.keyboard_arrow_down_rounded, color: Colors.blueGrey),
                items: _cities.map((String city) {
                  return DropdownMenuItem<String>(
                    value: city,
                    child: Text(
                      city, 
                      style: const TextStyle(
                        color: Colors.black, 
                        fontWeight: FontWeight.w600,
                        fontSize: 15
                      )
                    ),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  if (newValue != null) {
                    setState(() {
                      _selectedCity = newValue;
                    });
                    _refresh();
                  }
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTypeSelector() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          const Icon(Icons.home_outlined, color: Color(0xFF27C66E), size: 22),
          const SizedBox(width: 16),
          Expanded(
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: _selectedType,
                isExpanded: true,
                dropdownColor: Colors.white,
                borderRadius: BorderRadius.circular(16),
                hint: const Text('Type de bien', style: TextStyle(color: Colors.blueGrey)),
                icon: const Icon(Icons.keyboard_arrow_down_rounded, color: Colors.blueGrey),
                items: _types.map((String type) {
                  return DropdownMenuItem<String>(
                    value: type,
                    child: Text(
                      type, 
                      style: const TextStyle(
                        color: Colors.black, 
                        fontWeight: FontWeight.w600,
                        fontSize: 15
                      )
                    ),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  if (newValue != null) {
                    setState(() {
                      _selectedType = newValue;
                    });
                    _refresh();
                  }
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildNeighborhoodSelector() {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        children: [
          const Icon(Icons.location_on_outlined, color: Color(0xFF27C66E), size: 22),
          const SizedBox(width: 16),
          Expanded(
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: _selectedNeighborhood,
                isExpanded: true,
                dropdownColor: Colors.white,
                borderRadius: BorderRadius.circular(16),
                hint: const Text('Quartier', style: TextStyle(color: Colors.blueGrey)),
                icon: const Icon(Icons.keyboard_arrow_down_rounded, color: Colors.blueGrey),
                items: _neighborhoods.map((String neighborhood) {
                  return DropdownMenuItem<String>(
                    value: neighborhood,
                    child: Text(
                      neighborhood, 
                      style: const TextStyle(
                        color: Colors.black, 
                        fontWeight: FontWeight.w600,
                        fontSize: 15
                      )
                    ),
                  );
                }).toList(),
                onChanged: (String? newValue) {
                  if (newValue != null) {
                    setState(() {
                      _selectedNeighborhood = newValue;
                    });
                  }
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPropertyCard(Property p) {
    return GestureDetector(
      onTap: () => widget.onPropertyTap(p),
      child: Container(
        margin: const EdgeInsets.only(bottom: 24),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 20)],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Stack(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(24),
                  child: CachedNetworkImage(
                    imageUrl: p.images.isNotEmpty ? p.images.first.imageUrl : '',
                    height: 220,
                    width: double.infinity,
                    fit: BoxFit.cover,
                  ),
                ),
                Positioned(
                  top: 16,
                  left: 16,
                  child: Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(8)),
                        child: Text(
                          p.listingCategoryDisplay.toUpperCase(),
                          style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w900, color: Colors.black),
                        ),
                      ),
                      const SizedBox(width: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(color: const Color(0xFF27C66E), borderRadius: BorderRadius.circular(8)),
                        child: Text(
                          timeago.format(p.createdAt, locale: 'fr'),
                          style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w900, color: Colors.white),
                        ),
                      ),
                    ],
                  ),
                ),
                Positioned(
                  top: 12,
                  right: 12,
                  child: GestureDetector(
                    onTap: () async {
                      final success = await _apiService.toggleFavorite(p.id.toString());
                      if (success && mounted) {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Favoris mis à jour'), duration: Duration(seconds: 1)),
                        );
                      }
                    },
                    child: const CircleAvatar(
                      backgroundColor: Colors.white,
                      radius: 18,
                      child: Icon(Icons.favorite_border_rounded, size: 18, color: Colors.black),
                    ),
                  ),
                ),
              ],
            ),
            Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(p.title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900)),
                  const SizedBox(height: 4),
                  Text('${p.neighborhood}, ${p.city}', style: const TextStyle(color: Colors.blueGrey, fontSize: 13)),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Text(
                        '${NumberFormat.decimalPattern('fr').format(p.price)} F',
                        style: const TextStyle(color: Color(0xFF27C66E), fontWeight: FontWeight.w900, fontSize: 18),
                      ),
                      const Spacer(),
                      const Icon(Icons.bed_rounded, size: 16, color: Colors.blueGrey),
                      const SizedBox(width: 4),
                      Text('${p.bedrooms}', style: const TextStyle(color: Colors.blueGrey, fontSize: 12)),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSkeletonLoader() {
    return Container(height: 200, color: Colors.grey[100]);
  }
}
