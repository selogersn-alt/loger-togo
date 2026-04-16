import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/api_service.dart';

class ExploreProfessionalsScreen extends StatefulWidget {
  const ExploreProfessionalsScreen({super.key});

  @override
  State<ExploreProfessionalsScreen> createState() => _ExploreProfessionalsScreenState();
}

class _ExploreProfessionalsScreenState extends State<ExploreProfessionalsScreen> {
  final ApiService _apiService = ApiService();
  late Future<List<Map<String, dynamic>>> _prosFuture;

  @override
  void initState() {
    super.initState();
    _prosFuture = _apiService.fetchProfessionals();
  }

  void _launchCall(String phone) async {
    final url = "tel:$phone";
    if (await canLaunchUrl(Uri.parse(url))) {
      await launchUrl(Uri.parse(url));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text('Professionnels Certifiés', style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold, fontSize: 18)),
        backgroundColor: Colors.white,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back_ios_new_rounded, color: Colors.black, size: 20),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: FutureBuilder<List<Map<String, dynamic>>>(
        future: _prosFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator(color: Color(0xFF198754)));
          }
          if (snapshot.hasError) {
            return Center(child: Text('Erreur: ${snapshot.error}'));
          }

          final allPros = snapshot.data ?? [];
          // Filter only verified pros as requested in audio
          final pros = allPros.where((p) => p['is_verified_pro'] == true).toList();
          
          if (pros.isEmpty) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(40.0),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.person_search_rounded, size: 80, color: Colors.grey),
                    SizedBox(height: 20),
                    Text('Aucun professionnel certifié disponible pour le moment.', textAlign: TextAlign.center),
                  ],
                ),
              ),
            );
          }

          return ListView.builder(
            padding: const EdgeInsets.all(20),
            itemCount: pros.length,
            itemBuilder: (context, index) {
              final pro = pros[index];
              
              return Container(
                margin: const EdgeInsets.only(bottom: 20),
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(20),
                  boxShadow: [
                    BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 15, offset: const Offset(0, 8)),
                  ],
                ),
                child: Column(
                  children: [
                    Row(
                      children: [
                        CircleAvatar(
                          radius: 35,
                          backgroundColor: const Color(0xFF198754).withOpacity(0.1),
                          backgroundImage: pro['profile_picture'] != null 
                            ? CachedNetworkImageProvider(pro['profile_picture']) 
                            : null,
                          child: pro['profile_picture'] == null 
                            ? const Icon(Icons.account_balance_rounded, color: Color(0xFF198754), size: 30) 
                            : null,
                        ),
                        const SizedBox(width: 15),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                children: [
                                  Expanded(
                                    child: Text(
                                      pro['company_name'] ?? pro['full_name'],
                                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 17),
                                      maxLines: 1,
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                                    decoration: BoxDecoration(
                                      color: const Color(0xFF198754).withOpacity(0.1),
                                      borderRadius: BorderRadius.circular(10),
                                    ),
                                    child: const Row(
                                      children: [
                                        Icon(Icons.verified_rounded, color: Color(0xFF198754), size: 14),
                                        SizedBox(width: 4),
                                        Text('Certifié', style: TextStyle(color: Color(0xFF198754), fontSize: 10, fontWeight: FontWeight.bold)),
                                      ],
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 6),
                              Row(
                                children: [
                                  const Icon(Icons.location_on_rounded, size: 14, color: Colors.redAccent),
                                  const SizedBox(width: 4),
                                  Text(
                                    pro['coverage_area'] ?? 'Sénégal',
                                    style: TextStyle(color: Colors.grey[600], fontSize: 13),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    const Divider(),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          '${pro['properties_count'] ?? 0} annonces actives',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12, color: Colors.blueGrey),
                        ),
                        Row(
                          children: [
                            IconButton(
                              onPressed: () => _launchCall(pro['phone_number']),
                              icon: const CircleAvatar(
                                backgroundColor: Color(0xFF198754),
                                radius: 18,
                                child: Icon(Icons.phone_rounded, color: Colors.white, size: 16),
                              ),
                            ),
                            IconButton(
                              onPressed: () {
                                // TODO: Messaging
                              },
                              icon: CircleAvatar(
                                backgroundColor: const Color(0xFF198754).withOpacity(0.1),
                                radius: 18,
                                child: const Icon(Icons.chat_bubble_rounded, color: Color(0xFF198754), size: 16),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ],
                ),
              );
            },
          );
        },
      ),
    );
  }
}
