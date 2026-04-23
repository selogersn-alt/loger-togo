import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:animate_do/animate_do.dart';
import 'register_screen.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  Future<void> _launchWebLogin() async {
    final Uri url = Uri.parse('https://Logertogo.com/connexion/');
    if (!await launchUrl(url, mode: LaunchMode.externalApplication)) {
      throw Exception('Could not launch $url');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      body: Stack(
        children: [
          // Background Aesthetic Circle
          Positioned(
            top: -100,
            right: -100,
            child: Container(
              width: 300,
              height: 300,
              decoration: BoxDecoration(
                color: const Color(0xFF004D40).withOpacity(0.05),
                shape: BoxShape.circle,
              ),
            ),
          ),
          SafeArea(
            child: SingleChildScrollView(
              padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 40),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  FadeInLeft(
                    child: GestureDetector(
                      onTap: () => Navigator.pop(context),
                      child: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 10)],
                        ),
                        child: const Icon(Icons.arrow_back_ios_new_rounded, size: 20, color: Colors.black),
                      ),
                    ),
                  ),
                  const SizedBox(height: 60),
                  FadeInDown(
                    delay: const Duration(milliseconds: 200),
                    child: Center(
                      child: Container(
                        padding: const EdgeInsets.all(24),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 20)],
                        ),
                        child: Image.asset('assets/img/logo.png', width: 100),
                      ),
                    ),
                  ),
                  const SizedBox(height: 48),
                  FadeInUp(
                    delay: const Duration(milliseconds: 400),
                    child: const Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Connexion Sécurisée',
                          style: TextStyle(
                            fontSize: 32,
                            fontWeight: FontWeight.w900,
                            color: Color(0xFF004D40),
                            letterSpacing: -1,
                          ),
                        ),
                        SizedBox(height: 12),
                        Text(
                          'Pour garantir votre sécurité et l’authenticité des annonces, connectez-vous sur notre plateforme web certifiée.',
                          style: TextStyle(
                            fontSize: 16,
                            color: Colors.blueGrey,
                            height: 1.6,
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 50),
                  FadeInUp(
                    delay: const Duration(milliseconds: 600),
                    child: Container(
                      width: double.infinity,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF004D40), Color(0xFF1A237E)],
                          begin: Alignment.centerLeft,
                          end: Alignment.centerRight,
                        ),
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: const Color(0xFF004D40).withOpacity(0.3),
                            blurRadius: 20,
                            offset: const Offset(0, 10),
                          ),
                        ],
                      ),
                      child: ElevatedButton(
                        onPressed: _launchWebLogin,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.transparent,
                          shadowColor: Colors.transparent,
                          padding: const EdgeInsets.symmetric(vertical: 20),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                        ),
                        child: const Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.lock_open_rounded, color: Colors.white),
                            SizedBox(width: 12),
                            Text(
                              'ALLER SUR LE WEB',
                              style: TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 16),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 32),
                  FadeInUp(
                    delay: const Duration(milliseconds: 800),
                    child: Center(
                      child: Column(
                        children: [
                          TextButton(
                            onPressed: () {
                              Navigator.of(context).push(
                                MaterialPageRoute(builder: (context) => const RegisterScreen()),
                              );
                            },
                            child: RichText(
                              text: const TextSpan(
                                text: "Pas de compte ? ",
                                style: TextStyle(color: Colors.blueGrey, fontSize: 14),
                                children: [
                                  TextSpan(
                                    text: "S'inscrire ici",
                                    style: TextStyle(color: Color(0xFF004D40), fontWeight: FontWeight.w800),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          const SizedBox(height: 12),
                          TextButton(
                            onPressed: () => Navigator.pop(context),
                            child: Text(
                              "Continuer en mode découverte",
                              style: TextStyle(color: Colors.blueGrey.shade300, fontSize: 13, decoration: TextDecoration.underline),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
