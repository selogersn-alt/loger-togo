import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../core/constants/colors.dart';
import '../../data/models/property_model.dart';

class PropertyDetailScreen extends StatelessWidget {
  final Property property;
  const PropertyDetailScreen({super.key, required this.property});

  Future<void> _launchCall() async {
    final Uri url = Uri.parse('tel:${property.agentPhone ?? '+22890000000'}');
    if (!await launchUrl(url)) debugPrint('Error calling');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 350,
            pinned: true,
            backgroundColor: AppColors.primaryGreen,
            flexibleSpace: FlexibleSpaceBar(
              background: property.images.isNotEmpty
                ? PageView.builder(
                    itemCount: property.images.length,
                    itemBuilder: (context, index) => CachedNetworkImage(
                      imageUrl: property.images[index],
                      fit: BoxFit.cover,
                    ),
                  )
                : CachedNetworkImage(
                    imageUrl: property.mainImage ?? '',
                    fit: BoxFit.cover,
                  ),
            ),
          ),
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(25),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        '${property.price.toInt()} FCFA',
                        style: const TextStyle(color: AppColors.primaryGreen, fontSize: 28, fontWeight: FontWeight.bold),
                      ),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 15, vertical: 8),
                        decoration: BoxDecoration(color: AppColors.secondaryYellow, borderRadius: BorderRadius.circular(10)),
                        child: Text(
                          property.listingCategory.toUpperCase(),
                          style: const TextStyle(color: AppColors.primaryGreen, fontWeight: FontWeight.bold, fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 15),
                  Text(property.title, style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.textDark)),
                  const SizedBox(height: 10),
                  Row(
                    children: [
                      const Icon(Icons.location_on, color: AppColors.statusGreen, size: 20),
                      const SizedBox(width: 8),
                      Text('${property.neighborhood ?? ''}, ${property.city ?? ''}', style: const TextStyle(color: AppColors.textGrey, fontSize: 16)),
                    ],
                  ),
                  const Padding(padding: EdgeInsets.symmetric(vertical: 25), child: Divider()),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      _buildStat(Icons.king_bed_outlined, '${property.rooms ?? 0}', 'Chambres'),
                      _buildStat(Icons.bathtub_outlined, '${property.bathrooms ?? 0}', 'Douches'),
                      _buildStat(Icons.square_foot_outlined, '${property.area ?? 0}', 'm²'),
                    ],
                  ),
                  const Padding(padding: EdgeInsets.symmetric(vertical: 25), child: Divider()),
                  const Text('Description', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 12),
                  Text(property.description, style: const TextStyle(color: AppColors.textGrey, fontSize: 15, height: 1.6)),
                  const SizedBox(height: 120),
                ],
              ),
            ),
          ),
        ],
      ),
      bottomSheet: Container(
        padding: const EdgeInsets.all(20),
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.08), blurRadius: 20, offset: const Offset(0, -5))],
        ),
        child: SafeArea(
          child: Row(
            children: [
              Expanded(
                child: SizedBox(
                  height: 55,
                  child: ElevatedButton(
                    onPressed: () {},
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppColors.primaryGreen,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                    ),
                    child: const Text('ENVOYER UN MESSAGE', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ),
                ),
              ),
              const SizedBox(width: 15),
              SizedBox(
                height: 55,
                width: 55,
                child: ElevatedButton(
                  onPressed: _launchCall,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.secondaryYellow,
                    padding: EdgeInsets.zero,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                  ),
                  child: const Icon(Icons.phone, color: AppColors.primaryGreen),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStat(IconData icon, String val, String label) {
    return Column(
      children: [
        Icon(icon, color: AppColors.primaryGreen, size: 28),
        const SizedBox(height: 8),
        Text(val, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18)),
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
      ],
    );
  }
}
