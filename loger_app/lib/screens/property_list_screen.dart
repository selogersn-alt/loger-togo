import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:shimmer/shimmer.dart';
import 'package:flutter_staggered_animations/flutter_staggered_animations.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/property_model.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class PropertyListScreen extends StatefulWidget {
  final Function(Property) onPropertyTap;
  const PropertyListScreen({super.key, required this.onPropertyTap});

  @override
  State<PropertyListScreen> createState() => _PropertyListScreenState();
}

class _PropertyListScreenState extends State<PropertyListScreen> {
  final ApiService _apiService = ApiService();
  late Future<List<Property>> _propertiesFuture;
  final TextEditingController _searchController = TextEditingController();
  String _selectedCity = 'ALL';
  String _selectedCategory = 'ALL';
  
  final List<String> _cities = ['ALL', 'DAKAR', 'THIES', 'MBOUR', 'SAINT-LOUIS'];
  
  final List<Map<String, dynamic>> _categories = [
    {'id': 'ALL', 'name': 'Tous', 'icon': Icons.grid_view_rounded},
    {'id': 'APARTMENT', 'name': 'Apparts', 'icon': Icons.apartment_rounded},
    {'id': 'VILLA', 'name': 'Villas', 'icon': Icons.bungalow_rounded},
    {'id': 'STUDIO', 'name': 'Studios', 'icon': Icons.meeting_room_rounded},
    {'id': 'TERRAIN', 'name': 'Terrains', 'icon': Icons.landscape_rounded},
  ];

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  void _refresh() {
    setState(() {
      _propertiesFuture = _apiService.fetchProperties(
        city: _selectedCity == 'ALL' ? null : _selectedCity,
        search: _searchController.text.isNotEmpty ? _searchController.text : null,
      );
    });
  }

