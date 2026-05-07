# Loger Togo Android — Application Mobile Native Kotlin

Application Android native **Loger Togo** développée en Kotlin pur.

## Architecture
```
MVVM (Model-View-ViewModel)
├── data/
│   ├── api/         → Retrofit2 + OkHttp (appels REST vers Django)
│   └── model/       → Data classes Kotlin (mappant les APIs)
└── ui/
    ├── auth/        → Login + Register (JWT)
    ├── home/        → Accueil + Carousel Boostés + Recherche
    ├── property/    → Liste + Détail + Formulaire annonce
    └── chat/        → Messagerie temps réel (polling 3s)
```

## Stack Technique
| Composant | Technologie |
|-----------|-------------|
| Langage | Kotlin 100% |
| UI | Android Views + ViewBinding |
| Architecture | MVVM + LiveData |
| Réseau | Retrofit2 + OkHttp |
| Auth | JWT via Django SimpleJWT |
| Images | Glide (depuis Cloudflare R2) |
| Stockage local | DataStore Preferences |
| Navigation | Navigation Component |
| Carousel | ViewPager2 |
| Async | Coroutines + Flow |

## API Django connectées
- `POST /api/v1/auth/token/` — Connexion JWT
- `GET /api/v1/auth/me/` — Profil utilisateur
- `GET /api/v1/properties/` — Liste annonces paginée
- `GET /api/v1/properties/boosted/` — Annonces boostées (carousel)
- `GET /api/v1/properties/{id}/` — Détail annonce
- `GET /api/v1/chat/conversations/` — Liste discussions
- `GET /api/v1/chat/conversations/{id}/messages/` — Messages
- `POST /api/v1/chat/conversations/{id}/messages/` — Envoyer message + photo
- `PATCH /api/v1/chat/conversations/{id}/status/` — Accepter/Refuser

## Fichiers créés
- `app/build.gradle.kts` — Configuration Gradle + dépendances
- `data/model/Models.kt` — Modèles de données (Property, User, Message...)
- `data/api/LogerTogoApi.kt` — Interface Retrofit2 complète
- `data/api/NetworkModule.kt` — Configuration OkHttp + JWT DataStore
- `ui/home/HomeFragment.kt` — Écran accueil + carousel auto-scroll
- `ui/home/HomeViewModel.kt` — ViewModel MVVM pour l'accueil
- `ui/auth/LoginFragment.kt` — Écran connexion
- `ui/auth/AuthViewModel.kt` — Gestion session + refresh token
- `ui/chat/ChatDetailFragment.kt` — Messagerie + upload photos
- `ui/chat/ChatViewModel.kt` — Polling temps réel + envoi optimiste

## Configuration requise
1. Android Studio Iguana ou supérieur
2. SDK Android 26+ (minimum)
3. JDK 17
4. Kotlin 2.0+

## Prochaines étapes
- [ ] Layouts XML (activity_main, fragment_home, fragment_login...)
- [ ] Navigation Graph (nav_graph.xml)
- [ ] PropertyDetailFragment + PropertyListFragment  
- [ ] Adapter RecyclerView (BoostedCarouselAdapter, PropertyListAdapter, MessagesAdapter)
- [ ] Tests API sur l'environnement de production
- [ ] Upload sur Google Play Store
