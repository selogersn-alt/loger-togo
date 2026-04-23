import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:animate_do/animate_do.dart';

class RegisterScreen extends StatelessWidget {
  const RegisterScreen({super.key});

  Future<void> _launchWebRegister() async {
    final Uri url = Uri.parse('https://Logertogo.com/inscription/');
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
          Positioned(
            top: -50,
            left: -50,
            child: Container(
              width: 250,
              height: 250,
              decoration: BoxDecoration(
                color: const Color(0xFF004D40).withOpacity(0.04),
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
                    child: IconButton(
                      icon: Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(16),
                          boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 10)],
                        ),
                        child: const Icon(Icons.arrow_back_ios_new_rounded, size: 18, color: Colors.black),
                      ),
                      onPressed: () => Navigator.pop(context),
                    ),
                  ),
                  const SizedBox(height: 60),
                  FadeInRight(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text(
                          'Création de Compte Certifié',
                          style: TextStyle(
                            fontSize: 32,
                            fontWeight: FontWeight.w900,
                            color: Color(0xFF004D40),
                            height: 1.1,
                          ),
                        ),
                        const SizedBox(height: 24),
                        Container(
                          padding: const EdgeInsets.all(24),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(28),
                            boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.03), blurRadius: 20)],
                          ),
                          child: Column(
                            children: [
                              Container(
                                padding: const EdgeInsets.all(20),
                                decoration: BoxDecoration(
                                  color: const Color(0xFF004D40).withOpacity(0.05),
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(Icons.workspace_premium_rounded, size: 50, color: Color(0xFF004D40)),
                              ),
                              const SizedBox(height: 24),
                              const Text(
                                'Pourquoi s’inscrire sur le Web ?',
                                style: TextStyle(fontWeight: FontWeight.w800, fontSize: 18),
                              ),
                              const SizedBox(height: 12),
                              Text(
                                'Pour garantir votre sécurité et une expérience optimale, la création de compte et la gestion de profil se font sur notre plateforme web sécurisée.',
                                textAlign: TextAlign.center,
                                style: TextStyle(color: Colors.blueGrey.shade400, fontSize: 14, height: 1.6),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 48),
                  FadeInUp(
                    child: Container(
                      width: double.infinity,
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          colors: [Color(0xFF004D40), Color(0xFF1A1A1A)],
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
                        onPressed: _launchWebRegister,
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.transparent,
                          shadowColor: Colors.transparent,
                          padding: const EdgeInsets.symmetric(vertical: 20),
                        ),
                        child: const Text(
                          'S\'INSCRIRE MAINTENANT',
                          style: TextStyle(color: Colors.white, fontWeight: FontWeight.w900, fontSize: 16),
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 24),
                  Center(
                    child: TextButton(
                      onPressed: () => Navigator.pop(context),
                      child: const Text(
                        'J’ai déjà un compte Loger',
                        style: TextStyle(color: Color(0xFF004D40), fontWeight: FontWeight.w800),
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
