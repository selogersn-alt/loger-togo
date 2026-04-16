import 'package:flutter/material.dart';
import 'package:local_auth/local_auth.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:intl/intl.dart';
import 'package:cached_network_image/cached_network_image.dart';
import 'package:url_launcher/url_launcher.dart';

import 'models/property_model.dart';
import 'models/chat_model.dart';
import 'screens/property_list_screen.dart';
import 'screens/property_detail_screen.dart';
import 'screens/add_property_screen.dart';
import 'screens/professionals_screen.dart';
import 'screens/login_screen.dart';
import 'screens/chat_detail_screen.dart';
import 'screens/solvency_docs_screen.dart';
import 'services/auth_service.dart';
import 'services/api_service.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const LogerApp());
}

class LogerApp extends StatelessWidget {
  const LogerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Loger Sénégal',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF198754),
          primary: const Color(0xFF198754),
        ),
        useMaterial3: true,
      ),
      home: const SplashScreen(),
    );
  }
}

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  final LocalAuthentication auth = LocalAuthentication();

  @override
  void initState() {
    super.initState();
    _handleStartup();
  }

  Future<void> _handleStartup() async {
    await AuthService().loadUser();
    final prefs = await SharedPreferences.getInstance();
    final bool isSecurityEnabled = prefs.getBool('security_enabled') ?? true;

    if (isSecurityEnabled) {
      _checkBiometrics();
    } else {
      _navigateToHome();
    }
  }

  Future<void> _checkBiometrics() async {
    try {
      final bool canAuthenticateWithBiometrics = await auth.canCheckBiometrics;
      final bool canAuthenticate = canAuthenticateWithBiometrics || await auth.isDeviceSupported();

      if (canAuthenticate) {
        final bool didAuthenticate = await auth.authenticate(
          localizedReason: 'Sécurisez votre accès à Loger Sénégal',
          options: const AuthenticationOptions(
            stickyAuth: true,
            biometricOnly: false,
          ),
        );
        if (didAuthenticate) _navigateToHome();
      } else {
        _navigateToHome();
      }
    } catch (e) {
      _navigateToHome();
    }
  }

  void _navigateToHome() {
    if (mounted) {
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (context) => const MainNavigation()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset('assets/img/logo.png', width: 220),
            const SizedBox(height: 40),
            const CircularProgressIndicator(color: Color(0xFF198754)),
          ],
        ),
      ),
    );
  }
}

class MainNavigation extends StatefulWidget {
  const MainNavigation({super.key});

  @override
  State<MainNavigation> createState() => _MainNavigationState();
}

class _MainNavigationState extends State<MainNavigation> {
  int _selectedIndex = 0;

