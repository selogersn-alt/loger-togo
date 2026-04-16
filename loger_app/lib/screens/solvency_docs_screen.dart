import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';

class SolvencyDocsScreen extends StatefulWidget {
  const SolvencyDocsScreen({super.key});

  @override
  State<SolvencyDocsScreen> createState() => _SolvencyDocsScreenState();
}

class _SolvencyDocsScreenState extends State<SolvencyDocsScreen> {
  final ApiService _apiService = ApiService();
  final ImagePicker _picker = ImagePicker();
  late Future<List<dynamic>> _docsFuture;
  String _selectedDocType = 'PAYSLIP';

  final Map<String, String> _docTypes = {
    'PAYSLIP': 'Bulletin de Salaire',
    'CONTRACT': 'Contrat de Travail',
    'BANK_STATEMENT': 'Relevé Bancaire',
    'NINEA': 'NINEA',
    'ADMIN_DOC': 'Document Administratif',
  };

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  void _refresh() {
    setState(() {
      _docsFuture = _apiService.fetchSolvencyDocuments();
    });
  }

  Future<void> _pickAndUpload() async {
    try {
      final XFile? image = await _picker.pickImage(source: ImageSource.gallery);

      if (image != null) {
        File file = File(image.path);
        if (!mounted) return;

        final success = await _apiService.uploadSolvencyDocument(
          _selectedDocType,
          file,
        );

        if (mounted) {
          if (success) {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Document envoyé avec succès !'),
                backgroundColor: Colors.green,
              ),
            );
            _refresh();
          } else {
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(
                content: Text('Erreur lors de l\'envoi.'),
                backgroundColor: Colors.red,
              ),
            );
          }
        }
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Erreur: $e'), backgroundColor: Colors.red),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF8FAFC),
      appBar: AppBar(
        title: const Text(
          'Mes Documents de Solvabilité',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Colors.white,
        foregroundColor: Colors.black,
        elevation: 0,
      ),
      body: Column(
        children: [
          _buildUploadSection(),
          const Padding(
            padding: EdgeInsets.symmetric(horizontal: 20, vertical: 10),
            child: Align(
              alignment: Alignment.centerLeft,
              child: Text(
                'HISTORIQUE',
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  color: Colors.grey,
                  fontSize: 12,
                ),
              ),
            ),
          ),
          Expanded(
            child: FutureBuilder<List<dynamic>>(
              future: _docsFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                }
                final docs = snapshot.data ?? [];
                if (docs.isEmpty) {
                  return const Center(
                    child: Padding(
                      padding: EdgeInsets.all(40.0),
                      child: Text(
                        'Aucun document soumis. Prenez une photo de votre bulletin ou contrat.',
                        textAlign: TextAlign.center,
                      ),
                    ),
                  );
                }
                return ListView.builder(
                  itemCount: docs.length,
                  itemBuilder: (context, index) {
                    final doc = docs[index];
                    return _buildDocItem(doc);
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildUploadSection() {
    return Container(
      margin: const EdgeInsets.all(20),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10),
        ],
      ),
      child: Column(
        children: [
          DropdownButtonFormField<String>(
            initialValue: _selectedDocType,
            decoration: const InputDecoration(labelText: 'Type de document'),
            items: _docTypes.entries
                .map(
                  (e) => DropdownMenuItem(value: e.key, child: Text(e.value)),
                )
                .toList(),
            onChanged: (val) => setState(() => _selectedDocType = val!),
          ),
          const SizedBox(height: 20),
          ElevatedButton.icon(
            onPressed: _pickAndUpload,
            icon: const Icon(Icons.camera_alt_rounded),
            label: const Text('AJOUTER UNE PHOTO DU DOCUMENT'),
            style: ElevatedButton.styleFrom(
              backgroundColor: const Color(0xFF198754),
              foregroundColor: Colors.white,
              minimumSize: const Size(double.infinity, 50),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDocItem(Map<String, dynamic> doc) {
    final status = doc['status'];
    Color statusColor = Colors.orange;
    if (status == 'VERIFIED') statusColor = Colors.green;
    if (status == 'REJECTED') statusColor = Colors.red;

    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 20, vertical: 5),
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.grey.withOpacity(0.1)),
      ),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: const Color(0xFF198754).withOpacity(0.1),
          child: const Icon(
            Icons.description_rounded,
            color: Color(0xFF198754),
          ),
        ),
        title: Text(
          doc['doc_type_display'] ?? 'Document',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(
          'Soumis le ${doc['uploaded_at'].toString().substring(0, 10)}',
          style: const TextStyle(fontSize: 12),
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
          decoration: BoxDecoration(
            color: statusColor.withOpacity(0.1),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            doc['status_display'] ?? 'En attente',
            style: TextStyle(
              color: statusColor,
              fontWeight: FontWeight.bold,
              fontSize: 10,
            ),
          ),
        ),
      ),
    );
  }
}
