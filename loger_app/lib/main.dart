import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:local_auth/local_auth.dart';
import 'package:flutter/services.dart';
import 'package:file_picker/file_picker.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:webview_flutter_android/webview_flutter_android.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:io';
import 'screens/property_list_screen.dart';
import 'screens/property_detail_screen.dart';
import 'screens/login_screen.dart';
import 'screens/add_property_screen.dart';
import 'services/auth_service.dart';
import 'models/user_model.dart';



void main() {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setSystemUIOverlayStyle(const SystemUiOverlayStyle(
    statusBarColor: Colors.transparent,
    statusBarIconBrightness: Brightness.light,
  ));
  runApp(const LogerApp());
}

class LogerApp extends StatelessWidget {
  const LogerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Loger Sénégal',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          seedColor: const Color(0xFF0B4629),
          primary: const Color(0xFF0B4629),
          secondary: const Color(0xFF7FD47D),
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
  @override
  void initState() {
    super.initState();
    Future.delayed(const Duration(seconds: 3), () {
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => const BiometricAuthScreen()),
        );
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B4629),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset(
              'assets/img/logo.png',
              width: 180,
              errorBuilder: (context, error, stackTrace) => const Icon(
                Icons.home_work,
                size: 80,
                color: Color(0xFF7FD47D),
              ),
            ),
            const SizedBox(height: 30),
            const CircularProgressIndicator(
              color: Color(0xFF7FD47D),
              strokeWidth: 2,
            ),
          ],
        ),
      ),
    );
  }
}

class BiometricAuthScreen extends StatefulWidget {
  const BiometricAuthScreen({super.key});

  @override
  State<BiometricAuthScreen> createState() => _BiometricAuthScreenState();
}

class _BiometricAuthScreenState extends State<BiometricAuthScreen> {
  final LocalAuthentication auth = LocalAuthentication();
  bool _isAuthenticating = false;

  @override
  void initState() {
    super.initState();
    _authenticate();
  }

  Future<void> _authenticate() async {
    bool authenticated = false;
    try {
      setState(() {
        _isAuthenticating = true;
      });
      authenticated = await auth.authenticate(
        localizedReason: 'Accès sécurisé à votre tableau de bord immobilier',
        options: const AuthenticationOptions(
          stickyAuth: true,
          biometricOnly: false,
        ),
      );
    } on PlatformException catch (e) {
      debugPrint(e.toString());
      authenticated = true; // Fallback pour les appareils sans biométrie
    }

    if (!mounted) return;

    if (authenticated) {
      Navigator.of(context).pushReplacement(
        PageRouteBuilder(
          pageBuilder: (context, animation, secondaryAnimation) => const LogerHomePage(),
          transitionsBuilder: (context, animation, secondaryAnimation, child) {
            return FadeTransition(opacity: animation, child: child);
          },
        ),
      );
    } else {
      setState(() {
        _isAuthenticating = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0B4629),
      body: Container(
        width: double.infinity,
        padding: const EdgeInsets.symmetric(horizontal: 30),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Image.asset(
              'assets/img/logo.png',
              width: 120,
              errorBuilder: (context, error, stackTrace) => const Icon(
                Icons.lock_outline,
                size: 60,
                color: Color(0xFF7FD47D),
              ),
            ),
            const SizedBox(height: 40),
            const Text(
              'SÉCURITÉ SOLVABLE',
              style: TextStyle(
                color: Colors.white,
                fontSize: 18,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.5,
              ),
            ),
            const SizedBox(height: 10),
            const Text(
              'Veuillez vous authentifier',
              style: TextStyle(color: Color(0xFF7FD47D), fontSize: 14),
            ),
            const SizedBox(height: 80),
            if (!_isAuthenticating)
              IconButton(
                icon: const Icon(Icons.fingerprint, size: 70, color: Color(0xFF7FD47D)),
                onPressed: _authenticate,
              )
            else
              const CircularProgressIndicator(color: Color(0xFF7FD47D)),
          ],
        ),
      ),
    );
  }
}

class LogerHomePage extends StatefulWidget {
  const LogerHomePage({super.key});

  @override
  State<LogerHomePage> createState() => _LogerHomePageState();
}

class _LogerHomePageState extends State<LogerHomePage> {
  late final WebViewController controller;
  int _selectedIndex = 0;
  double progress = 0;

  @override
  void initState() {
    super.initState();
    controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setBackgroundColor(const Color(0xFFFFFFFF))
      ..setNavigationDelegate(
        NavigationDelegate(
          onProgress: (int progress) {
            setState(() {
              this.progress = progress / 100;
            });
          },
          onPageStarted: (String url) {
            setState(() {
              progress = 0;
            });
          },
          onPageFinished: (String url) {
            setState(() {
              progress = 1;
            });
          },
          onNavigationRequest: (NavigationRequest request) async {
            final url = request.url;
            if (url.startsWith('https://wa.me/') || 
                url.startsWith('whatsapp://') || 
                url.startsWith('tel:') || 
                url.startsWith('mailto:')) {
              if (await canLaunchUrl(Uri.parse(url))) {
                await launchUrl(Uri.parse(url), mode: LaunchMode.externalApplication);
                return NavigationDecision.prevent;
              }
            }
            return NavigationDecision.navigate;
          },
        ),
      )
      ..loadRequest(Uri.parse('https://logersenegal.com/'));

    _setupFilePicker();
  }

