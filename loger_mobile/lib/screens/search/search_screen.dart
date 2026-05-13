import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/colors.dart';
import '../../providers/property_provider.dart';
import '../../widgets/property_card.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final TextEditingController _queryController = TextEditingController();
  String _selectedCity = 'Toutes les villes';
  String _selectedType = 'Tous les types';
  String _selectedCategory = 'Toutes catégories';
  
  final List<String> _cities = ['Toutes les villes', 'Lomé', 'Aného', 'Kpalimé', 'Atakpamé', 'Sokodé', 'Kara', 'Dapaong'];
  final List<String> _types = ['Tous les types', 'Villa', 'Appartement', 'Terrain', 'Bureaux', 'Boutique', 'Chambre'];
  final List<String> _categories = ['Toutes catégories', 'Location', 'Vente', 'Nuitée'];

  @override
  void initState() {
    super.initState();
    Future.microtask(() => context.read<PropertyProvider>().searchProperties());
  }

  void _onSearch() {
    context.read<PropertyProvider>().searchProperties(
      query: _queryController.text,
      city: _selectedCity,
      type: _selectedType,
      category: _selectedCategory,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Explorer', style: TextStyle(fontWeight: FontWeight.bold)),
        elevation: 0,
        backgroundColor: Colors.white,
        foregroundColor: AppColors.primaryGreen,
      ),
      body: Column(
        children: [
          // Barre de recherche Premium
          Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              children: [
                TextField(
                  controller: _queryController,
                  onSubmitted: (_) => _onSearch(),
                  decoration: InputDecoration(
                    hintText: 'Rechercher...',
                    prefixIcon: const Icon(Icons.search, color: AppColors.primaryGreen),
                    filled: true,
                    fillColor: AppColors.backgroundLight,
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(15),
                      borderSide: BorderSide.none,
                    ),
                  ),
                ),
                const SizedBox(height: 15),
                Row(
                  children: [
                    Expanded(child: _buildDropdown(_selectedCity, _cities, (val) {
                      setState(() => _selectedCity = val!);
                      _onSearch();
                    })),
                    const SizedBox(width: 8),
                    Expanded(child: _buildDropdown(_selectedType, _types, (val) {
                      setState(() => _selectedType = val!);
                      _onSearch();
                    })),
                    const SizedBox(width: 8),
                    Expanded(child: _buildDropdown(_selectedCategory, _categories, (val) {
                      setState(() => _selectedCategory = val!);
                      _onSearch();
                    })),
                  ],
                ),
              ],
            ),
          ),

          // Résultats
          Expanded(
            child: Consumer<PropertyProvider>(
              builder: (context, provider, child) {
                if (provider.isLoading) {
                  return const Center(child: CircularProgressIndicator(color: AppColors.primaryGreen));
                }
                
                if (provider.searchResults.isEmpty) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.search_off, size: 60, color: Colors.grey[300]),
                        const SizedBox(height: 10),
                        const Text('Aucun résultat trouvé.', style: TextStyle(color: AppColors.textGrey)),
                      ],
                    ),
                  );
                }

                return ListView.builder(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  itemCount: provider.searchResults.length,
                  itemBuilder: (context, index) {
                    return PropertyCard(property: provider.searchResults[index]);
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDropdown(String current, List<String> options, Function(String?) onChanged) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10),
      decoration: BoxDecoration(
        color: AppColors.backgroundLight,
        borderRadius: BorderRadius.circular(12),
      ),
      child: DropdownButtonHideUnderline(
        child: DropdownButton<String>(
          value: current,
          isExpanded: true,
          style: const TextStyle(color: AppColors.primaryGreen, fontSize: 11, fontWeight: FontWeight.bold),
          items: options.map((String value) {
            return DropdownMenuItem<String>(
              value: value,
              child: Text(value, overflow: TextOverflow.ellipsis),
            );
          }).toList(),
          onChanged: onChanged,
        ),
      ),
    );
  }
}
