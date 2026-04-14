import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';
import 'package:local_auth/local_auth.dart';
import 'package:flutter/services.dart';

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
          onWebResourceError: (WebResourceError error) {
            debugPrint('WebResourceError: ${error.description}');
          },
        ),
      )
      ..loadRequest(Uri.parse('https://logersenegal.com/'));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Column(
          children: [
            if (progress < 1)
              LinearProgressIndicator(
                value: progress,
                backgroundColor: Colors.white,
                color: const Color(0xFF7FD47D),
                minHeight: 2,
              ),
            Expanded(
              child: PopScope(
                canPop: false,
                onPopInvokedWithResult: (didPop, result) async {
                  if (await controller.canGoBack()) {
                    controller.goBack();
                  }
                },
                child: WebViewWidget(controller: controller),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: BottomAppBar(
        height: 60,
        color: const Color(0xFF0B4629),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceAround,
          children: [
            IconButton(
              icon: const Icon(Icons.arrow_back_ios, color: Colors.white, size: 20),
              onPressed: () async {
                if (await controller.canGoBack()) {
                  controller.goBack();
                }
              },
            ),
            IconButton(
              icon: const Icon(Icons.home, color: Color(0xFF7FD47D), size: 28),
              onPressed: () => controller.loadRequest(Uri.parse('https://logersenegal.com/')),
            ),
            IconButton(
              icon: const Icon(Icons.refresh, color: Colors.white, size: 24),
              onPressed: () => controller.reload(),
            ),
            IconButton(
              icon: const Icon(Icons.arrow_forward_ios, color: Colors.white, size: 20),
              onPressed: () async {
                if (await controller.canGoForward()) {
                  controller.goForward();
                }
              },
            ),
          ],
        ),
      ),
    );
  }
}
