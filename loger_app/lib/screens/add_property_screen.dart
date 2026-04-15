import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';

class AddPropertyScreen extends StatefulWidget {
  const AddPropertyScreen({super.key});

  @override
  State<AddPropertyScreen> createState() => _AddPropertyScreenState();
}

class _AddPropertyScreenState extends State<AddPropertyScreen> {
  final _formKey = GlobalKey<FormState>();
  final ApiService _apiService = ApiService();
  final ImagePicker _picker = ImagePicker();
  
  final _titleController = TextEditingController();
  final _priceController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _neighborhoodController = TextEditingController();
  final _bedroomsController = TextEditingController(text: '0');
  final _bathroomsController = TextEditingController(text: '0');
  final _surfaceController = TextEditingController(text: '0');

  String _selectedCity = 'DAKAR';
  String _selectedCategory = 'RENT';
  String _selectedPropertyType = 'APARTMENT';
  List<XFile> _images = [];
  bool _isSubmitting = false;

  final Map<String, String> _cities = {
    'DAKAR': 'Dakar', 'THIES': 'Thiès', 'MBOUR': 'Mbour', 'SAINT-LOUIS': 'Saint-Louis', 'RUFISQUE': 'Rufisque'
  };

  final Map<String, String> _categories = {
    'RENT': 'À Louer', 'SALE': 'À Vendre', 'SHORT_TERM': 'Nuitée/Court séjour'
  };

  final Map<String, String> _propertyTypes = {
    'APARTMENT': 'Appartement', 'VILLA': 'Villa', 'STUDIO': 'Studio', 'CHAMBRE': 'Chambre', 'TERRAIN': 'Terrain', 'BUREAU': 'Bureau'
  };

  Future<void> _pickImages() async {
    final List<XFile> selectedImages = await _picker.pickMultiImage();
    if (selectedImages.isNotEmpty) {
      setState(() {
        _images.addAll(selectedImages);
      });
    }
  }

  void _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_images.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Veuillez ajouter au moins une image')));
      return;
    }

    setState(() => _isSubmitting = true);

    final propertyData = {
      'title': _titleController.text,
      'description': _descriptionController.text,
      'price': double.tryParse(_priceController.text) ?? 0,
      'city': _selectedCity,
      'neighborhood': _neighborhoodController.text,
      'listing_category': _selectedCategory,
      'property_type': _selectedPropertyType,
      'bedrooms': int.tryParse(_bedroomsController.text) ?? 0,
      'bathrooms': int.tryParse(_bathroomsController.text) ?? 0,
      'surface': double.tryParse(_surfaceController.text) ?? 0,
    };

    final result = await _apiService.createProperty(propertyData);

    if (result != null && result['id'] != null) {
      final String propertyId = result['id'].toString();
      
      // Upload images
      for (int i = 0; i < _images.length; i++) {
        await _apiService.uploadImage(
          propertyId, 
          File(_images[i].path), 
          isPrimary: i == 0
        );
      }

      if (mounted) {
        setState(() => _isSubmitting = false);
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Annonce publiée avec succès !')));
        Navigator.pop(context, true);
      }
    } else {
      if (mounted) {
        setState(() => _isSubmitting = false);
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Erreur lors de la publication')));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Déposer une annonce', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
        backgroundColor: const Color(0xFF0B4629),
        iconTheme: const IconThemeData(color: Colors.white),
      ),
      body: _isSubmitting 
        ? const Center(child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              CircularProgressIndicator(color: Color(0xFF0B4629)),
              SizedBox(height: 20),
              Text('Publication en cours... Veuillez patienter'),
            ],
          ))
        : SingleChildScrollView(
            padding: const EdgeInsets.all(20),
            child: Form(
              key: _formKey,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Images du bien', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 10),
                  SizedBox(
                    height: 100,
                    child: ListView(
                      scrollDirection: Axis.horizontal,
                      children: [
                        GestureDetector(
                          onTap: _pickImages,
                          child: Container(
                            width: 100,
                            decoration: BoxDecoration(color: Colors.grey[200], borderRadius: BorderRadius.circular(10)),
                            child: const Icon(Icons.add_a_photo, size: 40, color: Color(0xFF0B4629)),
                          ),
                        ),
                        ..._images.map((img) => Container(
                          width: 100,
                          margin: const EdgeInsets.only(left: 10),
                          decoration: BoxDecoration(
                            image: DecorationImage(image: FileImage(File(img.path)), fit: BoxFit.cover),
                            borderRadius: BorderRadius.circular(10),
                          ),
                        )),
                      ],
                    ),
                  ),
                  const SizedBox(height: 30),
                  
                  _buildTextField('Titre de l\'annonce', _titleController, 'Ex: Bel appartement F3 à Mermoz'),
                  _buildDropdown('Ville', _selectedCity, _cities, (val) => setState(() => _selectedCity = val!)),
                  _buildTextField('Quartier', _neighborhoodController, 'Ex: Mermoz, Sacré-Cœur...'),
                  
                  Row(
                    children: [
                      Expanded(child: _buildDropdown('Catégorie', _selectedCategory, _categories, (val) => setState(() => _selectedCategory = val!))),
                      const SizedBox(width: 15),
                      Expanded(child: _buildDropdown('Type de bien', _selectedPropertyType, _propertyTypes, (val) => setState(() => _selectedPropertyType = val!))),
                    ],
                  ),
                  
                  _buildTextField('Prix (FCFA)', _priceController, 'Ex: 250000', keyboardType: TextInputType.number),
                  
                  Row(
                    children: [
                      Expanded(child: _buildTextField('Chambres', _bedroomsController, '0', keyboardType: TextInputType.number)),
                      const SizedBox(width: 10),
                      Expanded(child: _buildTextField('SdB', _bathroomsController, '0', keyboardType: TextInputType.number)),
                      const SizedBox(width: 10),
                      Expanded(child: _buildTextField('Surface (m²)', _surfaceController, '0', keyboardType: TextInputType.number)),
                    ],
                  ),
                  
                  _buildTextField('Description complète', _descriptionController, 'Détails du bien...', maxLines: 5),
                  
                  const SizedBox(height: 40),
                  SizedBox(
                    width: double.infinity,
                    height: 55,
                    child: ElevatedButton(
                      onPressed: _submit,
                      style: ElevatedButton.styleFrom(backgroundColor: const Color(0xFF0B4629), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15))),
                      child: const Text('Publier l\'annonce', style: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                    ),
                  ),
                  const SizedBox(height: 50),
                ],
              ),
            ),
          ),
    );
  }

  Widget _buildTextField(String label, TextEditingController controller, String hint, {TextInputType keyboardType = TextInputType.text, int maxLines = 1}) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          TextFormField(
            controller: controller,
            keyboardType: keyboardType,
            maxLines: maxLines,
            decoration: InputDecoration(
              hintText: hint,
              filled: true,
              fillColor: Colors.grey[50],
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
            validator: (value) => value == null || value.isEmpty ? 'Champ requis' : null,
          ),
        ],
      ),
    );
  }

  Widget _buildDropdown(String label, String value, Map<String, String> items, Function(String?) onChanged) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            value: value,
            decoration: InputDecoration(
              filled: true,
              fillColor: Colors.grey[50],
              border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
            ),
            items: items.entries.map((e) => DropdownMenuItem(value: e.key, child: Text(e.value))).toList(),
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }
}
