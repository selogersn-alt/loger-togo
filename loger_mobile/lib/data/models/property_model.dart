class Property {
  final String id;
  final String title;
  final String description;
  final double price;
  final String? city;
  final String? neighborhood;
  final String propertyType;
  final String listingCategory;
  final List<String> images;
  final String? mainImage;
  final int? rooms;
  final int? bathrooms;
  final double? area;
  final bool isPremium;
  final DateTime? createdAt;
  final String? agentName;
  final String? agentPhone;
  final double? latitude;
  final double? longitude;

  Property({
    required this.id,
    required this.title,
    required this.description,
    required this.price,
    this.city,
    this.neighborhood,
    required this.propertyType,
    required this.listingCategory,
    required this.images,
    this.mainImage,
    this.rooms,
    this.bathrooms,
    this.area,
    this.isPremium = false,
    this.createdAt,
    this.agentName,
    this.agentPhone,
    this.latitude,
    this.longitude,
  });

  factory Property.fromJson(Map<String, dynamic> json) {
    // Parse images list from the list of PropertyImage objects
    final List<String> imageList = (json['images'] as List?)
        ?.map((e) => e['image_url']?.toString() ?? '')
        .where((url) => url.isNotEmpty)
        .toList() ?? [];

    return Property(
      id: json['id'].toString(),
      title: json['title'] ?? '',
      description: json['description'] ?? '',
      price: double.tryParse(json['price'].toString()) ?? 0.0,
      city: json['city'],
      neighborhood: json['neighborhood'],
      propertyType: json['property_type_display'] ?? json['property_type'] ?? '',
      listingCategory: json['listing_category_display'] ?? json['listing_category'] ?? '',
      images: imageList,
      mainImage: json['main_image'] ?? (imageList.isNotEmpty ? imageList[0] : null),
      rooms: json['total_rooms'] ?? json['rooms'] ?? 0,
      bathrooms: json['toilets'] ?? json['bathrooms'] ?? 0,
      area: double.tryParse(json['surface']?.toString() ?? json['area']?.toString() ?? ''),
      isPremium: json['is_boosted'] ?? json['is_premium'] ?? false,
      createdAt: json['created_at'] != null ? DateTime.parse(json['created_at']) : null,
      agentName: json['owner']?['company_name'] ?? json['owner']?['first_name'] ?? json['agent_name'],
      agentPhone: json['owner']?['phone_number'] ?? json['agent_phone'],
      latitude: double.tryParse(json['latitude']?.toString() ?? ''),
      longitude: double.tryParse(json['longitude']?.toString() ?? ''),
    );
  }
}