  @override
  Widget build(BuildContext context) {
    final user = AuthService().currentUser;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: CustomScrollView(
        physics: const BouncingScrollPhysics(),
        slivers: [
          // Professional & Minimalist Header
          SliverAppBar(
            expandedHeight: 120,
            floating: true,
            pinned: true,
            backgroundColor: Colors.white,
            elevation: 0,
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                color: Colors.white,
                padding: const EdgeInsets.fromLTRB(20, 50, 20, 0),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Image.asset('assets/img/logo.png', height: 45),
                    Row(
                      children: [
                        if (user != null)
                          Padding(
                            padding: const EdgeInsets.only(right: 15),
                            child: Text(
                              'Salut, ${user.firstName}',
                              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: Color(0xFF198754)),
                            ),
                          ),
                        CircleAvatar(
                          backgroundColor: const Color(0xFF198754).withValues(alpha: 0.1),
                          child: Icon(
                            user != null ? Icons.notifications_active_rounded : Icons.notifications_none_rounded, 
                            color: const Color(0xFF198754), 
                            size: 20
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ),

          // Search & Filters Header
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.fromLTRB(20, 10, 20, 0),
              child: Column(
                children: [
                  // Unified Search & City Filter
                  Row(
                    children: [
                      Expanded(
                        flex: 3,
                        child: Material(
                          elevation: 4,
                          shadowColor: Colors.black12,
                          borderRadius: BorderRadius.circular(15),
                          child: TextField(
                            controller: _searchController,
                            onSubmitted: (_) => _refresh(),
                            decoration: InputDecoration(
                              hintText: 'Quartier, réf...',
                              prefixIcon: const Icon(Icons.search, color: Color(0xFF198754)),
                              filled: true,
                              fillColor: Colors.white,
                              border: OutlineInputBorder(
                                borderRadius: BorderRadius.circular(15),
                                borderSide: BorderSide.none,
                              ),
                              contentPadding: const EdgeInsets.symmetric(vertical: 15),
                            ),
                          ),
                        ),
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        flex: 2,
                        child: Container(
                          height: 55,
                          padding: const EdgeInsets.symmetric(horizontal: 10),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(15),
                            boxShadow: const [BoxShadow(color: Colors.black12, blurRadius: 4, offset: Offset(0, 2))],
                          ),
                          child: DropdownButtonHideUnderline(
                            child: DropdownButton<String>(
                              value: _selectedCity,
                              icon: const Icon(Icons.location_on_rounded, color: Color(0xFF198754), size: 18),
                              isExpanded: true,
                              style: const TextStyle(color: Colors.black87, fontWeight: FontWeight.bold, fontSize: 13),
                              items: _cities.map((String city) {
                                return DropdownMenuItem<String>(
                                  value: city,
                                  child: Text(city == 'ALL' ? 'Tout Sénégal' : city),
                                );
                              }).toList(),
                              onChanged: (String? newValue) {
                                setState(() {
                                  _selectedCity = newValue!;
                                });
                                _refresh();
                              },
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 25),
                  
                  // Native Categories
                  SizedBox(
                    height: 100,
                    child: ListView.builder(
                      scrollDirection: Axis.horizontal,
                      itemCount: _categories.length,
                      physics: const BouncingScrollPhysics(),
                      itemBuilder: (context, index) {
                        final cat = _categories[index];
                        bool isSelected = _selectedCategory == cat['id'];
                        return Padding(
                          padding: const EdgeInsets.only(right: 15),
                          child: GestureDetector(
                            onTap: () {
                              setState(() => _selectedCategory = cat['id']);
                              _refresh();
                            },
                            child: Column(
                              children: [
                                AnimatedContainer(
                                  duration: const Duration(milliseconds: 300),
                                  padding: const EdgeInsets.all(15),
                                  decoration: BoxDecoration(
                                    color: isSelected ? const Color(0xFF198754) : Colors.white,
                                    borderRadius: BorderRadius.circular(20),
                                    boxShadow: [
                                      if (isSelected)
                                        BoxShadow(
                                          color: const Color(0xFF198754).withValues(alpha: 0.3),
                                          blurRadius: 10,
                                          offset: const Offset(0, 5),
                                        )
                                      else
                                        const BoxShadow(
                                          color: Colors.black12,
                                          blurRadius: 5,
                                          offset: Offset(0, 2),
                                        ),
                                    ],
                                  ),
                                  child: Icon(
                                    cat['icon'],
                                    color: isSelected ? Colors.white : const Color(0xFF198754),
                                    size: 28,
                                  ),
                                ),
                                const SizedBox(height: 10),
                                Text(
                                  cat['name'],
                                  style: TextStyle(
                                    fontSize: 13,
                                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                                    color: isSelected ? const Color(0xFF198754) : Colors.black87,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
                  ),
                ],
              ),
            ),
          ),

          // Main Content
          FutureBuilder<List<Property>>(
            future: _propertiesFuture,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return SliverToBoxAdapter(child: _buildSkeletonLoader());
              }

              if (snapshot.hasError) {
                return SliverFillRemaining(child: _buildErrorWidget(snapshot.error.toString()));
              }

              final allProperties = snapshot.data ?? [];
              if (allProperties.isEmpty) {
                return const SliverFillRemaining(child: Center(child: Text('Aucune annonce trouvée.')));
              }

              // Filtered by category (Local filter for UI speed)
              final properties = _selectedCategory == 'ALL' 
                ? allProperties 
                : allProperties.where((p) => p.propertyType == _selectedCategory).toList();

              final featured = properties.where((p) => p.isBoosted).toList();
              final recent = properties.where((p) => !p.isBoosted).toList();

              return SliverPadding(
                padding: const EdgeInsets.only(bottom: 100),
                sliver: SliverList(
                  delegate: SliverChildListDelegate([
                    if (featured.isNotEmpty) ...[
                      const Padding(
                        padding: EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                        child: Text(
                          'À la Une ✨',
                          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                        ),
                      ),
                      _buildFeaturedCarousel(featured),
                      const SizedBox(height: 20),
                    ],

                    const Padding(
                      padding: EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                      child: Text(
                        'Dernières Annonces',
                        style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                    ),
                    
                    AnimationLimiter(
                      child: Column(
                        children: List.generate(recent.length, (index) {
                          return AnimationConfiguration.staggeredList(
                            position: index,
                            duration: const Duration(milliseconds: 375),
                            child: SlideAnimation(
                              verticalOffset: 50.0,
                              child: FadeInAnimation(
                                child: _buildPropertyCard(recent[index]),
                              ),
                            ),
                          );
                        }),
                      ),
                    ),
                  ]),
                ),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildFeaturedCarousel(List<Property> featured) {
    return SizedBox(
      height: 250,
      child: ListView.builder(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.only(left: 20),
        itemCount: featured.length,
        itemBuilder: (context, index) {
          final p = featured[index];
          return GestureDetector(
            onTap: () => widget.onPropertyTap(p),
            child: Container(
              width: 300,
              margin: const EdgeInsets.only(right: 15),
              decoration: BoxDecoration(
                borderRadius: BorderRadius.circular(20),
                boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.1), blurRadius: 10)],
              ),
              child: ClipRRect(
                borderRadius: BorderRadius.circular(20),
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    CachedNetworkImage(
                      imageUrl: p.images.isNotEmpty ? p.images.first.imageUrl : '',
                      fit: BoxFit.cover,
                      placeholder: (context, url) => Container(color: Colors.grey[200]),
                      errorWidget: (context, url, error) => const Icon(Icons.error),
                    ),
                    Container(
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                          colors: [Colors.transparent, Colors.black.withOpacity(0.8)],
                        ),
                      ),
                    ),
                    Positioned(
                      bottom: 15,
                      left: 15,
                      right: 15,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: const Color(0xFFFFD700),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: const Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(Icons.bolt, size: 12, color: Colors.black),
                                Text(' PREMIUM', style: TextStyle(fontSize: 10, fontWeight: FontWeight.bold)),
                              ],
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            p.title,
                            style: const TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              Text(
                                '${NumberFormat.currency(locale: 'fr_FR', symbol: '', decimalDigits: 0).format(p.price)} FCFA',
                                style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.w900),
                              ),
                              Row(
                                children: [
                                  const Icon(Icons.location_on, color: Colors.white70, size: 14),
                                  Text(' ${p.neighborhood}', style: const TextStyle(color: Colors.white70, fontSize: 12)),
                                ],
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          );
        },
      ),
    );
  }

  Widget _buildPropertyCard(Property property) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 10, offset: const Offset(0, 4))],
      ),
      child: InkWell(
        onTap: () => widget.onPropertyTap(property),
        borderRadius: BorderRadius.circular(20),
        child: Row(
          children: [
            // Image
            Hero(
              tag: 'property-img-${property.id}',
              child: ClipRRect(
                borderRadius: const BorderRadius.only(topLeft: Radius.circular(20), bottomLeft: Radius.circular(20)),
                child: SizedBox(
                  width: 120,
                  height: 120,
                  child: CachedNetworkImage(
                    imageUrl: property.images.isNotEmpty ? property.images.first.imageUrl : '',
                    fit: BoxFit.cover,
                    placeholder: (context, url) => Shimmer.fromColors(
                      baseColor: Colors.grey[300]!,
                      highlightColor: Colors.grey[100]!,
                      child: Container(color: Colors.white),
                    ),
                    errorWidget: (context, url, error) => const Icon(Icons.error),
                  ),
                ),
              ),
            ),
            // Info
            Expanded(
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      property.title,
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                    const SizedBox(height: 4),
                    Text(
                      '${property.neighborhood}, ${property.city}',
                      style: TextStyle(color: Colors.grey[600], fontSize: 13),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '${NumberFormat.currency(locale: 'fr_FR', symbol: '', decimalDigits: 0).format(property.price)} F',
                          style: const TextStyle(color: Color(0xFF198754), fontWeight: FontWeight.w900, fontSize: 16),
                        ),
                        Row(
                          children: [
                            const Icon(Icons.bed, size: 14, color: Colors.grey),
                            Text(' ${property.bedrooms}', style: const TextStyle(fontSize: 12)),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSkeletonLoader() {
    return Shimmer.fromColors(
      baseColor: Colors.grey[300]!,
      highlightColor: Colors.grey[100]!,
      child: ListView.builder(
        shrinkWrap: true,
        physics: const NeverScrollableScrollPhysics(),
        itemCount: 5,
        padding: const EdgeInsets.all(20),
        itemBuilder: (context, index) {
          return Container(
            height: 100,
            margin: const EdgeInsets.only(bottom: 20),
            decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(15)),
          );
        },
      ),
    );
  }

  Widget _buildErrorWidget(String error) {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.wifi_off_rounded, size: 60, color: Colors.grey),
          const SizedBox(height: 16),
          Text('Erreur de connexion', style: TextStyle(color: Colors.grey[800], fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          const Text('Vérifiez votre internet ou réessayez plus tard', style: TextStyle(color: Colors.grey)),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: _refresh,
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF198754), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))),
            child: const Text('Réessayer', style: TextStyle(color: Colors.white)),
          ),
        ],
      ),
    );
  }
}
