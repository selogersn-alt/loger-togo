import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:animate_do/animate_do.dart';
import '../models/property_model.dart';
import '../services/api_service.dart';
import 'package:share_plus/share_plus.dart';

class PropertyDetailScreen extends StatefulWidget {
  final Property property;
  const PropertyDetailScreen({super.key, required this.property});

  @override
  State<PropertyDetailScreen> createState() => _PropertyDetailScreenState();
}
class _PropertyDetailScreenState extends State<PropertyDetailScreen> {
  int _currentImageIndex = 0;
  final PageController _pageController = PageController();
  late Future<Map<String, dynamic>> _similarPropertiesFuture;
  final ApiService _apiService = ApiService();

  @override
  void initState() {
    super.initState();
    _similarPropertiesFuture = _apiService.fetchProperties(
      propertyType: widget.property.propertyType,
      city: widget.property.city,
    );
  }

  void _openGallery(int initialIndex) {
    showDialog(
      context: context,
      builder: (context) => Scaffold(
        backgroundColor: Colors.black,
        appBar: AppBar(
          backgroundColor: Colors.transparent,
          elevation: 0,
          leading: IconButton(
            icon: const Icon(Icons.close, color: Colors.white),
            onPressed: () => Navigator.pop(context),
          ),
        ),
        body: PageView.builder(
          itemCount: widget.property.images.length,
          controller: PageController(initialPage: initialIndex),
          itemBuilder: (context, index) => InteractiveViewer(
            child: CachedNetworkImage(
              imageUrl: widget.property.images[index].imageUrl,
              fit: BoxFit.contain,
            ),
          ),
        ),
      ),
    );
  }

