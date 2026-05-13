import 'package:flutter/material.dart';
import '../core/utils/api_client.dart';
import '../data/models/property_model.dart';

class PropertyProvider with ChangeNotifier {
  final ApiClient _apiClient = ApiClient();
  
  List<Property> _boostedProperties = [];
  List<Property> _recentProperties = [];
  List<Property> _nearbyProperties = [];
  List<Property> _searchResults = [];
  bool _isLoading = false;

  List<Property> get boostedProperties => _boostedProperties;
  List<Property> get recentProperties => _recentProperties;
  List<Property> get nearbyProperties => _nearbyProperties;
  List<Property> get searchResults => _searchResults;
  bool get isLoading => _isLoading;

  List<Property> _parseResults(dynamic data) {
    final List results = (data is Map && data.containsKey('results')) 
        ? data['results'] 
        : (data is List ? data : []);
    return results.map((json) => Property.fromJson(json)).toList();
  }

  Future<void> fetchNearbyProperties(double lat, double lng) async {
    _isLoading = true;
    notifyListeners();
    try {
      final response = await _apiClient.dio.get('properties/', queryParameters: {
        'lat': lat,
        'lng': lng,
        'radius': 5000,
      });
      if (response.statusCode == 200) {
        _nearbyProperties = _parseResults(response.data);
      }
    } catch (e) {
      debugPrint('Error fetching nearby: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchBoostedProperties() async {
    _isLoading = true;
    notifyListeners();
    try {
      final response = await _apiClient.dio.get('properties/', queryParameters: {
        'is_premium': 'true',
      });
      if (response.statusCode == 200) {
        _boostedProperties = _parseResults(response.data);
      }
    } catch (e) {
      debugPrint('Error fetching boosted: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> fetchRecentProperties() async {
    _isLoading = true;
    notifyListeners();
    try {
      final response = await _apiClient.dio.get('properties/');
      if (response.statusCode == 200) {
        _recentProperties = _parseResults(response.data);
      }
    } catch (e) {
      debugPrint('Error fetching recent: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }

  Future<void> searchProperties({
    String? query,
    String? city,
    String? type,
    String? category,
    int? minPrice,
    int? maxPrice,
  }) async {
    _isLoading = true;
    notifyListeners();
    try {
      final params = <String, dynamic>{};
      if (query != null && query.isNotEmpty) params['search'] = query;
      if (city != null && city != 'Toutes les villes') params['city'] = city;
      if (type != null && type != 'Tous les types') params['property_type'] = type;
      if (category != null && category != 'Toutes catégories') params['listing_category'] = category;
      if (minPrice != null) params['min_price'] = minPrice;
      if (maxPrice != null) params['max_price'] = maxPrice;

      final response = await _apiClient.dio.get('properties/', queryParameters: params);
      if (response.statusCode == 200) {
        _searchResults = _parseResults(response.data);
      }
    } catch (e) {
      debugPrint('Error searching: $e');
    } finally {
      _isLoading = false;
      notifyListeners();
    }
  }
}