  void _onTabTapped(int index) {
    setState(() => _selectedIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            const NewsMarquee(),
            Expanded(
              child: IndexedStack(
                index: _selectedIndex,
                children: [
                  PropertyListScreen(
                    onPropertyTap: (property) {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (context) => PropertyDetailScreen(property: property),
                        ),
                      );
                    },
                  ),
                  const ExploreProfessionalsScreen(),
                  const MessagesScreen(),
                  const FavoritesScreen(),
                  const ProfileScreen(),
                ],
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onTabTapped,
        selectedItemColor: const Color(0xFF198754),
        unselectedItemColor: Colors.grey[600],
        type: BottomNavigationBarType.fixed,
        backgroundColor: Colors.white,
        elevation: 20,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home_rounded),
            label: 'Accueil',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.business_outlined),
            activeIcon: Icon(Icons.business_rounded),
            label: 'Pros',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.chat_bubble_outline_rounded),
            activeIcon: Icon(Icons.chat_bubble_rounded),
            label: 'Chat',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.favorite_outline_rounded),
            activeIcon: Icon(Icons.favorite_rounded),
            label: 'Favoris',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline_rounded),
            activeIcon: Icon(Icons.person_rounded),
            label: 'Profil',
          ),
        ],
      ),
      floatingActionButton: _selectedIndex == 0 ? FloatingActionButton.extended(
        onPressed: () async {
          final url = Uri.parse('https://logersenegal.com/annonces/nouvelle/');
          if (await canLaunchUrl(url)) {
            await launchUrl(url, mode: LaunchMode.externalApplication);
          }
        },
        elevation: 4,
        backgroundColor: const Color(0xFF198754),
        icon: const Icon(Icons.add_photo_alternate_rounded, color: Colors.white),
        label: const Text('Publier', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
      ) : null,
    );
  }
}

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  bool _securityEnabled = true;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _securityEnabled = prefs.getBool('security_enabled') ?? true;
    });
  }

  Future<void> _toggleSecurity(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool('security_enabled', value);
    setState(() {
      _securityEnabled = value;
    });
  }

  @override
  Widget build(BuildContext context) {
    final user = AuthService().currentUser;

    if (user == null) {
      return Scaffold(
        backgroundColor: Colors.white,
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(40.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Image.asset('assets/img/logo.png', width: 140),
                const SizedBox(height: 40),
                const Text(
                  'Espace Membre',
                  style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Color(0xFF198754)),
                ),
                const SizedBox(height: 15),
                const Text(
                  'Pour gérer vos annonces, vos baux et votre profil, veuillez vous connecter sur notre plateforme web sécurisée.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: Colors.grey, height: 1.5),
                ),
                const SizedBox(height: 40),
                SizedBox(
                  width: double.infinity,
                  child: ElevatedButton(
                    onPressed: () async {
                      final url = Uri.parse('https://logersenegal.com/connexion/');
                      if (await canLaunchUrl(url)) {
                        await launchUrl(url, mode: LaunchMode.externalApplication);
                      }
                    },
                    style: ElevatedButton.styleFrom(
                      backgroundColor: const Color(0xFF198754),
                      padding: const EdgeInsets.symmetric(vertical: 18),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                    ),
                    child: const Text('SE CONNECTER SUR LE WEB', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                  ),
                ),
                const SizedBox(height: 20),
                TextButton(
                  onPressed: () async {
                    final url = Uri.parse('https://logersenegal.com/inscription/');
                    if (await canLaunchUrl(url)) {
                      await launchUrl(url, mode: LaunchMode.externalApplication);
                    }
                  },
                  child: const Text("Créer un compte sur le site", style: TextStyle(color: Color(0xFF198754))),
                ),
              ],
            ),
          ),
        ),
      );
    }

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 140,
            floating: false,
            pinned: true,
            backgroundColor: const Color(0xFF198754),
            elevation: 0,
            flexibleSpace: FlexibleSpaceBar(
              title: Text(user.displayName, style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
              background: Container(
                decoration: const BoxDecoration(
                  gradient: LinearGradient(
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                    colors: [Color(0xFF198754), Color(0xFF146c43)],
                  ),
                ),
              ),
            ),
          ),
          SliverToBoxAdapter(
            child: Column(
              children: [
                const SizedBox(height: 20),
                // Premium Profile Card
                Container(
                  padding: const EdgeInsets.all(25),
                  margin: const EdgeInsets.symmetric(horizontal: 20),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(24),
                    boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 20, offset: const Offset(0, 10))],
                  ),
                  child: Column(
                    children: [
                      CircleAvatar(
                        radius: 45,
                        backgroundColor: const Color(0xFF198754).withOpacity(0.1),
                        child: const Icon(Icons.person_rounded, size: 55, color: Color(0xFF198754)),
                      ),
                      const SizedBox(height: 20),
                      Text(
                        '${user.firstName} ${user.lastName}',
                        style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 6),
                      Text(user.email, style: TextStyle(color: Colors.grey[600])),
                      const SizedBox(height: 20),
                      if (user.isVerified)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                          decoration: BoxDecoration(
                            color: const Color(0xFF198754).withOpacity(0.1),
                            borderRadius: BorderRadius.circular(30),
                          ),
                          child: const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.verified_rounded, color: Color(0xFF198754), size: 18),
                              SizedBox(width: 6),
                              Text('Professionnel Certifié', style: TextStyle(color: Color(0xFF198754), fontWeight: FontWeight.bold, fontSize: 13)),
                            ],
                          ),
                        ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 30),
                
                // Security Section
                _buildSectionTitle('SÉCURITÉ'),
                _buildProfileItem(
                  Icons.fingerprint_rounded,
                  'Protection Biométrique',
                  'Verrouiller l\'accès à l\'ouverture',
                  trailing: Switch.adaptive(
                    activeColor: const Color(0xFF198754),
                    value: _securityEnabled,
                    onChanged: _toggleSecurity,
                  ),
                ),
                
                const SizedBox(height: 20),
                
                // Reseau Solvable Section
                _buildSectionTitle('RÉSEAU SOLVABLE'),
                Container(
                  margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 5),
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(colors: [Color(0xFF2C3E50), Color(0xFF000000)]),
                    borderRadius: BorderRadius.circular(18),
                  ),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.shield_rounded, color: Colors.amber, size: 30),
                          const SizedBox(width: 15),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text('Votre Score de Solvabilité', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                                Text(user.isVerified ? 'Vérifié - Niveau 1' : 'Non vérifié', style: const TextStyle(color: Colors.white70, fontSize: 12)),
                              ],
                            ),
                          ),
                          TextButton(
                            onPressed: () {
                              Navigator.of(context).push(
                                MaterialPageRoute(builder: (context) => const SolvencyDocsScreen()),
                              );
                            },
                            child: const Text('DÉTAILS', style: TextStyle(color: Colors.amber, fontWeight: FontWeight.bold)),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 20),
                
                // Account Section
                _buildSectionTitle('MES SERVICES'),
                _buildProfileItem(Icons.home_work_rounded, 'Mes Annonces', 'Gérer mes publications'),
                _buildProfileItem(Icons.description_rounded, 'Mes Contrats', 'Baux et quittances PDF'),
                _buildProfileItem(Icons.help_center_rounded, 'Centre d\'aide', 'Assistance Loger Sénégal'),
                
                const SizedBox(height: 40),
                
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 20),
                  child: SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      onPressed: () => AuthService().logout(),
                      icon: const Icon(Icons.logout_rounded),
                      label: const Text('Se déconnecter', style: TextStyle(fontWeight: FontWeight.bold)),
                      style: OutlinedButton.styleFrom(
                        foregroundColor: Colors.redAccent,
                        side: const BorderSide(color: Colors.redAccent),
                        padding: const EdgeInsets.symmetric(vertical: 15),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 60),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.only(left: 25, bottom: 10, top: 10),
      child: Align(
        alignment: Alignment.centerLeft,
        child: Text(title, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: Colors.grey, letterSpacing: 1.2)),
      ),
    );
  }

  Widget _buildProfileItem(IconData icon, String title, String subtitle, {Widget? trailing}) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 5),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(18)),
      child: ListTile(
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(color: const Color(0xFFF8FAFC), borderRadius: BorderRadius.circular(12)),
          child: Icon(icon, color: const Color(0xFF198754), size: 22),
        ),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
        subtitle: Text(subtitle, style: const TextStyle(fontSize: 12, color: Colors.grey)),
        trailing: trailing ?? const Icon(Icons.chevron_right_rounded, color: Colors.grey),
        onTap: trailing == null ? () {} : null,
      ),
    );
  }
}

