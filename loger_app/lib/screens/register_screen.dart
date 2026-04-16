import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class RegisterScreen extends StatelessWidget {
  const RegisterScreen({super.key});

  Future<void> _launchWebRegister() async {
    final Uri url = Uri.parse('https://logersenegal.com/register/');
    if (!await launchUrl(url, mode: LaunchMode.externalApplication)) {
      throw Exception('Could not launch $url');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Création de Compte', style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(30.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Container(
                width: 100,
                height: 100,
                decoration: BoxDecoration(
                  color: const Color(0xFF198754).withOpacity(0.1),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.person_add_outlined, size: 50, color: Color(0xFF198754)),
              ),
              const SizedBox(height: 30),
              const Text(
                'Créez votre compte en sécurité',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 15),
              const Text(
                'Pour garantir la sécurité de vos données et la validation de votre identité (NILS), la création de compte se fait désormais sur notre plateforme web certifiée.',
                textAlign: TextAlign.center,
                style: TextStyle(fontSize: 15, color: Colors.grey, height: 1.5),
              ),
              const SizedBox(height: 40),
              SizedBox(
                width: double.infinity,
                height: 55,
                child: ElevatedButton.icon(
                  onPressed: _launchWebRegister,
                  icon: const Icon(Icons.open_in_browser, color: Colors.white),
                  label: const Text('S\'INSCRIRE SUR LE WEB', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF198754),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15)),
                    elevation: 5,
                    shadowColor: const Color(0xFF198754).withOpacity(0.4),
                  ),
                ),
              ),
              const SizedBox(height: 20),
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('Retour à la page de connexion', style: TextStyle(color: Colors.grey, fontWeight: FontWeight.w600)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
