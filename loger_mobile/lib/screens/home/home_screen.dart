import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/colors.dart';
import '../../providers/property_provider.dart';
import '../../widgets/property_card.dart';
import '../search/search_screen.dart';
import '../auth/login_screen.dart';
import '../profile/profile_screen.dart';
import '../property/post_property_screen.dart';
import '../property/favorites_screen.dart';
import '../chat/chat_list_screen.dart';
import '../around_me/around_me_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  final List<Widget> _pages = [
    const _HomeBody(),
    const SearchScreen(),
    const AroundMeScreen(),
    const ChatListScreen(),
    const ProfileScreen(),
  ];

  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      context.read<PropertyProvider>().fetchBoostedProperties();
      context.read<PropertyProvider>().fetchRecentProperties();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.white,
      appBar: AppBar(
        backgroundColor: Colors.white,
        elevation: 0,
        leadingWidth: 150,
        leading: Padding(
          padding: const EdgeInsets.only(left: 15),
          child: Image.asset(
            'assets/images/logo.png',
            fit: BoxFit.contain,
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_none, color: AppColors.primaryGreen, size: 26),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.menu, color: AppColors.primaryGreen, size: 28),
            onPressed: () {},
          ),
        ],
      ),
      body: _pages[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) => setState(() => _selectedIndex = index),
        selectedItemColor: AppColors.primaryGreen,
        unselectedItemColor: AppColors.textGrey,
        showUnselectedLabels: true,
        type: BottomNavigationBarType.fixed,
        selectedFontSize: 10,
        unselectedFontSize: 10,
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home_outlined, size: 24), activeIcon: Icon(Icons.home, size: 24), label: 'Accueil'),
          BottomNavigationBarItem(icon: Icon(Icons.search, size: 24), label: 'Explorer'),
          BottomNavigationBarItem(icon: Icon(Icons.gps_fixed, size: 24), label: 'Autour'),
          BottomNavigationBarItem(icon: Icon(Icons.chat_bubble_outline, size: 24), activeIcon: Icon(Icons.chat_bubble, size: 24), label: 'Messages'),
          BottomNavigationBarItem(icon: Icon(Icons.person_outline, size: 24), activeIcon: Icon(Icons.person, size: 24), label: 'Profil'),
        ],
      ),
    );
  }
}

class _HomeBody extends StatelessWidget {
  const _HomeBody();

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        children: [
          // Hero Section
          Container(
            width: double.infinity,
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 40),
            decoration: const BoxDecoration(
              color: AppColors.primaryGreen,
            ),
            child: Column(
              children: [
                RichText(
                  textAlign: TextAlign.center,
                  text: const TextSpan(
                    style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white),
                    children: [
                      TextSpan(text: 'Trouvez votre '),
                      TextSpan(text: 'logement\nidéal', style: TextStyle(color: AppColors.secondaryYellow)),
                      TextSpan(text: ' au Togo'),
                    ],
                  ),
                ),
                const SizedBox(height: 15),
                const Text(
                  'La plateforme immobilière la plus fiable pour louer ou acheter en toute sérénité.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.white70, fontSize: 14),
                ),
                const SizedBox(height: 30),
                
                // Floating Search Card
                Container(
                  padding: const EdgeInsets.all(20),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(25),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      _buildSearchField('JE CHERCHE...', 'Toutes les natures'),
                      const Divider(height: 30),
                      _buildSearchField('TYPE DE BIEN', 'Tous les types'),
                      const Divider(height: 30),
                      _buildSearchField('OÙ ? (VILLE)', 'Tout le Togo'),
                      const SizedBox(height: 25),
                      Center(
                        child: SizedBox(
                          width: double.infinity,
                          height: 55,
                          child: ElevatedButton(
                            onPressed: () {
                              // We could navigate to SearchScreen tab or open search
                            },
                            style: ElevatedButton.styleFrom(
                              backgroundColor: AppColors.secondaryYellow,
                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                            ),
                            child: const Row(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.search, color: AppColors.primaryGreen),
                                SizedBox(width: 10),
                                Text('RECHERCHER', style: TextStyle(color: AppColors.primaryGreen, fontWeight: FontWeight.bold, fontSize: 16)),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          // Recent Ads Section
          Padding(
            padding: const EdgeInsets.all(20),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Expanded(
                  child: Text(
                    'Annonces récentes',
                    style: TextStyle(color: AppColors.primaryGreen, fontWeight: FontWeight.bold, fontSize: 20),
                  ),
                ),
                TextButton(
                  onPressed: () {},
                  child: const Text('Tout voir', style: TextStyle(color: AppColors.statusGreen)),
                ),
              ],
            ),
          ),
          
          Consumer<PropertyProvider>(
            builder: (context, provider, child) {
              if (provider.isLoading && provider.recentProperties.isEmpty) {
                return const Center(child: CircularProgressIndicator(color: AppColors.primaryGreen));
              }
              return ListView.builder(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                padding: const EdgeInsets.symmetric(horizontal: 20),
                itemCount: provider.recentProperties.length,
                itemBuilder: (context, index) => PropertyCard(property: provider.recentProperties[index]),
              );
            },
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  Widget _buildSearchField(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 10, fontWeight: FontWeight.bold)),
        const SizedBox(height: 5),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(value, style: const TextStyle(color: AppColors.primaryGreen, fontWeight: FontWeight.bold, fontSize: 16)),
            const Icon(Icons.keyboard_arrow_down, color: Colors.grey),
          ],
        ),
      ],
    );
  }
}