  void _launchWhatsApp() async {
    final String propertyUrl = "https://Logertogo.com/annonces/${widget.property.id}/";
    final String message = "Bonjour, je suis intéressé par votre annonce : ${widget.property.title}.\nLien : $propertyUrl";
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

  void _launchSMS() async {
    final String message = "Bonjour, je suis intéressé par votre annonce : ${widget.property.title}";
    final String url = "sms:${widget.property.owner.phoneNumber}?body=${Uri.encodeComponent(message)}";
    if (await canLaunchUrl(Uri.parse(url))) {
      await launchUrl(Uri.parse(url));
    }
  }

  @override
  Widget build(BuildContext context) {
    final property = widget.property;
    final currencyFormatter = NumberFormat.decimalPattern('fr');

    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          CustomScrollView(
            physics: const BouncingScrollPhysics(),
            slivers: [
              SliverAppBar(
                expandedHeight: 400,
                pinned: true,
                stretch: true,
                backgroundColor: const Color(0xFF004D40),
                leading: Padding(
                  padding: const EdgeInsets.only(left: 16),
                  child: IconButton(
                    icon: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: const BoxDecoration(color: Colors.white, shape: BoxShape.circle),
                      child: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.black, size: 20),
                    ),
                    onPressed: () => Navigator.pop(context),
                  ),
                ),
                actions: [
                  Padding(
                    padding: const EdgeInsets.only(right: 16),
                    child: IconButton(
                      icon: Container(
                        padding: const EdgeInsets.all(8),
                        decoration: const BoxDecoration(color: Colors.white, shape: BoxShape.circle),
                        child: const Icon(Icons.share_rounded, color: Colors.black, size: 20),
                      ),
                      onPressed: () {
                        Share.share(
                          'Découvrez ce bien sur Loger Togo : ${property.title}\nLien : https://Logertogo.com/annonces/${property.id}/',
                        );
                      },
                    ),
                  ),
                ],
                flexibleSpace: FlexibleSpaceBar(
                  stretchModes: const [StretchMode.zoomBackground],
                  background: Stack(
                    fit: StackFit.expand,
                    children: [
                      PageView.builder(
                        controller: _pageController,
                        physics: const BouncingScrollPhysics(),
                        itemCount: property.images.length,
                        onPageChanged: (i) => setState(() => _currentImageIndex = i),
                        itemBuilder: (context, index) => GestureDetector(
                          onTap: () => _openGallery(index),
                          child: CachedNetworkImage(
                            imageUrl: property.images[index].imageUrl,
                            fit: BoxFit.cover,
                            placeholder: (context, url) => Container(color: Colors.grey[200]),
                            errorWidget: (context, url, error) => const Icon(Icons.error),
                          ),
                        ),
                      ),
                      IgnorePointer(
                        child: Container(
                          decoration: const BoxDecoration(
                            gradient: LinearGradient(
                              begin: Alignment.topCenter,
                              end: Alignment.bottomCenter,
                              colors: [Colors.black26, Colors.transparent, Colors.black45],
                            ),
                          ),
                        ),
                      ),
                      Positioned(
                        bottom: 40,
                        left: 0,
                        right: 0,
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: List.generate(
                            property.images.length,
                            (index) => Container(
                              margin: const EdgeInsets.symmetric(horizontal: 4),
                              width: _currentImageIndex == index ? 24 : 8,
                              height: 8,
                              decoration: BoxDecoration(
                                color: _currentImageIndex == index ? Colors.white : Colors.white54,
                                borderRadius: BorderRadius.circular(4),
                              ),
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),

              SliverToBoxAdapter(
                child: Transform.translate(
                  offset: const Offset(0, -30),
                  child: Container(
                    padding: const EdgeInsets.fromLTRB(24, 32, 24, 150),
                    decoration: const BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.vertical(top: Radius.circular(32)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                              decoration: BoxDecoration(color: Colors.amber.shade100, borderRadius: BorderRadius.circular(8)),
                              child: Text(property.listingCategoryDisplay, style: const TextStyle(color: Colors.amber, fontWeight: FontWeight.bold, fontSize: 10)),
                            ),
                            Text(
                              "${currencyFormatter.format(property.price)} F",
                              style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900, color: Color(0xFF004D40)),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Text(property.title, style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900, height: 1.1)),
                        const SizedBox(height: 12),
                        Row(
                          children: [
                            const Icon(Icons.location_on_rounded, size: 16, color: Color(0xFF004D40)),
                            const SizedBox(width: 4),
                            Text('${property.neighborhood}, ${property.city}', style: TextStyle(color: Colors.blueGrey, fontWeight: FontWeight.w500)),
                          ],
                        ),
                        const SizedBox(height: 32),
                        const Text('Caractéristiques', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 20),
                        Wrap(
                          spacing: 16,
                          runSpacing: 16,
                          children: [
                            _buildInfo(Icons.bed_rounded, '${property.bedrooms}', 'Chambres'),
                            _buildInfo(Icons.bathtub_rounded, '${property.toilets}', 'SdB'),
                            if (property.surface > 0) _buildInfo(Icons.square_foot_rounded, '${property.surface.toInt()}m²', 'Surface'),
                            if ((property.salons ?? 0) > 0) _buildInfo(Icons.weekend_rounded, '${property.salons}', 'Salons'),
                            if ((property.kitchens ?? 0) > 0) _buildInfo(Icons.countertops_rounded, '${property.kitchens}', 'Cuisines'),
                            if ((property.households ?? 0) > 0) _buildInfo(Icons.family_restroom_rounded, '${property.households}', 'Ménages'),
                            if ((property.floorLevel ?? 0) > 0) _buildInfo(Icons.stairs_rounded, '${property.floorLevel}', 'Étage'),
                          ],
                        ),
                        const SizedBox(height: 32),
                        const Divider(),
                        const SizedBox(height: 24),
                        const Text('Description', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 16),
                        Text(property.description, style: TextStyle(fontSize: 15, color: Colors.blueGrey.shade700, height: 1.6)),
                        const SizedBox(height: 48),
                        const Text('Biens Similaires', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                        const SizedBox(height: 16),
                        _buildSimilarProperties(),
                      ],
                    ),
                  ),
                ),
              ),
            ],
          ),

          Positioned(
            bottom: 24,
            left: 20,
            right: 20,
            child: FadeInUp(
              child: Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: const Color(0xFF1A1A1A),
                  borderRadius: BorderRadius.circular(24),
                  boxShadow: const [BoxShadow(color: Colors.black45, blurRadius: 20, offset: Offset(0, 10))],
                ),
                child: Row(
                  children: [
                    // SMS Button
                    _actionBtn(Icons.sms_rounded, _launchSMS),
                    const SizedBox(width: 12),
                    
                    // Main WhatsApp Button
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: _launchWhatsApp,
                        icon: const Icon(Icons.forum_rounded, color: Colors.white, size: 28),
                        label: const Text('WHATSAPP', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 16)),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFF25D366),
                          padding: const EdgeInsets.symmetric(vertical: 18),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                          elevation: 0,
                        ),
                      ),
                    ),
                    const SizedBox(width: 12),
                    
                    // Phone Button
                    _actionBtn(Icons.phone_rounded, _launchCall, color: const Color(0xFF004D40)),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSimilarProperties() {
    return FutureBuilder<Map<String, dynamic>>(
      future: _similarPropertiesFuture,
      builder: (context, snapshot) {
        if (!snapshot.hasData) return const SizedBox(height: 100);
        
        final list = (snapshot.data!['properties'] as List<Property>).where((p) => p.id != widget.property.id).take(5).toList();
        if (list.isEmpty) return const SizedBox.shrink();

        return SizedBox(
          height: 160,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: list.length,
            itemBuilder: (context, index) {
              final p = list[index];
              return GestureDetector(
                onTap: () {
                   Navigator.pushReplacement(
                     context,
                     MaterialPageRoute(builder: (context) => PropertyDetailScreen(property: p)),
                   );
                },
                child: Container(
                  width: 140,
                  margin: const EdgeInsets.only(right: 16),
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(16),
                    color: Colors.grey[100],
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      ClipRRect(
                        borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                        child: CachedNetworkImage(
                          imageUrl: p.images.isNotEmpty ? p.images.first.imageUrl : '',
                          height: 90,
                          width: 140,
                          fit: BoxFit.cover,
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.all(8.0),
                        child: Text(
                          p.title,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 8.0),
                        child: Text('${NumberFormat.compact().format(p.price)} F', style: const TextStyle(color: Color(0xFF004D40), fontWeight: FontWeight.bold, fontSize: 11)),
                      ),
                    ],
                  ),
                ),
              );
            },
          ),
        );
      },
    );
  }

  Widget _buildInfo(IconData icon, String val, String label) {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(color: const Color(0xFFF1F5F9), borderRadius: BorderRadius.circular(12)),
          child: Icon(icon, color: const Color(0xFF004D40), size: 20),
        ),
        const SizedBox(height: 8),
        Text(val, style: const TextStyle(fontWeight: FontWeight.bold)),
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10)),
      ],
    );
  }

  Widget _actionBtn(IconData icon, VoidCallback onTap, {Color color = Colors.white24}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(color: color.withOpacity(0.2), borderRadius: BorderRadius.circular(16)),
        child: Icon(icon, color: Colors.white, size: 24),
      ),
    );
  }
}
