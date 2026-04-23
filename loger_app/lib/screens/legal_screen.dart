import 'package:flutter/material.dart';
import 'package:animate_do/animate_do.dart';

class LegalScreen extends StatelessWidget {
  const LegalScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: const Text('Mentions Légales', style: TextStyle(fontWeight: FontWeight.w900)),
        centerTitle: true,
        backgroundColor: Colors.white,
        elevation: 0,
        foregroundColor: const Color(0xFF004D40),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            FadeInDown(
              child: const Center(
                child: Text(
                  "📜 MENTIONS LÉGALES & CONDITIONS D’UTILISATION",
                  textAlign: TextAlign.center,
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Color(0xFF004D40)),
                ),
              ),
            ),
            const SizedBox(height: 10),
            const Center(child: Text("Application : Loger Togo", style: TextStyle(color: Colors.grey))),
            const SizedBox(height: 32),
            
            _buildSection(
              "1. ÉDITEUR DE L’APPLICATION",
              "L’application Loger Togo est éditée par :\n\n• Nom / Société : DigitalH\n• Adresse : Lomé, Togo\n• Email : contact@logertg.com\n• Téléphone : +228 90 00 00 00",
            ),
            
            _buildSection(
              "2. OBJET DE L’APPLICATION",
              "L’application Loger Togo est une plateforme numérique permettant :\n\n• De consulter des annonces immobilières (location, vente, colocation, etc.)\n• De publier des annonces immobilières\n• De mettre en relation les utilisateurs (bailleurs, agences, locataires, acheteurs)\n\n⚠️ Loger Togo agit uniquement comme intermédiaire technique et ne participe pas aux transactions entre utilisateurs.",
            ),
            
            _buildSection(
              "3. ACCÈS AU SERVICE",
              "L’accès à l’application est gratuit (hors frais internet). Certaines fonctionnalités nécessitent la création d’un compte utilisateur et la fourniture d’informations personnelles exactes. L’utilisateur s’engage à fournir des informations véridiques.",
            ),
            
            _buildSection(
              "4. RESPONSABILITÉ",
              "DigitalH (Loger Togo) :\n• Ne garantit pas l’exactitude ni la fiabilité des annonces publiées.\n• Ne vérifie pas systématiquement les contenus.\n• N’est pas responsable des litiges, fraudes ou transactions.\n\n👉 Les utilisateurs sont seuls responsables de leurs annonces et des accords conclus entre eux.",
            ),
            
            _buildSection(
              "5. UTILISATION DU CONTACT",
              "L’application permet de contacter directement les auteurs via WhatsApp. L’utilisateur s’engage à ne pas envoyer de messages abusifs ou frauduleux. Tout non-respect peut entraîner la suppression définitive du compte.",
            ),
            
            _buildSection(
              "6. DONNÉES PERSONNELLES",
              "Les données collectées (nom, email, téléphone, localisation) sont utilisées uniquement pour le fonctionnement de l’application et la mise en relation. DigitalH s’engage à protéger ces données.\n\nVous disposez d’un droit d’accès, de modification et de suppression via : contact@logertg.com",
            ),
            
            _buildSection(
              "7. PROPRIÉTÉ INTELLECTUELLE",
              "Tous les éléments de l’application (logo, design, textes, images) sont protégés. Toute reproduction ou utilisation sans autorisation est interdite.",
            ),
            
            _buildSection(
              "8. MODÉRATION DES CONTENUS",
              "DigitalH se réserve le droit de supprimer toute annonce non conforme ou illégale et de suspendre tout compte utilisateur suspect.",
            ),
            
            _buildSection(
              "9. MODIFICATION DES CONDITIONS",
              "Les présentes conditions peuvent être modifiées à tout moment. Les utilisateurs seront informés via l’application ou par email.",
            ),
            
            _buildSection(
              "10. DROIT APPLICABLE",
              "Les présentes conditions sont soumises au droit en vigueur au Togo.",
            ),
            
            _buildSection(
              "11. CONTACT",
              "Pour toute question ou réclamation :\n📧 contact@logertg.com\n📞 +228 90 00 00 00",
            ),
            
            const SizedBox(height: 40),
            Center(
              child: Text(
                "Dernière mise à jour : Avril 2026",
                style: TextStyle(color: Colors.grey.shade400, fontSize: 12),
              ),
            ),
            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildSection(String title, String content) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: const TextStyle(fontWeight: FontWeight.w900, color: Color(0xFF004D40), fontSize: 13, letterSpacing: 0.5),
          ),
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFFF8FAFC),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Text(
              content,
              style: TextStyle(color: Colors.blueGrey.shade700, fontSize: 14, height: 1.5),
            ),
          ),
        ],
      ),
    );
  }
}
