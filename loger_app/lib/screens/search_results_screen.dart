import 'package:flutter/material.dart';
import 'package:infinite_scroll_pagination/infinite_scroll_pagination.dart';
import '../models/property_model.dart';
import '../services/api_service.dart';
import 'property_detail_screen.dart';
import 'package:flutter_staggered_animations/flutter_staggered_animations.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:intl/intl.dart';
import 'package:timeago/timeago.dart' as timeago;

class SearchResultsScreen extends StatefulWidget {
  final String? city;
  final String? type;
  final String? neighborhood;
  final String? search;

  const SearchResultsScreen({
    super.key,
    this.city,
    this.type,
    this.neighborhood,
    this.search,
  });

  @override
  State<SearchResultsScreen> createState() => _SearchResultsScreenState();
}

class _SearchResultsScreenState extends State<SearchResultsScreen> {
  final ApiService _apiService = ApiService();
  final PagingController<int, Property> _pagingController = PagingController(firstPageKey: 1);
  List<Property> _recommendations = [];
  bool _isLoadingRecommendations = false;

  @override
  void initState() {
    super.initState();
    _pagingController.addPageRequestListener((pageKey) {
      _fetchPage(pageKey);
    });
  }

  Future<void> _fetchPage(int pageKey) async {
    try {
      final newItems = await _apiService.fetchProperties(
        page: pageKey,
        city: widget.city,
        propertyType: widget.type,
        neighborhood: widget.neighborhood,
        search: widget.search,
      );
      
      final items = newItems['properties'] as List<Property>;
      
      if (pageKey == 1 && items.isEmpty) {
        _fetchRecommendations();
      }

      final isLastPage = !newItems['next'];
      if (isLastPage) {
        _pagingController.appendLastPage(items);
      } else {
        final nextPageKey = pageKey + 1;
        _pagingController.appendPage(items, nextPageKey);
      }
    } catch (error) {
      _pagingController.error = error;
    }
  }

  Future<void> _fetchRecommendations() async {
    setState(() => _isLoadingRecommendations = true);
    try {
      final results = await _apiService.fetchProperties(page: 1);
      setState(() {
        _recommendations = results['properties'] as List<Property>;
        _isLoadingRecommendations = false;
      });
    } catch (e) {
      setState(() => _isLoadingRecommendations = false);
    }
  }

  @override
  void dispose() {
    _pagingController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Résultats', style: TextStyle(fontWeight: FontWeight.w900, color: Colors.black)),
        centerTitle: true,
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black),
      ),
      body: PagedListView<int, Property>(
        pagingController: _pagingController,
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 16),
        builderDelegate: PagedChildBuilderDelegate<Property>(
          itemBuilder: (context, item, index) => AnimationConfiguration.staggeredList(
            position: index,
            duration: const Duration(milliseconds: 600),
            child: SlideAnimation(
              verticalOffset: 50.0,
              child: FadeInAnimation(
                child: _buildPropertyCard(item),
              ),
            ),
          ),
          noItemsFoundIndicatorBuilder: (_) => _buildNoResults(),
        ),
      ),
    );
  }

  Widget _buildNoResults() {
    return Column(
      children: [
        const SizedBox(height: 40),
        const Icon(Icons.search_off_rounded, size: 80, color: Colors.grey),
        const SizedBox(height: 16),
        const Text(
          'Aucun résultat exact trouvé',
          style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 8),
        const Text(
          'Désolé, nous n\'avons rien trouvé correspondant à vos critères. Voici quelques biens qui pourraient vous intéresser :',
          textAlign: TextAlign.center,
          style: TextStyle(color: Colors.grey),
        ),
        const SizedBox(height: 40),
        if (_isLoadingRecommendations)
          const CircularProgressIndicator()
        else
          ..._recommendations.map((p) => _buildPropertyCard(p)).toList(),
      ],
    );
  }

  Widget _buildPropertyCard(Property property) {
    final currencyFormat = NumberFormat.currency(locale: 'fr_FR', symbol: 'F CFA', decimalDigits: 0);
    
    return GestureDetector(
      onTap: () => Navigator.push(
        context,
        MaterialPageRoute(builder: (context) => PropertyDetailScreen(property: property)),
      ),
      child: Container(
        margin: const EdgeInsets.only(bottom: 24),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(24),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.04),
              blurRadius: 20,
              offset: const Offset(0, 10),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Stack(
              children: [
                ClipRRect(
                  borderRadius: const BorderRadius.vertical(top: Radius.circular(24)),
                  child: AspectRatio(
                    aspectRatio: 16 / 9,
                    child: CachedNetworkImage(
                      imageUrl: property.images.isNotEmpty ? property.images.first.imageUrl : 'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&q=80&w=1000',
                      fit: BoxFit.cover,
                      placeholder: (context, url) => Container(color: Colors.grey.shade100),
                      errorWidget: (context, url, error) => Container(color: Colors.grey.shade100, child: const Icon(Icons.error)),
                    ),
                  ),
                ),
                Positioned(
                  top: 16,
                  left: 16,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                    decoration: BoxDecoration(color: const Color(0xFF27C66E), borderRadius: BorderRadius.circular(8)),
                    child: Text(
                      timeago.format(property.createdAt, locale: 'fr'),
                      style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w900, color: Colors.white),
                    ),
                  ),
                ),
              ],
            ),
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    property.propertyTypeDisplay,
                    style: TextStyle(color: Colors.green.shade700, fontWeight: FontWeight.bold, fontSize: 12, letterSpacing: 1),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    property.title,
                    style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 18),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      const Icon(Icons.location_on_outlined, size: 16, color: Colors.grey),
                      const SizedBox(width: 4),
                      Text('${property.neighborhood}, ${property.city}', style: const TextStyle(color: Colors.grey, fontSize: 14)),
                    ],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    currencyFormat.format(property.price),
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.w900, color: Color(0xFF27C66E)),
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
