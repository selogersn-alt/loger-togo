import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/constants/colors.dart';
import '../../providers/auth_provider.dart';
import '../auth/login_screen.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    
    if (!auth.isAuthenticated) {
      return const LoginScreen();
    }

    final user = auth.user;

    return Scaffold(
      appBar: AppBar(
        title: const Text('Mon Profil', style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
        actions: [
          IconButton(
            icon: const Icon(Icons.logout, color: Colors.red),
            onPressed: () => auth.logout(),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            // Header
            Center(
              child: Column(
                children: [
                  CircleAvatar(
                    radius: 50,
                    backgroundColor: AppColors.primaryGreen,
                    backgroundImage: user?.profileImage != null ? NetworkImage(user!.profileImage!) : null,
                    child: user?.profileImage == null ? const Icon(Icons.person, size: 50, color: Colors.white) : null,
                  ),
                  const SizedBox(height: 15),
                  Text(
                    '${user?.firstName ?? ''} ${user?.lastName ?? ''}',
                    style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  Text(user?.email ?? '', style: const TextStyle(color: AppColors.textGrey)),
                ],
              ),
            ),
            const SizedBox(height: 40),
            
            // Menu Items (Similaire au Dashboard du site)
            _buildMenuItem(Icons.home_work_outlined, 'Mes annonces', () {}),
            _buildMenuItem(Icons.favorite_border, 'Mes favoris', () {}),
            _buildMenuItem(Icons.chat_outlined, 'Messages', () {}),
            _buildMenuItem(Icons.notifications_none, 'Notifications', () {}),
            const Divider(height: 40),
            _buildMenuItem(Icons.settings_outlined, 'Paramètres', () {}),
            _buildMenuItem(Icons.help_outline, 'Aide & FAQ', () {}),
          ],
        ),
      ),
    );
  }

  Widget _buildMenuItem(IconData icon, String title, VoidCallback onTap) {
    return ListTile(
      leading: Icon(icon, color: AppColors.primaryGreen),
      title: Text(title, style: const TextStyle(fontWeight: FontWeight.w500)),
      trailing: const Icon(Icons.chevron_right, size: 20),
      onTap: onTap,
    );
  }
}
