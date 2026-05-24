import os
import django
import sys

# Ensure we're in the correct directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from management.models import ContractTemplate

def populate():
    print("Insertion des modèles de contrats par défaut...")
    
    # Template 1: Classique Officiel
    t1_content = """
    <div style="font-family: 'Times New Roman', Times, serif; color: #000; padding: 20px; line-height: 1.6;">
        <div style="text-align: center; margin-bottom: 30px;">
            <img src="/static/img/logo_dark.png" alt="Logo" style="max-height: 80px;" />
            <h1 style="font-size: 24px; text-transform: uppercase; border-bottom: 2px solid #000; padding-bottom: 10px; margin-top: 20px;">
                CONTRAT DE BAIL À USAGE D'HABITATION
            </h1>
            <p style="font-style: italic; color: #555;">[EN_TETE_PERSONNALISE]</p>
        </div>
        
        <p><strong>ENTRE LES SOUSSIGNÉS :</strong></p>
        <p>
            Le Bailleur / L'Agence : <strong>[PROPRIETAIRE]</strong><br>
            Désigné ci-après "LE BAILLEUR"
        </p>
        <p><strong>ET :</strong></p>
        <p>
            Le Preneur : <strong>[LOCATAIRE]</strong><br>
            Désigné ci-après "LE LOCATAIRE"
        </p>
        
        <h3 style="text-decoration: underline; margin-top: 20px;">ARTICLE 1 : DÉSIGNATION DU BIEN</h3>
        <p>Le Bailleur donne en location au Locataire le bien désigné ci-après : <strong>[BIEN]</strong>.</p>
        
        <h3 style="text-decoration: underline; margin-top: 20px;">ARTICLE 2 : DURÉE DU BAIL</h3>
        <p>Le présent bail est consenti pour une durée commençant le <strong>[DATE_DEBUT]</strong> au <strong>[DATE_FIN]</strong>.</p>
        
        <h3 style="text-decoration: underline; margin-top: 20px;">ARTICLE 3 : LOYER ET CONDITIONS</h3>
        <p>Le loyer mensuel est fixé à la somme de <strong>[LOYER] FCFA</strong>. Le dépôt de garantie est de <strong>[CAUTION] FCFA</strong>.</p>
        
        <div style="background-color: #f9f9f9; padding: 15px; border-left: 4px solid #333; margin-top: 20px;">
            <h4>CLAUSES PARTICULIÈRES :</h4>
            <p>[CLAUSES_PARTICULIERES]</p>
        </div>
        
        <div style="margin-top: 50px; display: flex; justify-content: space-between;">
            <div style="text-align: left;">
                <p><strong>SIGNATURE DU LOCATAIRE</strong></p>
                <p style="color: #999; font-style: italic;">[SIGNATURE_LOCATAIRE]</p>
            </div>
            <div style="text-align: right;">
                <p><strong>SIGNATURE DU BAILLEUR</strong></p>
                <p style="color: #999; font-style: italic;">[SIGNATURE_BAILLEUR]</p>
            </div>
        </div>
    </div>
    """
    
    # Template 2: Moderne Coloré
    t2_content = """
    <div style="font-family: 'Helvetica Neue', Arial, sans-serif; color: #334155; padding: 20px; line-height: 1.6;">
        <div style="display: flex; justify-content: space-between; align-items: flex-end; border-bottom: 4px solid #0ea5e9; padding-bottom: 20px; margin-bottom: 30px;">
            <div>
                <h1 style="color: #0ea5e9; font-size: 28px; margin: 0; font-weight: 800;">CONTRAT DE LOCATION</h1>
                <p style="color: #64748b; margin: 5px 0 0 0; font-size: 14px;">[EN_TETE_PERSONNALISE]</p>
            </div>
            <img src="/static/img/logo_dark.png" alt="Logo" style="max-height: 60px;" />
        </div>
        
        <div style="display: flex; gap: 20px; margin-bottom: 30px;">
            <div style="flex: 1; background: #f0f9ff; padding: 15px; border-radius: 8px;">
                <h4 style="color: #0284c7; margin-top: 0;">LE BAILLEUR</h4>
                <p style="margin-bottom: 0;"><strong>[PROPRIETAIRE]</strong></p>
            </div>
            <div style="flex: 1; background: #f0f9ff; padding: 15px; border-radius: 8px;">
                <h4 style="color: #0284c7; margin-top: 0;">LE LOCATAIRE</h4>
                <p style="margin-bottom: 0;"><strong>[LOCATAIRE]</strong></p>
            </div>
        </div>
        
        <h3 style="color: #0f172a; border-left: 3px solid #0ea5e9; padding-left: 10px;">1. LE BIEN</h3>
        <p style="background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0;"><strong>[BIEN]</strong></p>
        
        <h3 style="color: #0f172a; border-left: 3px solid #0ea5e9; padding-left: 10px;">2. MODALITÉS FINANCIÈRES</h3>
        <table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;"><strong>Loyer Mensuel</strong></td>
                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right; color: #059669; font-weight: bold;">[LOYER] FCFA</td>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;"><strong>Dépôt de Garantie</strong></td>
                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right; font-weight: bold;">[CAUTION] FCFA</td>
            </tr>
            <tr>
                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;"><strong>Période du bail</strong></td>
                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0; text-align: right;">Du [DATE_DEBUT] au [DATE_FIN]</td>
            </tr>
        </table>
        
        <h3 style="color: #0f172a; border-left: 3px solid #0ea5e9; padding-left: 10px;">3. CLAUSES PARTICULIÈRES</h3>
        <div style="background: #f8fafc; padding: 15px; border-radius: 8px; border: 1px solid #e2e8f0; font-style: italic;">
            [CLAUSES_PARTICULIERES]
        </div>
        
        <div style="margin-top: 40px; background: #0f172a; color: white; padding: 20px; border-radius: 8px; display: flex; justify-content: space-between;">
            <div style="text-align: left;">
                <p style="margin-top: 0; color: #94a3b8; font-size: 12px; text-transform: uppercase;">Lu et Approuvé, Le Locataire</p>
                <p style="margin-bottom: 0;">[SIGNATURE_LOCATAIRE]</p>
            </div>
            <div style="text-align: right;">
                <p style="margin-top: 0; color: #94a3b8; font-size: 12px; text-transform: uppercase;">Pour l'Agence / Le Bailleur</p>
                <p style="margin-bottom: 0;">[SIGNATURE_BAILLEUR]</p>
            </div>
        </div>
    </div>
    """
    
    # Template 3: Premium Minimaliste
    t3_content = """
    <div style="font-family: 'Courier New', Courier, monospace; color: #111; padding: 40px; line-height: 1.8; position: relative; max-width: 800px; margin: 0 auto; border: 1px solid #eee;">
        
        <!-- Filigrane (Watermark) -->
        <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); opacity: 0.03; pointer-events: none;">
            <img src="/static/img/logo_dark.png" alt="Watermark" style="width: 400px; filter: grayscale(100%);" />
        </div>

        <div style="text-align: center; margin-bottom: 50px;">
            <h1 style="font-weight: 300; letter-spacing: 4px; font-size: 20px;">ACCORD DE LOCATION</h1>
            <div style="height: 1px; width: 50px; background: #111; margin: 20px auto;"></div>
            <p style="font-size: 12px; color: #888; text-transform: uppercase; letter-spacing: 2px;">[EN_TETE_PERSONNALISE]</p>
        </div>

        <div style="margin-bottom: 40px;">
            <p style="margin: 0; font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px;">Partie 01 - Les Parties</p>
            <p style="margin-top: 5px;">Le présent accord est conclu entre <strong>[PROPRIETAIRE]</strong> (Bailleur) d'une part, et <strong>[LOCATAIRE]</strong> (Locataire) d'autre part.</p>
        </div>

        <div style="margin-bottom: 40px;">
            <p style="margin: 0; font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px;">Partie 02 - L'Objet</p>
            <p style="margin-top: 5px;">Le Bailleur loue le bien suivant : <strong>[BIEN]</strong>.</p>
            <p>La location s'étend du <strong>[DATE_DEBUT]</strong> au <strong>[DATE_FIN]</strong>.</p>
        </div>

        <div style="margin-bottom: 40px;">
            <p style="margin: 0; font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px;">Partie 03 - Conditions Financières</p>
            <p style="margin-top: 5px;">
                Loyer Mensuel : <strong>[LOYER] FCFA</strong><br>
                Dépôt de Garantie : <strong>[CAUTION] FCFA</strong>
            </p>
        </div>

        <div style="margin-bottom: 40px;">
            <p style="margin: 0; font-size: 11px; color: #888; text-transform: uppercase; letter-spacing: 1px;">Partie 04 - Conditions Particulières</p>
            <div style="padding: 10px; border-left: 2px solid #111; margin-top: 10px; background: #fafafa;">
                <p style="margin: 0; font-size: 13px;">[CLAUSES_PARTICULIERES]</p>
            </div>
        </div>

        <div style="margin-top: 60px; border-top: 1px solid #eee; padding-top: 20px; display: flex; justify-content: space-between; font-size: 12px;">
            <div style="width: 45%;">
                <p style="margin-bottom: 40px;">Bailleur / Agence :</p>
                <div style="border-bottom: 1px dotted #ccc; padding-bottom: 5px;">[SIGNATURE_BAILLEUR]</div>
            </div>
            <div style="width: 45%;">
                <p style="margin-bottom: 40px;">Locataire :</p>
                <div style="border-bottom: 1px dotted #ccc; padding-bottom: 5px;">[SIGNATURE_LOCATAIRE]</div>
            </div>
        </div>
        
        <div style="text-align: center; margin-top: 40px;">
            <img src="/static/img/logo_dark.png" alt="Logo" style="max-height: 30px; opacity: 0.5;" />
        </div>
    </div>
    """

    ContractTemplate.objects.update_or_create(
        title="Classique Officiel (Global)",
        agency=None,
        defaults={'content': t1_content}
    )
    
    ContractTemplate.objects.update_or_create(
        title="Moderne Coloré (Global)",
        agency=None,
        defaults={'content': t2_content}
    )
    
    ContractTemplate.objects.update_or_create(
        title="Premium Minimaliste (Global)",
        agency=None,
        defaults={'content': t3_content}
    )
    
    print("Modèles globaux ajoutés avec succès !")

if __name__ == '__main__':
    populate()