  void _setupFilePicker() {
    if (controller.platform is AndroidWebViewController) {
      (controller.platform as AndroidWebViewController).setOnShowFileSelector(
        (params) async {
          return await _showFileSelectionDialog(params);
        },
      );
    }
  }

  void _onTabTapped(int index) async {
    if (index == 2) {
      // Onglet Profil
      final loggedIn = await AuthService().isLoggedIn();
      if (!loggedIn && mounted) {
        final success = await Navigator.of(context).push(
          MaterialPageRoute(builder: (context) => const LoginScreen()),
        );
        if (success == true) {
          setState(() {
            _selectedIndex = 2;
          });
        }
        return;
      }
    }
    setState(() {
      _selectedIndex = index;
    });
  }

  final ImagePicker _picker = ImagePicker();

  Future<List<String>> _showFileSelectionDialog(FileSelectorParams params) async {
    return await showModalBottomSheet<List<String>>(
      context: context,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => Container(
        padding: const EdgeInsets.all(20),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 40,
              height: 4,
              margin: const EdgeInsets.bottom(20),
              decoration: BoxDecoration(
                color: Colors.grey[300],
                borderRadius: BorderRadius.circular(2),
              ),
            ),
            const Text(
              'Choisir un document',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 25),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildPickerOption(
                  icon: Icons.camera_alt,
                  label: 'Caméra',
                  color: const Color(0xFF0B4629),
                  onTap: () async {
                    final result = await _pickFromCamera();
                    if (context.mounted) Navigator.pop(context, result);
                  },
                ),
                _buildPickerOption(
                  icon: Icons.photo_library,
                  label: 'Galerie',
                  color: const Color(0xFF0B4629),
                  onTap: () async {
                    final result = await _pickFromGallery(params);
                    if (context.mounted) Navigator.pop(context, result);
                  },
                ),
                _buildPickerOption(
                  icon: Icons.insert_drive_file,
                  label: 'Fichiers',
                  color: const Color(0xFF0B4629),
                  onTap: () async {
                    final result = await _pickFromFiles(params);
                    if (context.mounted) Navigator.pop(context, result);
                  },
                ),
              ],
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    ) ?? [];
  }

  Widget _buildPickerOption({
    required IconData icon,
    required String label,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      child: Column(
        children: [
          Container(
            padding: const EdgeInsets.all(15),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(icon, color: color, size: 30),
          ),
          const SizedBox(height: 8),
          Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  Future<List<String>> _pickFromCamera() async {
    try {
      if (await Permission.camera.request().isGranted) {
        final XFile? photo = await _picker.pickImage(source: ImageSource.camera);
        if (photo != null) {
          return [Uri.file(photo.path).toString()];
        }
      }
    } catch (e) {
      debugPrint('Error picking from camera: $e');
    }
    return [];
  }

  Future<List<String>> _pickFromGallery(FileSelectorParams params) async {
    try {
      if (Platform.isAndroid && !await _requestStoragePermissions()) {
        return [];
      }
      
      if (params.mode == FileSelectorMode.openMultiple) {
        final List<XFile> images = await _picker.pickMultiImage();
        return images.map((image) => Uri.file(image.path).toString()).toList();
      } else {
        final XFile? image = await _picker.pickImage(source: ImageSource.gallery);
        if (image != null) {
          return [Uri.file(image.path).toString()];
        }
      }
    } catch (e) {
      debugPrint('Error picking from gallery: $e');
    }
    return [];
  }

  Future<List<String>> _pickFromFiles(FileSelectorParams params) async {
    try {
      if (Platform.isAndroid && !await _requestStoragePermissions()) {
        return [];
      }
      
      final result = await FilePicker.platform.pickFiles(
        allowMultiple: params.mode == FileSelectorMode.openMultiple,
        type: FileType.any,
      );

      if (result != null && result.files.isNotEmpty) {
        return result.files
            .where((file) => file.path != null)
            .map((file) => Uri.file(file.path!).toString())
            .toList();
      }
    } catch (e) {
      debugPrint('Error picking files: $e');
    }
    return [];
  }

  Future<bool> _requestStoragePermissions() async {
    if (Platform.isAndroid) {
      if (await Permission.photos.request().isGranted || 
          await Permission.storage.request().isGranted) {
        return true;
      }
      if (await Permission.videos.request().isGranted) {
        return true;
      }
    }
    return true;
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
                // OUVERTURE NATIVE !
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

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

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
                
                // Menu d'options
                _buildMenuItem(Icons.home_work_outlined, 'Mes Annonces', () {}),
                _buildMenuItem(Icons.favorite_outline, 'Mes Favoris', () {}),
                _buildMenuItem(Icons.security, 'Vérification NILS', () {}),
                _buildMenuItem(Icons.settings_outlined, 'Paramètres', () {}),
                
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

