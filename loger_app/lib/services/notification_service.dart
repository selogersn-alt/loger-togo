import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

class NotificationService {
  static final FirebaseMessaging _firebaseMessaging = FirebaseMessaging.instance;
  static final FlutterLocalNotificationsPlugin _localNotificationsPlugin = FlutterLocalNotificationsPlugin();

  static Future<void> initialize() async {
    // Demander la permission (iOS)
    NotificationSettings settings = await _firebaseMessaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      print('User granted permission');
    }

    // Configuration pour les notifications locales (Foreground)
    const AndroidInitializationSettings initializationSettingsAndroid = AndroidInitializationSettings('@mipmap/ic_launcher');
    const InitializationSettings initializationSettings = InitializationSettings(android: initializationSettingsAndroid);
    await _localNotificationsPlugin.initialize(settings: initializationSettings);

    // Gérer les messages en arrière-plan
    FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

    // Gérer les messages quand l'app est ouverte (Foreground)
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      _showLocalNotification(message);
    });
  }

  static Future<void> _showLocalNotification(RemoteMessage message) async {
    const AndroidNotificationDetails androidDetail = AndroidNotificationDetails(
      'high_importance_channel', // channelId
      'High Importance Notifications', // channelName
      importance: Importance.max,
      priority: Priority.high,
    );
    const NotificationDetails noticeDetail = NotificationDetails(android: androidDetail);
    
    await _localNotificationsPlugin.show(
      id: 0,
      title: message.notification?.title,
      body: message.notification?.body,
      notificationDetails: noticeDetail,
    );
  }

  static Future<String?> getToken() async {
    return await _firebaseMessaging.getToken();
  }
}

// Handler global pour l'arrière-plan
Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  print("Handling a background message: ${message.messageId}");
}
