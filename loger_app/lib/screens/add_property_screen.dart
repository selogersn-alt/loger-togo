import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import '../services/api_service.dart';
import '../services/auth_service.dart';

class AddPropertyScreen extends StatefulWidget {
  const AddPropertyScreen({super.key});

  @override
  State<AddPropertyScreen> createState() => _AddPropertyScreenState();
}

class _AddPropertyScreenState extends State<AddPropertyScreen> {
  final ApiService _apiService = ApiService();
  final _formKey = GlobalKey<FormState>();
  int _currentStep = 0;

  // Form Data
  String _listingCategory = 'A_LOUER';
  String _propertyType = 'APPARTEMENT';
  final _titleController = TextEditingController();
  final _priceController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _cityController = TextEditingController();
  final _neighborhoodController = TextEditingController();
  
  int _bedrooms = 1;
  int _toilets = 1;
  final double _surface = 0;

  final List<File> _selectedImages = [];
  bool _isSubmitting = false;

  final ImagePicker _picker = ImagePicker();

  Future<void> _pickImages() async {
    final List<XFile> images = await _picker.pickMultiImage();
    if (images.isNotEmpty) {
      setState(() {
        _selectedImages.addAll(images.map((x) => File(x.path)));
      });
    }
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_selectedImages.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Veuillez ajouter au moins une photo.')),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    try {
      final propertyData = {
        'title': _titleController.text,
        'listing_category': _listingCategory,
        'property_type': _propertyType,
        'price': double.parse(_priceController.text),
        'description': _descriptionController.text,
        'city': _cityController.text,
        'neighborhood': _neighborhoodController.text,
        'bedrooms': _bedrooms,
        'toilets': _toilets,
        'surface': _surface,
      };

      final result = await _apiService.createProperty(propertyData);
      if (result != null) {
        final propertyId = result['id'].toString();
        
        // Upload images one by one
        for (int i = 0; i < _selectedImages.length; i++) {
          await _apiService.uploadImage(
            propertyId, 
            _selectedImages[i], 
            isPrimary: i == 0
          );
        }

        if (context.mounted) {
          showDialog(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text('Succès'),
              content: const Text('Votre annonce a été soumise avec succès et est en attente de validation.'),
              actions: [
                TextButton(
                  onPressed: () {
                    Navigator.pop(context); // dialog
                    Navigator.pop(context); // screen
                  },
                  child: const Text('Génial'),
                ),
              ],
            ),
          );
        }
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Erreur: $e')),
      );
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final user = AuthService().currentUser;