class MessagesScreen extends StatefulWidget {
  const MessagesScreen({super.key});

  @override
  State<MessagesScreen> createState() => _MessagesScreenState();
}

class _MessagesScreenState extends State<MessagesScreen> {
  final ApiService _apiService = ApiService();
  late Future<List<dynamic>> _conversationsFuture;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  void _refresh() {
    setState(() {
      _conversationsFuture = _apiService.fetchConversations();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text('Messagerie', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 0,
      ),
      body: FutureBuilder<List<dynamic>>(
        future: _conversationsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator(color: Color(0xFF198754)));
          }
          if (snapshot.hasError || !snapshot.hasData || snapshot.data!.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.chat_bubble_outline_rounded, size: 80, color: Colors.grey[300]),
                  const SizedBox(height: 20),
                  Text(
                    snapshot.hasError ? 'Erreur de chargement' : 'Vos conversations s\'afficheront ici',
                    style: const TextStyle(color: Colors.grey, fontSize: 16)
                  ),
                ],
              ),
            );
          }

          final conversations = (snapshot.data as List).map((c) => Conversation.fromJson(c)).toList();
          return RefreshIndicator(
            onRefresh: () async => _refresh(),
            child: ListView.separated(
              itemCount: conversations.length,
              separatorBuilder: (context, index) => Divider(height: 1, color: Colors.grey[100]),
              itemBuilder: (context, index) {
                final conv = conversations[index];
                return _buildConversationItem(conv);
              },
            ),
          );
        },
      ),
    );
  }

  Widget _buildConversationItem(Conversation conv) {
    // Basic logic to find the "other" person's name
    final otherParticipant = conv.participants.firstWhere(
      (p) => p.id != AuthService().currentUser?.id.toString(),
      orElse: () => ChatUser(id: '0', displayName: 'Support'),
    );

    return ListTile(
      contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      leading: CircleAvatar(
        radius: 28,
        backgroundColor: const Color(0xFF198754).withOpacity(0.1),
        child: Text(
          otherParticipant.displayName[0].toUpperCase(),
          style: const TextStyle(color: Color(0xFF198754), fontWeight: FontWeight.bold),
        ),
      ),
      title: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Text(otherParticipant.displayName, 
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
          ),
          Text(
            DateFormat('HH:mm').format(conv.updatedAt),
            style: TextStyle(color: Colors.grey[500], fontSize: 12),
          ),
        ],
      ),
      subtitle: Padding(
        padding: const EdgeInsets.only(top: 5),
        child: Text(
          conv.lastMessage?.content ?? 'Pas de message',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(color: Colors.grey[600]),
        ),
      ),
      onTap: () {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (context) => ChatDetailScreen(conversation: conv),
          ),
        );
      },
    );
  }
}

