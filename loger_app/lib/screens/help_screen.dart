import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import 'package:animate_do/animate_do.dart';

class HelpScreen extends StatelessWidget {
  const HelpScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Centre d\'aide & FAQ', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        elevation: 0,
        foregroundColor: Colors.black,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            FadeInDown(
              child: const Text(
                'Comment ça marche ?',
                style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900, color: Color(0xFF004D40)),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Bienvenue sur Loger Togo. Pour vous offrir une expérience sécurisée, voici quelques informations importantes.',
              style: TextStyle(fontSize: 16, color: Colors.blueGrey, height: 1.5),
            ),
            const SizedBox(height: 32),
            
            _buildFAQItem(
              'Pourquoi dois-je me connecter sur le Web ?',
              'La gestion complète de votre compte et le dépôt d\'annonces se font via notre plateforme Web optimisée pour garantir la sécurité des transactions et la qualité des annonces.',
            ),
            _buildFAQItem(
              'Comment déposer une annonce ?',
              'Cliquez sur le bouton "Déposer" sur la page d\'accueil. Vous serez redirigé vers notre formulaire web sécurisé.',
            ),

            _buildFAQItem(
              'Besoin d\'assistance direct ?',
              'Nos équipes sont disponibles pour vous accompagner dans vos recherches.',
            ),
            
            const SizedBox(height: 40),
            Center(
              child: ElevatedButton.icon(
                onPressed: () => launchUrl(
                  Uri.parse('https://Logertogo.com/contact/'),
                  mode: LaunchMode.inAppWebView,
                ),
                icon: const Icon(Icons.support_agent_rounded, color: Colors.white),
                label: const Text('CONTACTER LE SUPPORT', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF004D40),
                  padding: const EdgeInsets.symmetric(horizontal: 32, vertical: 16),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                ),
              ),
            ),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildFAQItem(String question, String answer) {
    return Container(
      margin: const EdgeInsets.only(bottom: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            question,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.black87),
          ),
          const SizedBox(height: 8),
          Text(
            answer,
            style: const TextStyle(fontSize: 15, color: Colors.blueGrey, height: 1.4),
          ),
          const SizedBox(height: 16),
          const Divider(),
        ],
      ),
    );
  }
}
