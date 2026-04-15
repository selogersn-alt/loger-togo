import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/property_model.dart';
import '../services/api_service.dart';

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
  final List<String> _cities = ['ALL', 'DAKAR', 'THIES', 'MBOUR', 'SAINT-LOUIS'];

  @override
  void initState() {
    super.initState();
    _propertiesFuture = _apiService.fetchProperties();
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
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7F9),
      appBar: AppBar(
        title: const Text(
          'Loger Sénégal',
          style: TextStyle(fontWeight: FontWeight.bold, color: Colors.white),
        ),
        backgroundColor: const Color(0xFF0B4629),
        elevation: 0,
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(110),
          child: Column(
            children: [
              // Barre de Recherche
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 10),
                child: TextField(
                  controller: _searchController,
                  onSubmitted: (_) => _refresh(),
                  decoration: InputDecoration(
                    hintText: 'Chercher par quartier...',
                    prefixIcon: const Icon(Icons.search, color: Color(0xFF0B4629)),
                    suffixIcon: _searchController.text.isNotEmpty 
                      ? IconButton(icon: const Icon(Icons.clear), onPressed: () { _searchController.clear(); _refresh(); })
                      : null,
                    filled: true,
                    fillColor: Colors.white,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(30),
                      borderSide: BorderSide.none,
                    ),
                    contentPadding: const EdgeInsets.symmetric(vertical: 0),
                  ),
                ),
              ),
              // Filtres Villes
              SingleChildScrollView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.only(left: 15, bottom: 10),
                child: Row(
                  children: _cities.map((city) {
                    bool isSelected = _selectedCity == city;
                    return Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: ChoiceChip(
                        label: Text(city == 'ALL' ? 'Toutes les villes' : city),
                        selected: isSelected,
                        onSelected: (selected) {
                          if (selected) {
                            setState(() {
                              _selectedCity = city;
                              _refresh();
                            });
                          }
                        },
                        selectedColor: const Color(0xFF7FD47D),
                        backgroundColor: Colors.white,
                        labelStyle: TextStyle(
                          color: isSelected ? Colors.white : Colors.black87,
                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                          fontSize: 12,
                        ),
                      ),
                    );
                  }).toList(),
                ),
              ),
            ],
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh, color: Colors.white),
            onPressed: () {
              _searchController.clear();
              _selectedCity = 'ALL';
              _refresh();
            },
          ),
        ],
      ),
      body: FutureBuilder<List<Property>>(
        future: _propertiesFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(
              child: CircularProgressIndicator(color: Color(0xFF0B4629)),
            );
          } else if (snapshot.hasError) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.error_outline, size: 60, color: Colors.red),
                    const SizedBox(height: 16),
                    Text(
                      'Oups ! Impossible de charger les données.\n${snapshot.error}',
                      textAlign: TextAlign.center,
                      style: const TextStyle(color: Colors.grey),
                    ),
                    const SizedBox(height: 20),
                    ElevatedButton(
                      onPressed: _refresh,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: const Color(0xFF0B4629),
                      ),
                      child: const Text('Réessayer', style: TextStyle(color: Colors.white)),
                    ),
                  ],
                ),
              ),
            );
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('Aucune annonce disponible.'));
          }

          final properties = snapshot.data!;
          return RefreshIndicator(
            onRefresh: () async => _refresh(),
            color: const Color(0xFF0B4629),
            child: ListView.builder(
              padding: const EdgeInsets.all(12),
              itemCount: properties.length,
              itemBuilder: (context, index) {
                return _buildPropertyCard(properties[index]);
              },
            ),
          );
        },
      ),
    );
  }

  Widget _buildPropertyCard(Property property) {
    final currencyFormatter = NumberFormat.currency(
      locale: 'fr_FR',
      symbol: 'FCFA',
      decimalDigits: 0,
    );

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      elevation: 2,
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
      clipBehavior: Clip.antiAlias,
      child: InkWell(
        onTap: () => widget.onPropertyTap(property),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Stack(
              children: [
                AspectRatio(
                  aspectRatio: 16 / 9,
                  child: property.images.isNotEmpty
                      ? Image.network(
                          property.images.first.imageUrl,
                          fit: BoxFit.cover,
                          errorBuilder: (context, error, stackTrace) =>
                              const Center(child: Icon(Icons.broken_image, size: 50)),
                        )
                      : Container(
                          color: Colors.grey[200],
                          child: const Icon(Icons.home_work, size: 50, color: Colors.grey),
                        ),
                ),
                if (property.isBoosted)
                  Positioned(
                    top: 10,
                    right: 10,
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: Colors.amber,
                        borderRadius: BorderRadius.circular(5),
                      ),
                      child: const Row(
                        children: [
                          Icon(Icons.bolt, size: 14, color: Colors.black),
                          Text(
                            'PREMIUM',
                            style: TextStyle(
                              fontSize: 10,
                              fontWeight: FontWeight.bold,
                              color: Colors.black,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                Positioned(
                  bottom: 10,
                  left: 10,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                    decoration: BoxDecoration(
                      color: const Color(0xFF0B4629),
                      borderRadius: BorderRadius.circular(5),
                    ),
                    child: Text(
                      property.listingCategoryDisplay,
                      style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ],
            ),
            Padding(
              padding: const EdgeInsets.all(12),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    property.title,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      const Icon(Icons.location_on, size: 14, color: Colors.redAccent),
                      const SizedBox(width: 4),
                      Text(
                        '${property.neighborhood}, ${property.city}',
                        style: TextStyle(color: Colors.grey[600], fontSize: 13),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        currencyFormatter.format(property.price),
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.w900,
                          color: Color(0xFF0B4629),
                        ),
                      ),
                      Row(
                        children: [
                          const Icon(Icons.bed, size: 16, color: Colors.grey),
                          const SizedBox(width: 4),
                          Text('${property.bedrooms}', style: const TextStyle(fontSize: 13)),
                          const SizedBox(width: 12),
                          const Icon(Icons.bathtub, size: 16, color: Colors.grey),
                          const SizedBox(width: 4),
                          Text('${property.bathrooms}', style: const TextStyle(fontSize: 13)),
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
    );
  }
}
