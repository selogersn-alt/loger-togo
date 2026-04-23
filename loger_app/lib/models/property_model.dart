class Property {
  final String id;
  final String title;
  final String? slug;
  final String description;
  final double price;
  final double? pricePerNight;
  final String city;
  final String neighborhood;
  final String propertyType;
  final String propertyTypeDisplay;
  final String listingCategory;
  final String listingCategoryDisplay;
  final int bedrooms;
  final int toilets;
  final int? totalRooms;
  final int? salons;
  final int? kitchens;
  final int? households;
  final int? floorLevel;
  final bool hasGarage;
  final bool hasBalcony;
  final bool hasTerrace;
  final String? documentType;
  final bool isBoosted;
  final DateTime createdAt;
  final List<PropertyImage> images;
  final Owner owner;
  final String absoluteUrl;
  final double surface;
  final double latitude;
  final double longitude;

  Property({
    required this.id,
    required this.title,
    this.slug,
    required this.description,
    required this.price,
    this.pricePerNight,
    required this.city,
    required this.neighborhood,
    required this.propertyType,
    required this.propertyTypeDisplay,
    required this.listingCategory,
    required this.listingCategoryDisplay,
    required this.bedrooms,
    required this.toilets,
    this.totalRooms,
    this.salons,
    this.kitchens,
    this.households,
    this.floorLevel,
    this.hasGarage = false,
    this.hasBalcony = false,
    this.hasTerrace = false,
    this.documentType,
    required this.surface,
    required this.isBoosted,
    required this.createdAt,
    required this.images,
    required this.owner,
    required this.absoluteUrl,
    this.latitude = 0.0,
    this.longitude = 0.0,
  });

  factory Property.fromJson(Map<String, dynamic> json) {
    return Property(
      id: json['id'].toString(),
      title: json['title'] ?? '',
      slug: json['slug'],
      description: json['description'] ?? '',
      price: double.tryParse(json['price']?.toString() ?? '0') ?? 0.0,
      pricePerNight: json['price_per_night'] != null ? double.tryParse(json['price_per_night'].toString()) : null,
      city: json['city'] ?? '',
      neighborhood: json['neighborhood'] ?? '',
      propertyType: json['property_type'] ?? '',
      propertyTypeDisplay: json['property_type_display'] ?? '',
      listingCategory: json['listing_category'] ?? '',
      listingCategoryDisplay: json['listing_category_display'] ?? '',
      bedrooms: json['bedrooms'] ?? 0,
      toilets: json['toilets'] ?? 0,
      totalRooms: json['total_rooms'],
      salons: json['salons'],
      kitchens: json['kitchens'],
      households: json['households'],
      floorLevel: json['floor_level'],
      hasGarage: json['has_garage'] ?? false,
      hasBalcony: json['has_balcony'] ?? false,
      hasTerrace: json['has_terrace'] ?? false,
      documentType: json['document_type'],
      surface: double.tryParse(json['surface']?.toString() ?? '0') ?? 0.0,
      isBoosted: json['is_boosted'] ?? false,
      createdAt: DateTime.tryParse(json['created_at']?.toString() ?? '') ?? DateTime.now(),
      images: (json['images'] as List?)?.map((i) => PropertyImage.fromJson(i)).toList() ?? [],
      owner: Owner.fromJson(json['owner'] ?? {}),
      absoluteUrl: json['absolute_url'] ?? '',
      latitude: double.tryParse(json['latitude']?.toString() ?? '0') ?? 0.0,
      longitude: double.tryParse(json['longitude']?.toString() ?? '0') ?? 0.0,
    );
  }
}

class PropertyImage {
  final String id;
  final String imageUrl;

  PropertyImage({required this.id, required this.imageUrl});

  factory PropertyImage.fromJson(Map<String, dynamic> json) {
    // Some API versions use 'image', others 'image_url'
    String url = json['image_url'] ?? json['image'] ?? '';
    return PropertyImage(
      id: json['id'].toString(),
      imageUrl: url,
    );
  }
}

class Owner {
  final String id;
  final String firstName;
  final String lastName;
  final String? companyName;
  final String phoneNumber;

  Owner({
    required this.id,
    required this.firstName,
    required this.lastName,
    this.companyName,
    required this.phoneNumber,
  });

  factory Owner.fromJson(Map<String, dynamic> json) {
    return Owner(
      id: json['id'].toString(),
      firstName: json['first_name'] ?? '',
      lastName: json['last_name'] ?? '',
      companyName: json['company_name'],
      phoneNumber: json['phone_number'] ?? '',
    );
  }

  String get displayName => companyName ?? '$firstName $lastName';
}
