import 'dart:async';
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:local_auth/local_auth.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:io';
import 'package:image_picker/image_picker.dart';
import 'package:file_picker/file_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:intl/intl.dart';

import 'screens/property_list_screen.dart';
import 'screens/property_detail_screen.dart';
import 'screens/login_screen.dart';
import 'screens/add_property_screen.dart';
import 'services/auth_service.dart';
import 'models/user_model.dart';

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
        colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF0B4629)),
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
    // 1. Charger l'utilisateur en tâche de fond
    await AuthService().loadUser();
    
    // 2. Vérifier si la sécurité est activée dans les réglages
    final prefs = await SharedPreferences.getInstance();
    final bool isSecurityEnabled = prefs.getBool('security_enabled') ?? true; // Activé par défaut

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

        if (didAuthenticate) {
          _navigateToHome();
        }
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
            Image.asset('assets/img/logo.png', width: 200),
            const SizedBox(height: 30),
            const CircularProgressIndicator(color: Color(0xFF0B4629)),
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
  final WebViewController controller = WebViewController();
  double progress = 0;
  final ImagePicker _picker = ImagePicker();

  @override
  void initState() {
    super.initState();
    controller
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onProgress: (val) => setState(() => progress = val / 100),
          onPageStarted: (url) => setState(() => progress = 0),
          onPageFinished: (url) => setState(() => progress = 1),
        ),
      )
      ..loadRequest(Uri.parse('https://logersenegal.com'));

    if (Platform.isAndroid) {
      _setupFilePicker();
    }
  }

  void _setupFilePicker() {
    // Code de gestion du sélecteur de fichiers Android fusionné
  }

  void _onTabTapped(int index) {
    setState(() => _selectedIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
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
            Column(
              children: [
                if (progress < 1)
                  LinearProgressIndicator(
                    value: progress,
                    backgroundColor: Colors.white,
                    color: const Color(0xFF7FD47D),
                    minHeight: 2,
                  ),
                Expanded(
                  child: WebViewWidget(controller: controller),
                ),
              ],
            ),
            const ProfileScreen(),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onTabTapped,
        selectedItemColor: const Color(0xFF0B4629),
        unselectedItemColor: Colors.grey,
        type: BottomNavigationBarType.fixed,
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined),
            activeIcon: Icon(Icons.home),
            label: 'Accueil',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.language_outlined),
            activeIcon: Icon(Icons.language),
            label: 'Site Web',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline),
            activeIcon: Icon(Icons.person),
            label: 'Profil',
          ),
        ],
      ),
      floatingActionButton: _selectedIndex == 0 ? FloatingActionButton.extended(
        onPressed: () async {
          final loggedIn = await AuthService().isLoggedIn();
          if (!loggedIn && mounted) {
            await Navigator.of(context).push(MaterialPageRoute(builder: (context) => const LoginScreen()));
            return;
          }
          if (mounted) {
             Navigator.of(context).push(MaterialPageRoute(builder: (context) => const AddPropertyScreen()));
          }
        },
        backgroundColor: const Color(0xFF0B4629),
        icon: const Icon(Icons.add_photo_alternate, color: Colors.white),
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
      return const Center(child: CircularProgressIndicator());
    }

    return Scaffold(
      backgroundColor: const Color(0xFFF5F7F9),
      body: CustomScrollView(
        slivers: [
          SliverAppBar(
            expandedHeight: 120,
            floating: false,
            pinned: true,
            backgroundColor: const Color(0xFF0B4629),
            flexibleSpace: FlexibleSpaceBar(
              title: Text(user.displayName, style: const TextStyle(color: Colors.white, fontSize: 16)),
              background: Container(color: const Color(0xFF0B4629)),
            ),
          ),
          SliverToBoxAdapter(
            child: Column(
              children: [
                const SizedBox(height: 20),
                // En-tête du profil
                Container(
                  padding: const EdgeInsets.all(20),
                  margin: const EdgeInsets.symmetric(horizontal: 15),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10)],
                  ),
                  child: Column(
                    children: [
                      CircleAvatar(
                        radius: 40,
                        backgroundColor: const Color(0xFF0B4629).withOpacity(0.1),
                        child: const Icon(Icons.person, size: 50, color: Color(0xFF0B4629)),
                      ),
                      const SizedBox(height: 15),
                      Text(
                        '${user.firstName} ${user.lastName}',
                        style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 5),
                      Text(user.email, style: const TextStyle(color: Colors.grey)),
                      const SizedBox(height: 15),
                      if (user.isVerified)
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                          decoration: BoxDecoration(
                            color: const Color(0xFF0B4629).withOpacity(0.1),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: const Row(
                            mainAxisSize: MainAxisSize.min,
                            children: [
                              Icon(Icons.verified, color: Color(0xFF0B4629), size: 16),
                              SizedBox(width: 5),
                              Text('Profil Vérifié', style: TextStyle(color: Color(0xFF0B4629), fontWeight: FontWeight.bold, fontSize: 12)),
                            ],
                          ),
                        ),
                    ],
                  ),
                ),
                
                const SizedBox(height: 25),
                
                // Réglages de sécurité
                Container(
                  padding: const EdgeInsets.all(10),
                  margin: const EdgeInsets.symmetric(horizontal: 15),
                  decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(15)),
                  child: SwitchListTile(
                    activeColor: const Color(0xFF0B4629),
                    title: const Text('Sécurité Biométrique', style: TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: const Text('Activer le verrouillage au démarrage'),
                    value: _securityEnabled,
                    onChanged: _toggleSecurity,
                    secondary: const Icon(Icons.security, color: Color(0xFF0B4629)),
                  ),
                ),
                
                const SizedBox(height: 10),
                
                // Menu d'options
                _buildMenuItem(Icons.home_work_outlined, 'Mes Annonces', () {}),
                _buildMenuItem(Icons.favorite_outline, 'Mes Favoris', () {}),
                _buildMenuItem(Icons.help_outline, 'Besoin d\'aide ?', () {}),
                
                const SizedBox(height: 30),
                
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 15),
                  child: TextButton.icon(
                    onPressed: () async {
                      await AuthService().logout();
                    },
                    icon: const Icon(Icons.logout, color: Colors.red),
                    label: const Text('Se déconnecter', style: TextStyle(color: Colors.red, fontWeight: FontWeight.bold)),
                  ),
                ),
                const SizedBox(height: 50),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMenuItem(IconData icon, String title, VoidCallback onTap) {
    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 15, vertical: 5),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(12)),
      child: ListTile(
        leading: Icon(icon, color: const Color(0xFF0B4629)),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
        trailing: const Icon(Icons.chevron_right, size: 18),
        onTap: onTap,
      ),
    );
  }
}
