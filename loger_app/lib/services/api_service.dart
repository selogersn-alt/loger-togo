import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:hive/hive.dart';
import '../models/property_model.dart';

class ApiService {
  static const String baseUrl = 'https://Logertogo.com/api';
  final _storage = const FlutterSecureStorage();

  Future<Map<String, dynamic>> fetchProperties({String? city, String? propertyType, String? neighborhood, String? search, int page = 1}) async {
    final queryParameters = <String, String>{};
    if (city != null && city != 'TOUT') queryParameters['city'] = city;
    if (propertyType != null && propertyType != 'TOUT') queryParameters['property_type'] = propertyType;
    if (neighborhood != null && neighborhood != 'TOUT') {
      queryParameters['neighborhood'] = _normalizeNeighborhood(neighborhood);
    }
    if (search != null && search.isNotEmpty) queryParameters['search'] = search;
    queryParameters['page'] = page.toString();

    final uri = Uri.parse('$baseUrl/properties/').replace(queryParameters: queryParameters);

    try {
      final response = await http.get(uri);
      if (response.statusCode == 200) {
        final dynamic decodedData = json.decode(utf8.decode(response.bodyBytes));
        debugPrint('API Response Type: ${decodedData.runtimeType}');
        if (decodedData is Map) debugPrint('API Keys: ${decodedData.keys}');
        
        List<dynamic> list;
        bool hasNext = false;

        if (decodedData is Map<String, dynamic>) {
          // Paginated response
          list = decodedData['results'] ?? [];
          hasNext = decodedData['next'] != null;

          // Caching logic for page 1 without filters
          if (page == 1 && city == null && propertyType == null && (search == null || search.isEmpty)) {
            try {
              final box = Hive.box('properties_cache');
              box.put('home_properties', list);
            } catch (e) {
              debugPrint('Cache Save Error: $e');
            }
          }
        } else if (decodedData is List) {
          // Legacy unpaginated response
          list = decodedData;
          hasNext = false;
        } else {
          throw Exception('Format de données inconnu');
        }

        final properties = list.map((json) {
          try {
            return Property.fromJson(Map<String, dynamic>.from(json));
          } catch (e) {
            debugPrint('Property Parse Error: $e');
            return null;
          }
        }).whereType<Property>().toList();

        return {
          'properties': properties,
          'next': hasNext,
        };
      } else {
        throw Exception('Erreur serveur (${response.statusCode})');
      }
    } catch (e) {
      debugPrint('ApiService Error: $e');
      throw Exception('Impossible de charger les annonces');
    }
  }

  String _normalizeNeighborhood(String name) {
    return name.trim().toUpperCase().replaceAll(' ', '_').replaceAll("'", "_").replaceAll("-", "_");
  }

  List<Property> getCachedProperties() {
    try {
      final box = Hive.box('properties_cache');
      final List<dynamic>? cached = box.get('home_properties');
      if (cached != null) {
        return cached.map((json) {
          try {
            return Property.fromJson(Map<String, dynamic>.from(json));
          } catch (e) {
            return null;
          }
        }).whereType<Property>().toList();
      }
    } catch (e) {
      debugPrint('Cache Load Error: $e');
    }
    return [];
  }

  Future<Map<String, dynamic>?> createProperty(Map<String, dynamic> data) async {
    final token = await _storage.read(key: 'access_token');
    if (token == null) return null;

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/properties/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: json.encode(data),
      );

      if (response.statusCode == 201) {
        return json.decode(response.body);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  Future<bool> uploadImage(String propertyId, File imageFile, {bool isPrimary = false}) async {
    final token = await _storage.read(key: 'access_token');
    if (token == null) return false;

    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('$baseUrl/property-images/'),
      );

      request.headers['Authorization'] = 'Bearer $token';
      request.fields['property'] = propertyId;
      request.fields['is_primary'] = isPrimary.toString();
      
      request.files.add(await http.MultipartFile.fromPath(
        'image_url',
        imageFile.path,
      ));

      final response = await request.send();
      return response.statusCode == 201;
    } catch (e) {
      return false;
    }
  }

  Future<List<Map<String, dynamic>>> fetchProfessionals() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/professionals/'));
      if (response.statusCode == 200) {
        final List<dynamic> list = json.decode(utf8.decode(response.bodyBytes));
        return list.cast<Map<String, dynamic>>();
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  // --- Favorites ---

  Future<bool> toggleFavorite(String propertyId) async {
    final token = await _storage.read(key: 'access_token');
    if (token == null) return false;

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/properties/$propertyId/toggle-favorite/'),
        headers: {'Authorization': 'Bearer $token'},
      );
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  Future<List<Property>> fetchFavorites() async {
    final token = await _storage.read(key: 'access_token');
    if (token == null) return [];

    try {
      final response = await http.get(
        Uri.parse('$baseUrl/properties/favorites/'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (response.statusCode == 200) {
        final List<dynamic> list = json.decode(utf8.decode(response.bodyBytes));
        return list.map((json) => Property.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  // --- Conversations & Chat ---

  Future<List<dynamic>> fetchConversations() async {
    final token = await _storage.read(key: 'access_token');
    if (token == null) return [];

    try {
      final response = await http.get(
        Uri.parse('$baseUrl/conversations/'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (response.statusCode == 200) {
        return json.decode(utf8.decode(response.bodyBytes));
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  Future<List<dynamic>> fetchMessages(String conversationId) async {
    final token = await _storage.read(key: 'access_token');
    if (token == null) return [];

    try {
      final response = await http.get(
        Uri.parse('$baseUrl/conversations/$conversationId/messages/'),
        headers: {'Authorization': 'Bearer $token'},
      );
      if (response.statusCode == 200) {
        return json.decode(utf8.decode(response.bodyBytes));
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  Future<bool> sendMessage(String conversationId, String content) async {
    final token = await _storage.read(key: 'access_token');
    if (token == null) return false;

    try {
      final response = await http.post(
        Uri.parse('$baseUrl/conversations/$conversationId/send_message/'),
        headers: {
          'Authorization': 'Bearer $token',
          'Content-Type': 'application/json',
        },
        body: json.encode({'content': content}),
      );
      return response.statusCode == 201;
    } catch (e) {
      return false;
    }
  }


}
