import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/property_model.dart';

class ApiService {
  static const String baseUrl = 'https://logersenegal.com/api';
  final _storage = const FlutterSecureStorage();

  Future<List<Property>> fetchProperties({String? city, String? propertyType, String? search}) async {
    final queryParameters = <String, String>{};
    if (city != null && city != 'ALL') queryParameters['city'] = city;
    if (propertyType != null && propertyType != 'ALL') queryParameters['property_type'] = propertyType;
    if (search != null && search.isNotEmpty) queryParameters['search'] = search;

    final uri = Uri.parse('$baseUrl/properties/').replace(queryParameters: queryParameters);

    try {
      final response = await http.get(uri);
      if (response.statusCode == 200) {
        final List<dynamic> list = json.decode(utf8.decode(response.bodyBytes));
        return list.map((json) => Property.fromJson(json)).toList();
      } else {
        throw Exception('Erreur lors du chargement des annonces (${response.statusCode})');
      }
    } catch (e) {
      throw Exception('Erreur de connexion : $e');
    }
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
}
