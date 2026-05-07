package com.digitalh.logertogo.ui.screens.home

import android.content.Context
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.List
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.rotate
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.digitalh.logertogo.utils.CompassManager
import org.osmdroid.config.Configuration
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker

@Composable
fun MapScreen(
    viewModel: HomeViewModel,
    onBackToList: () -> Unit
) {
    val context = LocalContext.current
    val properties by viewModel.properties.collectAsState()
    val compassManager = remember { CompassManager(context) }
    val azimuth by compassManager.azimuth.collectAsState()

    // Configuration OSM
    Configuration.getInstance().load(context, context.getSharedPreferences("osm", Context.MODE_PRIVATE))

    DisposableEffect(Unit) {
        compassManager.start()
        onDispose { compassManager.stop() }
    }

    Box(modifier = Modifier.fillMaxSize()) {
        AndroidView(
            factory = { ctx ->
                MapView(ctx).apply {
                    setTileSource(TileSourceFactory.MAPNIK)
                    setMultiTouchControls(true)
                    controller.setZoom(13.0)
                    controller.setCenter(GeoPoint(6.1256, 1.2254)) // Lomé
                }
            },
            update = { mapView ->
                mapView.overlays.clear()
                properties.forEach { property ->
                    if (property.latitude != null && property.longitude != null) {
                        val marker = Marker(mapView)
                        marker.position = GeoPoint(property.latitude, property.longitude)
                        marker.title = property.title
                        marker.snippet = "${property.price.toInt()} CFA"
                        mapView.overlays.add(marker)
                    }
                }
                mapView.invalidate()
            },
            modifier = Modifier.fillMaxSize()
        )

        // Overlay Boussole Premium
        Card(
            modifier = Modifier
                .align(Alignment.BottomEnd)
                .padding(16.dp),
            shape = MaterialTheme.shapes.medium,
            colors = CardDefaults.cardColors(containerColor = Color.White.copy(alpha = 0.8f))
        ) {
            Column(
                modifier = Modifier.padding(8.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Box(modifier = Modifier.size(40.dp)) {
                    Text(
                        "▲", 
                        modifier = Modifier.align(Alignment.Center).rotate(azimuth),
                        color = Color(0xFF28A745),
                        fontWeight = androidx.compose.ui.text.font.FontWeight.Black
                    )
                }
                Text("N", style = MaterialTheme.typography.labelSmall)
            }
        }

        // Bouton retour liste
        SmallFloatingActionButton(
            onClick = onBackToList,
            modifier = Modifier
                .align(Alignment.TopStart)
                .padding(16.dp),
            containerColor = Color.White,
            contentColor = Color.Black
        ) {
            Icon(Icons.Default.List, contentDescription = "Liste")
        }
    }
}
