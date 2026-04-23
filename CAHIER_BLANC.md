# 🛡️ CAHIER BLANC : Loger Togo (DIGITALH)
**Édition de Prestige - Version 1.0 (Avril 2026)**

---

## 1. VISION STRATÉGIQUE
**Loger Togo**, propulsé par l'écosystème **DigitalH**, est une plateforme immobilière de confiance totale. Elle résout le problème majeur du marché sénégalais : **l'insécurité transactionnelle**. 

La plateforme repose sur trois piliers :
1.  **La Confiance (NILS)** : Vérification d'identité certifiée par IA.
2.  **La Sécurité (SOLVABLE)** : Filiation entre bailleur et locataire pour un suivi des paiements.
3.  **La Monétisation (PÉAGE)** : Un modèle économique ultra-accessible et scalable.

---

## 2. ARCHITECTURE TECHNIQUE
### 2.1 Stack Technologique
*   **Core** : Python 3.13 / Django 6.0 (Architecture MVC robuste).
*   **Database** : PostgreSQL (Prêt pour la production) / SQLite (Développement).
*   **Design** : DigitalH Design System (Vanilla CSS, Luxe & Glassmorphism).
*   **Logiciel Monétaire** : Pont d'intégration FedaPay Bridge.

### 2.2 Hiérarchie de Gouvernance
*   **Super-Admin (DigitalH Owner)** : Contrôle total des revenus et des accès.
*   **Sous-Administrateur** : Gestion opérationnelle déléguée (Staff).
*   **Conseiller Client** : Support technique et validation des annonces (Staff).
*   **Professionnels (Agents/Bailleurs)** : Utilisateurs certifiés avec badge de confiance.

---

## 3. MOTEUR DE MONÉTISATION (Standard DigitalH)
Le système repose sur un péage de publication et d'upsell à faible coût pour garantir un volume élevé de transactions.

| Service | Tarif (FCFA) | Impact Visuel | Fréquence |
| :--- | :--- | :--- | :--- |
| **Publication** | 100 F | Présence sur le site | Par annonce |
| **Boost Quotidien** | 100 F | Bandeau Premium & Top de liste | Par jour |
| **Premium Pop-up** | 500 F | Modal Plein Écran (10s delay) | Par jour |

---

## 4. SÉCURITÉ & RÉCUPÉRATION (H-RECOVERY)
Pour limiter les coûts de maintenance (SMS/Email), **DigitalH** utilise un tunnel de récupération assistée par humain via WhatsApp :
*   **Pas de coûts API** pour la plateforme.
*   **Vérification Humaine** : L'assistant génère un code à 6 chiffres unique pour le client.
*   **Support Direct** : Ouverture d'un canal WhatsApp direct entre l'admin et l'utilisateur.

---

## 5. EXPÉRIENCE UTILISATEUR (UX)
### 5.1 Le Bandeau Premium
Animation fluide de la **gauche vers la droite** (`animate__slideInLeft`). Une sélection d'exclusivités rafraîchie toutes les 5 secondes pour une dynamique de catalogue moderne.

### 5.2 Le Profil NILS
Un score de confiance calculé sur l'historique de paiement et de comportement. Ce score (Gauge) est le passeport du locataire et du bailleur sur le marché DigitalH.

---

## 6. PROCHAINES ÉTAPES (Feuille de Route)
1.  **Activation FedaPay** : Remplacement du simulateur par les clés API réelles.
2.  **Audit KYC Automatisé** : Connexion aux API de reconnaissance faciale (Vision API).
3.  **Application Mobile** : Synchronisation avec le Dashboard Web Responsive.

---
**DigitalH - "L'Immobilier de Confiance au Togo"**
