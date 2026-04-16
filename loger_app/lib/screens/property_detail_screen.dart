import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../models/property_model.dart';

class PropertyDetailScreen extends StatefulWidget {
  final Property property;

  const PropertyDetailScreen({super.key, required this.property});

  @override
  State<PropertyDetailScreen> createState() => _PropertyDetailScreenState();
}

class _PropertyDetailScreenState extends State<PropertyDetailScreen> {
  int _currentImageIndex = 0;

  void _launchWhatsApp() async {
    final String message = "Bonjour, je suis intéressé par votre annonce : ${widget.property.title}. L'offre est-elle toujours disponible ?";
    final String url = "https://wa.me/${widget.property.owner.phoneNumber}?text=${Uri.encodeComponent(message)}";
    if (await canLaunchUrl(Uri.parse(url))) {
      await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
    }
  }

  void _launchCall() async {
    final String url = "tel:${widget.property.owner.phoneNumber}";
    if (await canLaunchUrl(Uri.parse(url))) {
      await launchUrl(Uri.parse(url));
    }
  }

  @override
  Widget build(BuildContext context) {
    final property = widget.property;
    final currencyFormatter = NumberFormat.currency(
      locale: 'fr_FR',
      symbol: 'FCFA',
      decimalDigits: 0,
    );

    return Scaffold(
      backgroundColor: Colors.white,
      body: CustomScrollView(
        slivers: [
          // Elegant Parallax Header
          SliverAppBar(
            expandedHeight: 400,
            pinned: true,
            stretch: true,
            backgroundColor: const Color(0xFF198754),
            leading: IconButton(
              icon: const CircleAvatar(
                backgroundColor: Colors.white38,
                child: Icon(Icons.arrow_back, color: Colors.white, size: 20),
              ),
              onPressed: () => Navigator.pop(context),
            ),
            actions: [
              IconButton(
                icon: const CircleAvatar(
                  backgroundColor: Colors.white38,
                  child: Icon(Icons.share, color: Colors.white, size: 20),
                ),
                onPressed: () {
                  // TODO: Share logic
                },
              ),
              const SizedBox(width: 10),
            ],
            flexibleSpace: FlexibleSpaceBar(
              stretchModes: const [StretchMode.zoomBackground, StretchMode.blurBackground],
              background: Hero(
                tag: 'property-img-${widget.property.id}',
                child: Stack(
                  fit: StackFit.expand,
                  children: [
                    if (widget.property.images.isEmpty)
                      const Icon(Icons.home_work, size: 100, color: Colors.white24)
                    else
                      PageView.builder(
                        itemCount: widget.property.images.length,
                        onPageChanged: (index) {
                          setState(() => _currentImageIndex = index);
                        },
                        itemBuilder: (context, index) {
                          return CachedNetworkImage(
                            imageUrl: widget.property.images[index].imageUrl,
                            fit: BoxFit.cover,
                          );
                        },
                      ),
                    IgnorePointer(
                      child: DecoratedBox(
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                            begin: Alignment.topCenter,
                            end: Alignment.bottomCenter,
                            colors: [Colors.black45, Colors.transparent, Colors.black87],
                          ),
                        ),
                      ),
                    ),
                    // Indicator Dots
                    if (widget.property.images.length > 1)
                      IgnorePointer(
                        child: Positioned(
                          bottom: 60,
                          left: 0,
                          right: 0,
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: widget.property.images.asMap().entries.map((entry) {
                              return Container(
                                width: 8.0,
                                height: 8.0,
                                margin: const EdgeInsets.symmetric(horizontal: 4.0),
                                decoration: BoxDecoration(
                                  shape: BoxShape.circle,
                                  color: Colors.white.withOpacity(
                                    _currentImageIndex == entry.key ? 0.9 : 0.4
                                  ),
                                ),
                              );
                            }).toList(),
                          ),
                        ),
                      ),
                    if (widget.property.images.length > 1)
                      IgnorePointer(
                        child: Positioned(
                          bottom: 40,
                          right: 20,
                          child: Container(
                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
                            decoration: BoxDecoration(
                              color: Colors.black54,
                              borderRadius: BorderRadius.circular(15),
                            ),
                            child: Row(
                              children: [
                                const Icon(Icons.photo_library_rounded, color: Colors.white, size: 14),
                                const SizedBox(width: 5),
                                Text(
                                  '${_currentImageIndex + 1} / ${widget.property.images.length}',
                                  style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.bold),
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
          ),

          // Content
          SliverToBoxAdapter(
            child: Transform.translate(
              offset: const Offset(0, -30),
              child: Container(
                padding: const EdgeInsets.fromLTRB(25, 30, 25, 100),
                decoration: const BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.only(topLeft: Radius.circular(30), topRight: Radius.circular(30)),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: const Color(0xFF198754).withOpacity(0.1),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text(
                            widget.property.listingCategoryDisplay,
                            style: const TextStyle(color: Color(0xFF198754), fontWeight: FontWeight.bold, fontSize: 12),
                          ),
                        ),
                        if (widget.property.isBoosted)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                            decoration: BoxDecoration(
                              gradient: const LinearGradient(colors: [Color(0xFFFFD700), Color(0xFFFFA500)]),
                              borderRadius: BorderRadius.circular(20),
                            ),
                            child: const Text('BOOSTÉ ✨', style: TextStyle(fontWeight: FontWeight.w900, color: Colors.black, fontSize: 10)),
                          ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    Text(
                      widget.property.title,
                      style: const TextStyle(fontSize: 26, fontWeight: FontWeight.bold, height: 1.2),
                    ),
                    const SizedBox(height: 12),
                    Row(
                      children: [
                        const Icon(Icons.location_on_rounded, color: Colors.redAccent, size: 20),
                        const SizedBox(width: 6),
                        Text('${widget.property.neighborhood}, ${widget.property.city}', style: TextStyle(color: Colors.grey[600], fontSize: 16)),
                      ],
                    ),
                    const SizedBox(height: 25),
                    Text(
                      currencyFormatter.format(widget.property.price),
                      style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w900, color: Color(0xFF198754)),
                    ),
                    const SizedBox(height: 30),
                    
                    // Amenities
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        _buildBadge(Icons.bed_rounded, '${property.bedrooms}', 'Chambres'),
                        _buildBadge(Icons.bathtub_rounded, '${property.toilets}', 'Toilettes'),
                        _buildBadge(Icons.square_foot_rounded, '${property.surface.toInt()}', 'm²'),
                        _buildBadge(Icons.home_work_rounded, '', property.propertyTypeDisplay),
                      ],
                    ),
                    
                    const Padding(padding: EdgeInsets.symmetric(vertical: 25), child: Divider()),
                    
                    const Text('Description', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 12),
                    Text(
                      property.description,
                      style: TextStyle(fontSize: 16, color: Colors.grey[800], height: 1.6),
                    ),
                    
                    const SizedBox(height: 40),
                    
                    // Owner Card
                    Container(
                      padding: const EdgeInsets.all(20),
                      decoration: BoxDecoration(
                        color: const Color(0xFFF8FAFC),
                        borderRadius: BorderRadius.circular(24),
                        border: Border.all(color: Colors.grey[200]!),
                      ),
                      child: Column(
                        children: [
                          Row(
                            children: [
                              CircleAvatar(
                                radius: 25,
                                backgroundColor: const Color(0xFF198754),
                                child: Text(property.owner.firstName[0], style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                              ),
                              const SizedBox(width: 15),
                              Expanded(
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: [
                                    Text(property.owner.displayName, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
                                    const Row(
                                      children: [
                                        Icon(Icons.verified, color: Colors.blue, size: 16),
                                        SizedBox(width: 4),
                                        Text('Professionnel Vérifié', style: TextStyle(color: Colors.grey, fontSize: 12)),
                                      ],
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 25),
                          Row(
                            children: [
                              Expanded(
                                child: ElevatedButton.icon(
                                  onPressed: _launchWhatsApp,
                                  icon: const Icon(Icons.forum_rounded, color: Colors.white),
                                  label: const Text('WhatsApp', style: TextStyle(fontWeight: FontWeight.bold)),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: const Color(0xFF25D366),
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(vertical: 15),
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                                    elevation: 0,
                                  ),
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: ElevatedButton.icon(
                                  onPressed: _launchCall,
                                  icon: const Icon(Icons.phone_rounded, color: Colors.white),
                                  label: const Text('Appeler', style: TextStyle(fontWeight: FontWeight.bold)),
                                  style: ElevatedButton.styleFrom(
                                    backgroundColor: const Color(0xFF198754),
                                    foregroundColor: Colors.white,
                                    padding: const EdgeInsets.symmetric(vertical: 15),
                                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                                    elevation: 0,
                                  ),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 15),
                          SizedBox(
                            width: double.infinity,
                            child: ElevatedButton.icon(
                              onPressed: () {
                                // Logic for application / Solvable integration
                              },
                              icon: const Icon(Icons.description_rounded, color: Colors.white),
                              label: const Text('POSTULER À CETTE ANNONCE', style: TextStyle(fontWeight: FontWeight.w900, letterSpacing: 1.1)),
                              style: ElevatedButton.styleFrom(
                                backgroundColor: const Color(0xFF2C3E50),
                                foregroundColor: Colors.white,
                                padding: const EdgeInsets.symmetric(vertical: 18),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                                elevation: 4,
                                shadowColor: Colors.black45,
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBadge(IconData icon, String value, String unit) {
    return Container(
      width: 75,
      padding: const EdgeInsets.symmetric(vertical: 12),
      decoration: BoxDecoration(
        color: const Color(0xFFF8FAFC),
        borderRadius: BorderRadius.circular(15),
        border: Border.all(color: Colors.grey[100]!),
      ),
      child: Column(
        children: [
          Icon(icon, color: const Color(0xFF198754), size: 24),
          const SizedBox(height: 6),
          Text(
            value,
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
          ),
          Text(unit, style: const TextStyle(color: Colors.grey, fontSize: 10)),
        ],
      ),
    );
  }
}
