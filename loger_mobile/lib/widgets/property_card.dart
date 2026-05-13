import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import '../core/constants/colors.dart';
import '../data/models/property_model.dart';
import '../screens/property/property_detail_screen.dart';

class PropertyCard extends StatelessWidget {
  final Property property;
  const PropertyCard({super.key, required this.property});

  Future<void> _launchWhatsApp() async {
    final String phone = property.agentPhone ?? '+22890000000';
    final Uri url = Uri.parse('https://wa.me/${phone.replaceAll('+', '').replaceAll(' ', '')}');
    if (!await launchUrl(url, mode: LaunchMode.externalApplication)) {
      debugPrint('Could not launch WhatsApp');
    }
  }

  Future<void> _launchCall() async {
    final String phone = property.agentPhone ?? '+22890000000';
    final Uri url = Uri.parse('tel:$phone');
    if (!await launchUrl(url)) {
      debugPrint('Could not launch dialer');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(bottom: 25),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.06),
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Image Section
          Stack(
            children: [
              ClipRRect(
                borderRadius: const BorderRadius.vertical(top: Radius.circular(20)),
                child: CachedNetworkImage(
                  imageUrl: property.mainImage ?? '',
                  width: double.infinity,
                  height: 240,
                  fit: BoxFit.cover,
                  placeholder: (context, url) => Container(color: AppColors.backgroundLight),
                  errorWidget: (context, url, error) => const Icon(Icons.error),
                ),
              ),
              Positioned(
                top: 15,
                left: 15,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildBadge(property.propertyType.toUpperCase(), Colors.white, AppColors.textDark),
                    const SizedBox(height: 6),
                    _buildBadge('EN ${property.listingCategory.toUpperCase()}', AppColors.statusGreen, Colors.white),
                    if (property.isPremium) ...[
                      const SizedBox(height: 6),
                      _buildBadge('PREMIUM', AppColors.secondaryYellow, AppColors.primaryGreen),
                    ],
                  ],
                ),
              ),
              Positioned(
                bottom: 0,
                right: 0,
                child: Container(
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                  decoration: const BoxDecoration(
                    color: AppColors.primaryGreen,
                    borderRadius: BorderRadius.only(topLeft: Radius.circular(20)),
                  ),
                  child: Column(
                    children: [
                      Text(
                        '${property.price.toInt()}'.replaceAllMapped(RegExp(r'(\d{1,3})(?=(\d{3})+(?!\d))'), (Match m) => '${m[1]} '),
                        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 19),
                      ),
                      Text(
                        'FCFA/${property.listingCategory == 'Location' ? 'Mois' : 'Vente'}',
                        style: const TextStyle(color: Colors.white70, fontSize: 11),
                      ),
                    ],
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
                  property.title,
                  style: const TextStyle(color: AppColors.primaryGreen, fontWeight: FontWeight.bold, fontSize: 19),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    const Icon(Icons.person, size: 18, color: AppColors.statusGreen),
                    const SizedBox(width: 8),
                    Text(
                      property.agentName ?? 'AGENT LOGER TOGO',
                      style: const TextStyle(color: AppColors.statusGreen, fontWeight: FontWeight.bold, fontSize: 14),
                    ),
                  ],
                ),
                const SizedBox(height: 10),
                Row(
                  children: [
                    const Icon(Icons.location_on, size: 18, color: AppColors.statusGreen),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        '${property.neighborhood ?? ''}, ${property.city ?? ''}'.toUpperCase(),
                        style: const TextStyle(color: AppColors.textGrey, fontSize: 13),
                      ),
                    ),
                    const Icon(Icons.access_time, size: 18, color: AppColors.statusGreen),
                    const SizedBox(width: 8),
                    const Text('Récemment', style: TextStyle(color: AppColors.textGrey, fontSize: 13)),
                  ],
                ),
                const Padding(padding: EdgeInsets.symmetric(vertical: 20), child: Divider()),
                Row(
                  children: [
                    _buildSocialButton(FontAwesomeIcons.whatsapp, Colors.green, _launchWhatsApp),
                    const SizedBox(width: 12),
                    _buildSocialButton(FontAwesomeIcons.phone, Colors.blue, _launchCall),
                    const Spacer(),
                    SizedBox(
                      height: 48,
                      child: ElevatedButton(
                        onPressed: () {
                          Navigator.push(context, MaterialPageRoute(builder: (_) => PropertyDetailScreen(property: property)));
                        },
                        style: ElevatedButton.styleFrom(
                          backgroundColor: AppColors.primaryGreen,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(30)),
                          padding: const EdgeInsets.symmetric(horizontal: 25),
                        ),
                        child: const Row(
                          children: [
                            Text('Détails', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 15)),
                            SizedBox(width: 8),
                            Icon(Icons.chevron_right, size: 20, color: Colors.white),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildBadge(String text, Color bgColor, Color textColor) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 7),
      decoration: BoxDecoration(color: bgColor, borderRadius: BorderRadius.circular(10)),
      child: Text(text, style: TextStyle(color: textColor, fontWeight: FontWeight.bold, fontSize: 11)),
    );
  }

  Widget _buildSocialButton(dynamic icon, Color color, VoidCallback onTap) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(12),
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          border: Border.all(color: color.withOpacity(0.3)),
          borderRadius: BorderRadius.circular(12),
        ),
        child: FaIcon(icon, color: color, size: 22),
      ),
    );
  }
}
