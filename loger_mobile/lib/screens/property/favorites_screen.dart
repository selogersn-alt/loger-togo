import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../providers/property_provider.dart';
import '../../widgets/property_card.dart';

class FavoritesScreen extends StatelessWidget {
  const FavoritesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final favorites = context.watch<PropertyProvider>().recentProperties.take(2).toList(); // Demo

    return Scaffold(
      appBar: AppBar(title: const Text('Mes Favoris', style: TextStyle(fontWeight: FontWeight.bold))),
      body: favorites.isEmpty
        ? const Center(child: Text('Aucun favori pour le moment.'))
        : GridView.builder(
            padding: const EdgeInsets.all(20),
            gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
              crossAxisCount: 2,
              mainAxisSpacing: 15,
              crossAxisSpacing: 15,
              childAspectRatio: 0.78,
            ),
            itemCount: favorites.length,
            itemBuilder: (context, index) => PropertyCard(property: favorites[index]),
          ),
    );
  }
}
