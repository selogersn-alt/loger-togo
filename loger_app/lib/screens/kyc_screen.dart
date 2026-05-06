import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:animate_do/animate_do.dart';

class KycScreen extends StatefulWidget {
  const KycScreen({super.key});

  @override
  State<KycScreen> createState() => _KycScreenState();
}

class _KycScreenState extends State<KycScreen> {
  final _storage = const FlutterSecureStorage();
  final _picker = ImagePicker();
  
  File? _cniFront;
  File? _cniBack;
  File? _selfie;
  bool _isUploading = false;

  Future<void> _pickImage(String type) async {
    final XFile? image = await _picker.pickImage(
      source: type == 'selfie' ? ImageSource.camera : ImageSource.gallery,
      imageQuality: 70,
    );

    if (image != null) {
      setState(() {
        if (type == 'front') _cniFront = File(image.path);
        if (type == 'back') _cniBack = File(image.path);
        if (type == 'selfie') _selfie = File(image.path);
      });
    }
  }

  Future<void> _submitKyc() async {
    if (_cniFront == null || _cniBack == null || _selfie == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Veuillez fournir tous les documents demandés.')),
      );
      return;
    }

    setState(() => _isUploading = true);

    try {
      final token = await _storage.read(key: 'access_token');
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('https://Logertogo.com/api/users/kyc/'),
      );

      request.headers['Authorization'] = 'Bearer $token';
      
      request.files.add(await http.MultipartFile.fromPath('cni_front_image', _cniFront!.path));
      request.files.add(await http.MultipartFile.fromPath('cni_back_image', _cniBack!.path));
      request.files.add(await http.MultipartFile.fromPath('selfie_image', _selfie!.path));

      final response = await request.send();

      if (response.statusCode == 201) {
        if (mounted) {
          showDialog(
            context: context,
            barrierDismissible: false,
            builder: (context) => AlertDialog(
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
              title: const Text('Succès'),
              content: const Text('Vos documents ont été envoyés avec succès. Notre équipe va les vérifier sous 24h.'),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.pop(context); // close dialog
                    Navigator.pop(context); // return to settings
                  },
                  child: const Text('OK'),
                ),
              ],
            ),
          );
        }
      } else {
        throw Exception('Échec de l\'envoi (${response.statusCode})');
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erreur: $e')),
        );
      }
    } finally {
      if (mounted) setState(() => _isUploading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Vérification d\'identité', style: TextStyle(fontWeight: FontWeight.bold)),
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
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: const Color(0xFF27C66E).withValues(alpha: 0.1),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.verified_user_rounded, color: Color(0xFF27C66E), size: 40),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: const [
                          Text(
                            'Gagnez en confiance',
                            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                          ),
                          Text(
                            'Les profils vérifiés reçoivent 3x plus de demandes.',
                            style: TextStyle(fontSize: 13, color: Colors.black54),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 32),
            const Text(
              'Documents requis',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildUploadBox(
              title: 'Recto de la pièce d\'identité',
              subtitle: 'CNI, Passport ou Carte Électeur',
              file: _cniFront,
              onTap: () => _pickImage('front'),
              delay: 100,
            ),
            const SizedBox(height: 16),
            _buildUploadBox(
              title: 'Verso de la pièce d\'identité',
              subtitle: 'La face arrière de votre document',
              file: _cniBack,
              onTap: () => _pickImage('back'),
              delay: 200,
            ),
            const SizedBox(height: 16),
            _buildUploadBox(
              title: 'Selfie de vérification',
              subtitle: 'Prenez une photo de votre visage',
              file: _selfie,
              onTap: () => _pickImage('selfie'),
              isCamera: true,
              delay: 300,
            ),
            const SizedBox(height: 40),
            FadeInUp(
              delay: const Duration(milliseconds: 400),
              child: SizedBox(
                width: double.infinity,
                height: 60,
                child: ElevatedButton(
                  onPressed: _isUploading ? null : _submitKyc,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: const Color(0xFF27C66E),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    elevation: 4,
                  ),
                  child: _isUploading
                      ? const CircularProgressIndicator(color: Colors.white)
                      : const Text(
                          'Soumettre pour vérification',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                ),
              ),
            ),
            const SizedBox(height: 20),
            const Center(
              child: Text(
                'Vos données sont cryptées et sécurisées.',
                style: TextStyle(color: Colors.grey, fontSize: 12),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildUploadBox({
    required String title,
    required String subtitle,
    File? file,
    required VoidCallback onTap,
    bool isCamera = false,
    int delay = 0,
  }) {
    return FadeInLeft(
      delay: Duration(milliseconds: delay),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Container(
          width: double.infinity,
          height: 120,
          decoration: BoxDecoration(
            border: Border.all(color: Colors.grey.withValues(alpha: 0.3), width: 2),
            borderRadius: BorderRadius.circular(16),
            image: file != null
                ? DecorationImage(image: FileImage(file), fit: BoxFit.cover, opacity: 0.5)
                : null,
          ),
          child: file != null
              ? const Center(child: Icon(Icons.check_circle, color: Color(0xFF27C66E), size: 48))
              : Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(isCamera ? Icons.camera_alt_rounded : Icons.add_photo_alternate_rounded, color: Colors.grey),
                    const SizedBox(height: 8),
                    Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
                    Text(subtitle, style: const TextStyle(fontSize: 12, color: Colors.grey)),
                  ],
                ),
        ),
      ),
    );
  }
}
