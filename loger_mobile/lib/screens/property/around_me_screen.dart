import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
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
  bool _permissionDenied = false;
  Set<Marker> _markers = {};

  @override
  void initState() {
    super.initState();
    _checkPermission();
  }

  Future<void> _checkPermission() async {
    bool serviceEnabled = await Geolocator.isLocationServiceEnabled();
    if (!serviceEnabled) return;

    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        setState(() => _permissionDenied = true);
        return;
      }
    }

    _currentPosition = await Geolocator.getCurrentPosition();
    _fetchNearby();
  }

  void _fetchNearby() async {
    if (_currentPosition != null) {
      await context.read<PropertyProvider>().fetchNearbyProperties(
        _currentPosition!.latitude, 
        _currentPosition!.longitude
      );
      _createMarkers();
    }
  }

  void _createMarkers() {
    final properties = context.read<PropertyProvider>().nearbyProperties;
    setState(() {
      _markers = properties.map((p) {
        // Mock coordinates if null in model (for demo)
        double lat = _currentPosition!.latitude + (0.01 * properties.indexOf(p));
        double lng = _currentPosition!.longitude + (0.01 * properties.indexOf(p));
        
        return Marker(
          markerId: MarkerId(p.id),
          position: LatLng(lat, lng),
          infoWindow: InfoWindow(title: p.title, snippet: '${p.price} FCFA'),
          icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueGreen),
        );
      }).toSet();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Autour de moi', style: TextStyle(fontWeight: FontWeight.bold)),
        backgroundColor: Colors.white,
        foregroundColor: AppColors.primaryGreen,
        elevation: 0,
      ),
      body: _permissionDenied
          ? const Center(child: Text('Accès à la localisation refusé.'))
          : Column(
              children: [
                // Map Section
                Expanded(
                  flex: 1,
                  child: _currentPosition == null
                      ? const Center(child: CircularProgressIndicator(color: AppColors.primaryGreen))
                      : GoogleMap(
                          initialCameraPosition: CameraPosition(
                            target: LatLng(_currentPosition!.latitude, _currentPosition!.longitude),
                            zoom: 14,
                          ),
                          onMapCreated: (controller) => _mapController = controller,
                          markers: _markers,
                          myLocationEnabled: true,
                          zoomControlsEnabled: false,
                        ),
                ),
                
                // List Section
                Expanded(
                  flex: 1,
                  child: Consumer<PropertyProvider>(
                    builder: (context, provider, child) {
                      if (provider.isLoading && provider.nearbyProperties.isEmpty) {
                        return const Center(child: CircularProgressIndicator(color: AppColors.primaryGreen));
                      }

                      return ListView.builder(
                        padding: const EdgeInsets.all(20),
                        itemCount: provider.nearbyProperties.length,
                        itemBuilder: (context, index) => PropertyCard(property: provider.nearbyProperties[index]),
                      );
                    },
                  ),
                ),
              ],
            ),
    );
  }
}
