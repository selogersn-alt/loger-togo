import 'package:flutter/material.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:geolocator/geolocator.dart';
import 'package:provider/provider.dart';
import '../../core/constants/colors.dart';
import '../../providers/property_provider.dart';
import '../../widgets/property_card.dart';

class AroundMeScreen extends StatefulWidget {
  const AroundMeScreen({super.key});

  @override
  State<AroundMeScreen> createState() => _AroundMeScreenState();
}

class _AroundMeScreenState extends State<AroundMeScreen> {
  GoogleMapController? _mapController;
  Position? _currentPosition;
  Set<Marker> _markers = {};

  @override
  void initState() {
    super.initState();
    _determinePosition();
  }

  Future<void> _determinePosition() async {
    bool serviceEnabled;
    LocationPermission permission;

    serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return;

    permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) return;
    }

    final position = await Geolocator.getCurrentPosition();
    setState(() => _currentPosition = position);
    
    if (_mapController != null) {
      _mapController!.animateCamera(CameraUpdate.newLatLng(
        LatLng(position.latitude, position.longitude),
      ));
    }

    _fetchProperties(position.latitude, position.longitude);
  }

  Future<void> _fetchProperties(double lat, double lng) async {
    await context.read<PropertyProvider>().fetchNearbyProperties(lat, lng);
    _updateMarkers();
  }

  void _updateMarkers() {
    final properties = context.read<PropertyProvider>().nearbyProperties;
    setState(() {
      _markers = properties.map((p) => Marker(
        markerId: MarkerId(p.id.toString()),
        position: LatLng(p.latitude ?? 0, p.longitude ?? 0),
        infoWindow: InfoWindow(title: p.title, snippet: '${p.price.toInt()} FCFA'),
      )).toSet();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Autour de moi', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        foregroundColor: AppColors.primaryGreen,
        elevation: 0,
      ),
      body: Stack(
        children: [
          GoogleMap(
            initialCameraPosition: const CameraPosition(target: LatLng(6.1375, 1.2125), zoom: 12),
            onMapCreated: (controller) async {
              _mapController = controller;
              // Appliquer le style premium
              String style = await DefaultAssetBundle.of(context).loadString('assets/map_style.json');
              _mapController?.setMapStyle(style);
            },
            markers: _markers,
            myLocationEnabled: true,
            myLocationButtonEnabled: true,
          ),
          
          // Bottom Carousel of properties
          Positioned(
            bottom: 20,
            left: 0,
            right: 0,
            height: 180,
            child: Consumer<PropertyProvider>(
              builder: (context, provider, child) {
                if (provider.nearbyProperties.isEmpty) return const SizedBox.shrink();
                return PageView.builder(
                  controller: PageController(viewportFraction: 0.85),
                  itemCount: provider.nearbyProperties.length,
                  onPageChanged: (index) {
                    final p = provider.nearbyProperties[index];
                    _mapController?.animateCamera(CameraUpdate.newLatLng(
                      LatLng(p.latitude ?? 0, p.longitude ?? 0),
                    ));
                  },
                  itemBuilder: (context, index) {
                    final p = provider.nearbyProperties[index];
                    return Padding(
                      padding: const EdgeInsets.only(right: 15),
                      child: PropertyCard(property: p), // We might need a smaller version later
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