class FavoritesScreen extends StatefulWidget {
  const FavoritesScreen({super.key});

  @override
  State<FavoritesScreen> createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends State<FavoritesScreen> {
  final ApiService _apiService = ApiService();
  late Future<List<Property>> _favoritesFuture;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  void _refresh() {
    setState(() {
      _favoritesFuture = _apiService.fetchFavorites();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text('Mes Favoris', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 0,
      ),
      body: FutureBuilder<List<Property>>(
        future: _favoritesFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator(color: Color(0xFF198754)));
          }
          if (snapshot.hasError || !snapshot.hasData || snapshot.data!.isEmpty) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.favorite_outline_rounded, size: 80, color: Colors.grey[300]),
                  const SizedBox(height: 20),
                  Text(
                    snapshot.hasError ? 'Erreur de chargement' : 'Aucun favori pour le moment',
                    style: const TextStyle(color: Colors.grey, fontSize: 16)
                  ),
                ],
              ),
            );
          }

          final favorites = snapshot.data!;
          return RefreshIndicator(
            onRefresh: () async => _refresh(),
            child: ListView.builder(
              padding: const EdgeInsets.all(15),
              itemCount: favorites.length,
              itemBuilder: (context, index) {
                final property = favorites[index];
                return _buildFavoriteItem(property);
              },
            ),
          );
        },
      ),
    );
  }

  Widget _buildFavoriteItem(Property property) {
    return Card(
      margin: const EdgeInsets.only(bottom: 15),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
      child: ListTile(
        contentPadding: const EdgeInsets.all(10),
        leading: ClipRRect(
          borderRadius: BorderRadius.circular(10),
          child: property.images.isNotEmpty
              ? CachedNetworkImage(
                  imageUrl: property.images.first.imageUrl,
                  width: 80,
                  height: 80,
                  fit: BoxFit.cover,
                  placeholder: (context, url) => Container(color: Colors.grey[200]),
                )
              : Container(width: 80, height: 80, color: Colors.grey[200]),
        ),
        title: Text(property.title, maxLines: 1, overflow: TextOverflow.ellipsis, 
          style: const TextStyle(fontWeight: FontWeight.bold)),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('${NumberFormat.decimalPattern('fr').format(property.price)} FCFA',
                style: const TextStyle(color: Color(0xFF198754), fontWeight: FontWeight.bold)),
            Text(property.neighborhood, style: TextStyle(color: Colors.grey[600], fontSize: 12)),
          ],
        ),
        trailing: IconButton(
          icon: const Icon(Icons.favorite_rounded, color: Colors.red),
          onPressed: () async {
            await _apiService.toggleFavorite(property.id);
            _refresh();
          },
        ),
        onTap: () {
          Navigator.of(context).push(
            MaterialPageRoute(builder: (context) => PropertyDetailScreen(property: property)),
          );
        },
      ),
    );
  }
}

class NewsMarquee extends StatefulWidget {
  const NewsMarquee({super.key});

  @override
  State<NewsMarquee> createState() => _NewsMarqueeState();
}

class _NewsMarqueeState extends State<NewsMarquee> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      duration: const Duration(seconds: 40),
      vsync: this,
    )..repeat();
    _animation = Tween<double>(begin: 1.0, end: -1.0).animate(_controller);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 35,
      width: double.infinity,
      color: const Color(0xFFC62828),
      child: AnimatedBuilder(
        animation: _animation,
        builder: (context, child) {
          return ClipRect(
            child: FractionalTranslation(
              translation: Offset(_animation.value * 2, 0.0),
              child: const Center(
                child: Text(
                  "🛡️ SÉCURITÉ : Ne versez jamais d'argent avant d'avoir visité le bien. | 🤝 RÉSEAU SOLVABLE : Les meilleurs professionnels du Sénégal à votre service. | 📊 +1500 annonces vérifiées cette semaine.",
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                  maxLines: 1,
                  overflow: TextOverflow.visible,
                  softWrap: false,
                ),
              ),
            ),
          );
        },
      ),
    );
  }
}
