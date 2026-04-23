import 'package:flutter/material.dart';
import 'package:local_auth/local_auth.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:google_fonts/google_fonts.dart';
import 'package:animate_do/animate_do.dart';
import 'package:flutter_spinkit/flutter_spinkit.dart';

import 'models/property_model.dart';
import 'screens/property_list_screen.dart';
import 'screens/property_detail_screen.dart';
import 'screens/professionals_screen.dart';
import 'screens/settings_screen.dart';
import 'services/auth_service.dart';
import 'services/notification_service.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:sentry_flutter/sentry_flutter.dart';
import 'package:timeago/timeago.dart' as timeago;

void main() async {
  timeago.setLocaleMessages('fr', timeago.FrMessages());
  WidgetsFlutterBinding.ensureInitialized();
  
  await SentryFlutter.init(
    (options) {
      options.dsn = 'https://example@sentry.io/123456'; // À remplacer par le vrai DNS
      options.tracesSampleRate = 1.0;
    },
    appRunner: () async {
      try {
        await Firebase.initializeApp();
        await NotificationService.initialize();
      } catch (e) {
        debugPrint('Firebase/Notification Init Error: $e');
      }
  
      await Hive.initFlutter();
      await Hive.openBox('properties_cache');
  
      runApp(const LogerApp());
    },
  );
}

class LogerApp extends StatelessWidget {
  const LogerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Loger Togo',
      theme: ThemeData(
        useMaterial3: true,
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF004D40),
          primary: const Color(0xFF004D40),
          secondary: const Color(0xFF1A237E),
          surface: Colors.white,
        ),
        textTheme: GoogleFonts.outfitTextTheme(Theme.of(context).textTheme),
        scaffoldBackgroundColor: const Color(0xFFF0F2F5),
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
    final bool isSecurityEnabled = prefs.getBool('use_biometrics') ?? false;

    if (isSecurityEnabled) {
      _checkBiometrics();
    } else {
      _navigateToHome();
    }
  }

  Future<void> _checkBiometrics() async {
    try {
      final bool canAuthenticate = await auth.canCheckBiometrics || await auth.isDeviceSupported();
      if (canAuthenticate) {
        final bool didAuthenticate = await auth.authenticate(
          localizedReason: 'Sécurisez votre accès à Loger Togo',
          options: const AuthenticationOptions(stickyAuth: true),
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
            FadeInDown(
              // Taille réduite pour éviter l'overflow
              child: Image.asset('assets/img/logo.png', width: 180),
            ),
            const SizedBox(height: 20),
            FadeInUp(
              child: const Text(
                "L'immobilier en toute confiance",
                style: TextStyle(color: Color(0xFF004D40), fontWeight: FontWeight.bold, fontSize: 13),
              ),
            ),
            const SizedBox(height: 40),
            const SpinKitFadingCube(color: Color(0xFF004D40), size: 30.0),
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
      body: Column(
        children: [
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
                const FavoritesScreen(),
                const SettingsScreen(),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.only(top: 8),
        decoration: BoxDecoration(
          color: Colors.white,
          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 20, offset: const Offset(0, -4))],
        ),
        child: BottomNavigationBar(
          currentIndex: _selectedIndex,
          onTap: _onTabTapped,
          selectedItemColor: const Color(0xFF004D40),
          unselectedItemColor: Colors.blueGrey.shade200,
          showSelectedLabels: true,
          showUnselectedLabels: true,
          type: BottomNavigationBarType.fixed,
          backgroundColor: Colors.white,
          elevation: 0,
          selectedFontSize: 11,
          unselectedFontSize: 10,
          selectedLabelStyle: const TextStyle(fontWeight: FontWeight.w900),
          items: const [
            BottomNavigationBarItem(
              icon: Icon(Icons.grid_view_rounded, size: 22),
              activeIcon: Icon(Icons.grid_view_rounded, size: 26),
              label: 'Accueil',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.explore_outlined, size: 22),
              activeIcon: Icon(Icons.explore_rounded, size: 26),
              label: 'Pros',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.favorite_outline_rounded, size: 22),
              activeIcon: Icon(Icons.favorite_rounded, size: 26),
              label: 'Favoris',
            ),
            BottomNavigationBarItem(
              icon: Icon(Icons.tune_rounded, size: 22),
              activeIcon: Icon(Icons.tune_rounded, size: 26),
              label: 'Paramètres',
            ),
          ],
        ),
      ),
    );
  }
}

class FavoritesScreen extends StatefulWidget {
  const FavoritesScreen({super.key});

  @override
  State<FavoritesScreen> createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends State<FavoritesScreen> {
  // Favorites implementation dummy (shared_prefs linked)
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text('Favoris', style: TextStyle(fontWeight: FontWeight.w900)),
        centerTitle: true,
        backgroundColor: Colors.white,
        elevation: 0,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.favorite_border_rounded, size: 80, color: Colors.blueGrey.shade100),
            const SizedBox(height: 16),
            const Text('Vos coups de coeur s\'afficheront ici', style: TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }
}
