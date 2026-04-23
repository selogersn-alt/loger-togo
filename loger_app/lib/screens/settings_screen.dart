import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:animate_do/animate_do.dart';
import 'package:url_launcher/url_launcher.dart';
import '../services/auth_service.dart';

import 'legal_screen.dart';
import 'help_screen.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _notifyNewAnnonce = true;
  bool _autoUpdateContent = true;
  bool _useBiometrics = false;

  @override
  void initState() {
    super.initState();
    _loadSettings();
  }

  Future<void> _loadSettings() async {
    final prefs = await SharedPreferences.getInstance();
    if (mounted) {
      setState(() {
        _notifyNewAnnonce = prefs.getBool('notify_new_annonce') ?? true;
        _autoUpdateContent = prefs.getBool('auto_update_content') ?? true;
        _useBiometrics = prefs.getBool('use_biometrics') ?? false;
      });
    }
  }

  Future<void> _updateSetting(String key, bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(key, value);
    setState(() {
      if (key == 'notify_new_annonce') _notifyNewAnnonce = value;
      if (key == 'auto_update_content') _autoUpdateContent = value;
      if (key == 'use_biometrics') _useBiometrics = value;
    });
  }

  Future<void> _launchWeb(String path) async {
    final Uri url = Uri.parse('https://Logertogo.com/$path');
    await launchUrl(url, mode: LaunchMode.inAppWebView);
  }

  @override
  Widget build(BuildContext context) {
    final user = AuthService().currentUser;

    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text('Paramètres', style: TextStyle(fontWeight: FontWeight.w900)),
        centerTitle: true,
        backgroundColor: Colors.white,
        elevation: 0,
      ),
      body: ListView(
        padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
        children: [
          if (user != null) ...[
            FadeInDown(child: _buildProfile(user)),
            const SizedBox(height: 24),

          ] else ...[
             FadeInDown(child: _buildAuthPrompt()),
          ],
          
          const SizedBox(height: 32),
          _buildSectionHeader('Sécurité'),
          _buildToggle(
            'Authentification Biométrique',
            'Utiliser Fingerprint/FaceID au démarrage',
            _useBiometrics,
            Icons.fingerprint_rounded,
            (val) => _updateSetting('use_biometrics', val),
          ),
          
          const SizedBox(height: 32),
          _buildSectionHeader('Notifications & Flux'),
          _buildToggle(
            'Alertes Nouvelles Annonces',
            'Savoir quand un bien est validé',
            _notifyNewAnnonce,
            Icons.notifications_active_rounded,
            (val) => _updateSetting('notify_new_annonce', val),
          ),
          const SizedBox(height: 12),
          _buildToggle(
            'Mise à jour Automatique',
            'Actualiser le contenu toutes les 45s',
            _autoUpdateContent,
            Icons.sync_rounded,
            (val) => _updateSetting('auto_update_content', val),
          ),
          
          const SizedBox(height: 32),
          _buildSectionHeader('Espace Web Sécurisé'),
          _buildWebButton('Mon Profil Complet', 'profil/', Icons.person_outline_rounded),
          _buildWebButton('Mes Annonces Déposées', 'mes-annonces/', Icons.list_alt_rounded),


          const SizedBox(height: 32),
          _buildSectionHeader('Support & Légal'),
          Container(
            margin: const EdgeInsets.only(top: 12),
            decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20)),
            child: Column(
              children: [
                ListTile(
                  leading: const Icon(Icons.help_outline_rounded, color: Color(0xFF004D40)),
                  title: const Text('Centre d\'aide & FAQ', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                  subtitle: const Text('Comprendre le fonctionnement et la sécurité', style: TextStyle(fontSize: 11)),
                  trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 16, color: Colors.grey),
                  onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => const HelpScreen())),
                ),
                const Divider(height: 1, indent: 60),
                ListTile(
                  leading: const Icon(Icons.gavel_rounded, color: Colors.blueGrey),
                  title: const Text('Mentions Légales', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                  subtitle: const Text('Conditions d’utilisation de Loger Togo', style: TextStyle(fontSize: 11)),
                  trailing: const Icon(Icons.arrow_forward_ios_rounded, size: 16, color: Colors.grey),
                  onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => const LegalScreen())),
                ),
              ],
            ),
          ),

          const SizedBox(height: 48),
          if (user != null)
            FadeInUp(
              child: ElevatedButton(
                onPressed: () => AuthService().logout(),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.red.shade50,
                  foregroundColor: Colors.red,
                  padding: const EdgeInsets.symmetric(vertical: 20),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
                ),
                child: const Text('DÉCONNEXION', style: TextStyle(fontWeight: FontWeight.w900, letterSpacing: 1.2)),
              ),
            ),
          const SizedBox(height: 60),
        ],
      ),
    );
  }

  Widget _buildProfile(dynamic user) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(28),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.04), blurRadius: 20)],
      ),
      child: Row(
        children: [
          CircleAvatar(
            radius: 35,
            backgroundColor: const Color(0xFF004D40).withOpacity(0.1),
            child: Text(user.firstName[0], style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w900, color: Color(0xFF004D40))),
          ),
          const SizedBox(width: 20),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('${user.firstName} ${user.lastName}', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900)),
                Text(user.email, style: TextStyle(color: Colors.blueGrey.shade400, fontSize: 13)),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAuthPrompt() {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(color: const Color(0xFF1A1A1A), borderRadius: BorderRadius.circular(28)),
      child: Column(
        children: [
          const Icon(Icons.lock_rounded, color: Colors.amber, size: 40),
          const SizedBox(height: 16),
          const Text('Accès Sécurisé Requis', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
          const SizedBox(height: 8),
          const Text('Connectez-vous pour profiter de toutes les fonctionnalités.', textAlign: TextAlign.center, style: TextStyle(color: Colors.white70, fontSize: 13)),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () => _launchWeb('connexion/'),
            style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF004D40), padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 15)),
            child: const Text('CONNEXION WEB', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
          ),
        ],
      ),
    );
  }


  Widget _buildSectionHeader(String title) {
    return Text(title.toUpperCase(), style: TextStyle(fontSize: 11, fontWeight: FontWeight.w900, color: Colors.blueGrey.shade400, letterSpacing: 1.5));
  }

  Widget _buildToggle(String title, String sub, bool val, IconData icon, ValueChanged<bool> onChanged) {
    return Container(
      margin: const EdgeInsets.only(top: 12),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20)),
      child: ListTile(
        leading: Icon(icon, color: const Color(0xFF004D40)),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
        subtitle: Text(sub, style: const TextStyle(fontSize: 11)),
        trailing: Switch.adaptive(value: val, activeColor: const Color(0xFF004D40), onChanged: onChanged),
      ),
    );
  }

  Widget _buildWebButton(String title, String path, IconData icon) {
    return Container(
      margin: const EdgeInsets.only(top: 12),
      decoration: BoxDecoration(color: Colors.white, borderRadius: BorderRadius.circular(20)),
      child: ListTile(
        leading: Icon(icon, color: Colors.blueGrey),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
        trailing: const Icon(Icons.open_in_new_rounded, size: 18, color: Colors.blueGrey),
        onTap: () => _launchWeb(path),
      ),
    );
  }
}