    if (user == null) {
      return _buildAuthRequired();
    }

    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Nouvelle Annonce', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        elevation: 0,
        foregroundColor: Colors.black,
      ),
      body: _isSubmitting 
        ? const Center(child: CircularProgressIndicator(color: Color(0xFF004D40)))
        : Form(
            key: _formKey,
            child: Theme(
              data: Theme.of(context).copyWith(
                colorScheme: const ColorScheme.light(primary: Color(0xFF004D40)),
              ),
              child: Stepper(
                type: StepperType.horizontal,
                currentStep: _currentStep,
                onStepContinue: () {
                  if (_currentStep < 3) {
                    setState(() => _currentStep += 1);
                  } else {
                    _submit();
                  }
                },
                onStepCancel: () {
                  if (_currentStep > 0) {
                    setState(() => _currentStep -= 1);
                  }
                },
                steps: [
                  _buildStepCategory(),
                  _buildStepDetails(),
                  _buildStepLocation(),
                  _buildStepPhotos(),
                ],
              ),
            ),
          ),
    );
  }

  Step _buildStepCategory() {
    return Step(
      title: const Text('Type'),
      isActive: _currentStep >= 0,
      content: Column(
        children: [
          _buildSelectionTitle('Catégorie d\'annonce'),
          Row(
            children: [
              _buildChoiceChip('A_LOUER', 'À Louer', _listingCategory, (v) => setState(() => _listingCategory = v)),
              const SizedBox(width: 10),
              _buildChoiceChip('A_VENDRE', 'À Vendre', _listingCategory, (v) => setState(() => _listingCategory = v)),
            ],
          ),
          const SizedBox(height: 24),
          _buildSelectionTitle('Type de bien'),
          Wrap(
            spacing: 8,
            children: [
              _buildChoiceChip('APPARTEMENT', 'Appartement', _propertyType, (v) => setState(() => _propertyType = v)),
              _buildChoiceChip('VILLA', 'Villa', _propertyType, (v) => setState(() => _propertyType = v)),
              _buildChoiceChip('TERRAIN', 'Terrain', _propertyType, (v) => setState(() => _propertyType = v)),
              _buildChoiceChip('STUDIO', 'Studio', _propertyType, (v) => setState(() => _propertyType = v)),
              _buildChoiceChip('CHAMBRE', 'Chambre', _propertyType, (v) => setState(() => _propertyType = v)),
            ],
          ),
        ],
      ),
    );
  }

  Step _buildStepDetails() {
    return Step(
      title: const Text('Détails'),
      isActive: _currentStep >= 1,
      content: Column(
        children: [
          _buildTextField(_titleController, 'Titre de l\'annonce', 'Ex: Villa moderne à Baguida'),
          const SizedBox(height: 16),
          _buildTextField(_priceController, 'Prix (F CFA)', 'Ex: 150000', isNumber: true),
          const SizedBox(height: 16),
          _buildTextField(_descriptionController, 'Description', 'Détails supplémentaires...', maxLines: 3),
          const SizedBox(height: 24),
          Row(
            children: [
              Expanded(child: _buildCounter('Chambres', _bedrooms, (v) => setState(() => _bedrooms = v))),
              const SizedBox(width: 16),
              Expanded(child: _buildCounter('SdB / WC', _toilets, (v) => setState(() => _toilets = v))),
            ],
          ),
        ],
      ),
    );
  }

  Step _buildStepLocation() {
    return Step(
      title: const Text('Lieu'),
      isActive: _currentStep >= 2,
      content: Column(
        children: [
          _buildTextField(_cityController, 'Ville', 'Ex: Lomé'),
          const SizedBox(height: 16),
          _buildTextField(_neighborhoodController, 'Quartier', 'Ex: Hedzranawoé'),
        ],
      ),
    );
  }

  Step _buildStepPhotos() {
    return Step(
      title: const Text('Photos'),
      isActive: _currentStep >= 3,
      content: Column(
        children: [
          const Text('Ajoutez les plus belles photos de votre bien.', style: TextStyle(color: Colors.grey)),
          const SizedBox(height: 20),
          if (_selectedImages.isNotEmpty)
            SizedBox(
              height: 100,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: _selectedImages.length,
                itemBuilder: (context, index) => Container(
                  margin: const EdgeInsets.only(right: 10),
                  width: 100,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(12),
                    image: DecorationImage(image: FileImage(_selectedImages[index]), fit: BoxFit.cover),
                  ),
                ),
              ),
            ),
          const SizedBox(height: 20),
          OutlinedButton.icon(
            onPressed: _pickImages,
            icon: const Icon(Icons.add_a_photo_rounded),
            label: const Text('Ajouter des photos'),
            style: OutlinedButton.styleFrom(
              minimumSize: const Size(double.infinity, 50),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTextField(TextEditingController controller, String label, String hint, {bool isNumber = false, int maxLines = 1}) {
    return TextFormField(
      controller: controller,
      keyboardType: isNumber ? TextInputType.number : TextInputType.text,
      maxLines: maxLines,
      decoration: InputDecoration(
        labelText: label,
        hintText: hint,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
        filled: true,
        fillColor: Colors.grey.shade50,
      ),
      validator: (v) => v!.isEmpty ? 'Ce champ est requis' : null,
    );
  }

  Widget _buildChoiceChip(String value, String label, String groupValue, Function(String) onSelected) {
    bool selected = value == groupValue;
    return ChoiceChip(
      label: Text(label),
      selected: selected,
      onSelected: (_) => onSelected(value),
      selectedColor: const Color(0xFF004D40),
      labelStyle: TextStyle(color: selected ? Colors.white : Colors.black, fontWeight: FontWeight.bold),
    );
  }

  Widget _buildCounter(String label, int value, Function(int) onChanged) {
    return Column(
      children: [
        Text(label, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
        Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            IconButton(onPressed: value > 0 ? () => onChanged(value - 1) : null, icon: const Icon(Icons.remove_circle_outline)),
            Text('$value', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            IconButton(onPressed: () => onChanged(value + 1), icon: const Icon(Icons.add_circle_outline)),
          ],
        ),
      ],
    );
  }

  Widget _buildSelectionTitle(String title) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8.0),
      child: Align(
        alignment: Alignment.centerLeft,
        child: Text(title, style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
      ),
    );
  }

  Widget _buildAuthRequired() {
    return Scaffold(
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.lock_person_rounded, size: 80, color: Color(0xFF004D40)),
              const SizedBox(height: 24),
              const Text('Connexion requise', style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
              const SizedBox(height: 12),
              const Text(
                'Vous devez être connecté pour publier une annonce immobilière sur Loger Togo.',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey),
              ),
              const SizedBox(height: 32),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF004D40),
                  minimumSize: const Size(200, 50),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                ),
                child: const Text('Se connecter', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
