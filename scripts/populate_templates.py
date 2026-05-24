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
    
    # Template 1: Classique Officiel (Togo)
    t1_content = """
    <div style="font-family: 'Times New Roman', Times, serif; color: #000; padding: 20px; line-height: 1.6; font-size: 14px;">
        <div style="text-align: center; margin-bottom: 30px;">
            <img src="/static/img/logo_dark.png" alt="Logo" style="max-height: 80px;" />
            <h1 style="font-size: 22px; text-transform: uppercase; border-bottom: 2px solid #000; padding-bottom: 10px; margin-top: 20px;">
                CONTRAT DE LOCATION à usage d'habitation
            </h1>
        </div>
        
        <p><strong>ENTRE LES SOUSSIGNÉS,</strong><br>
        <strong>[NOM_BAILLEUR]</strong><br>
        Ci-après dénommé LE BAILLEUR, d'une part</p>
        
        <p><strong>ET</strong><br>
        <strong>[NOM_COMPLET_CLIENT]</strong> , titulaire d'une pièce d'identité [NATIONALITE_CLIENT] Numéro : [NUMERO_CARTE_CLIENT]<br>
        Ci-après dénommé LE LOCATAIRE, d'autre part</p>
        
        <p><strong>Il a été arrêté et convenu ce qui suit :</strong><br>
        Le bailleur louant les locaux et équipements ci-après, désignés, au locataire qui les accepte aux conditions suivantes. Le locataire déclare bien connaître les lieux loués pour les avoir visités.</p>
        
        <h3 style="text-decoration: underline; font-size: 16px; margin-top: 20px;">DÉSIGNATION</h3>
        <p><strong>[TYPE_DE_BIEN]</strong><br>
        Consistance des locaux :<br>
        [DETAILS_DE_BIEN]</p>
        
        <h3 style="text-decoration: underline; font-size: 16px; margin-top: 20px;">DESTINATION DES LOCAUX</h3>
        <p>A usage <strong>[TYPE_D_USAGE]</strong></p>
        
        <h2 style="font-size: 18px; text-align: center; margin-top: 30px;">CONDITIONS GENERALES</h2>
        
        <p><strong>1) DURÉE DU CONTRAT</strong><br>
        Le bail est consenti pour une durée au moins égale à UN (01) AN avec tacite reconduction.</p>
        
        <p><strong>2) CONGÉ</strong><br>
        Le congé doit être signifié par lettre. II peut être délivré à tout moment par le locataire en respectant un préavis de DEUX (02) MOIS courant à compter de la réception de la lettre ou de l'acte. Le congé délivré par le bailleur ne peut être délivré que pour le terme du contrat initial ou renouvelé en respectant un préavis de SIX (06) MOIS. Le congé du bailleur ne peut être délivré que pour un des trois motifs ci-après, dûment énoncés dans l'acte : Reprise du local au bénéfice du bailleur ; Vente du local ; Motif légitime et sérieux, notamment l'inexécution par le locataire d'une des obligations lui incombant.</p>
        
        <p><strong>3) RECONDUCTION DU CONTRAT</strong><br>
        A défaut de congé régulier du bailleur ou du locataire, le contrat parvenu à son terme est reconduit tacitement pour une durée égale à celle du contrat initial.</p>
        
        <p><strong>4) RENOUVELLEMENT DU CONTRAT</strong><br>
        A défaut de congé et de tacite reconduction, le contrat parvenu à son terme peut également faire l'objet d'une offre de renouvellement de la part du bailleur.</p>
        
        <p><strong>5) ABANDON DU DOMICILE</strong><br>
        Le bail est résilié de plein droit par l'abandon de domicile du locataire.</p>
        
        <p><strong>6) OBLIGATIONS DU BAILLEUR</strong><br>
        Le bailleur est obligé :<br>
        - De délivrer le logement en bon état d'usage et de réparation ;<br>
        - De délivrer les éléments d'équipement en bon état de fonctionnement ;<br>
        - D'assurer au locataire une jouissance paisible et la garantie des vices ou défauts ;<br>
        - De maintenir les locaux en état de servir à l'usage prévu par le contrat ;<br>
        - De ne pas s'opposer aux aménagements réalisés par le locataire dès lors qu'ils n'entraînent pas une transformation du local ;<br>
        - De remettre gratuitement une quittance au locataire qui en fait la demande.</p>
        
        <p><strong>7) OBLIGATIONS DU LOCATAIRE</strong><br>
        Le locataire est obligé :<br>
        - De payer le loyer ;<br>
        - D'user paisiblement des locaux loués en respectant leur destination ;<br>
        - De répondre des dégradations ou des pertes survenues pendant le cours du bail ;<br>
        - De prendre à sa charge l'entretien courant du logement et des équipements ;<br>
        - De ne faire aucun changement de distribution ou transformation sans l'accord préalable et écrit du bailleur ;<br>
        - De ne pouvoir, ni sous-louer ni céder ni prêter les locaux, même temporairement, sauf accord exprès ;<br>
        - D'informer immédiatement le bailleur de tous désordres, dégradations et sinistres ;<br>
        - De laisser exécuter sans indemnité tous les travaux nécessaires ;<br>
        - En cas de vente ou de nouvelle location, de laisser visiter le logement deux heures par jour pendant les jours ouvrables ;<br>
        - De respecter le règlement de l'immeuble, la circulation dans les parties communes et la quiétude de l'immeuble ;<br>
        - De renoncer à tout recours contre le bailleur en cas de vol commis dans les lieux loués, interruption du service de l'eau, du gaz, de l'électricité, trouble de voisinage ;<br>
        - De satisfaire à toutes les charges de ville ou de police.</p>
        
        <p><strong>8) MONTANT DU LOYER</strong><br>
        Le montant mensuel du loyer est fixé à <strong>[PRIX_DU_BIEN]</strong> payable au plus tard le 05 de chaque mois.</p>
        
        <p><strong>9) DÉPÔT DE GARANTIE</strong><br>
        Le montant du dépôt de garantie est indiqué aux CONDITIONS PARTICULIÈRES du présent contrat. Il ne peut excéder un mois du loyer principal et un (1) mois de caution. Il n'est pas productif d'intérêt. Il est destiné à être remboursé au locataire sortant dans les DEUX (02) MOIS de son départ effectif, déduction faite des sommes restant dues au bailleur.</p>
        
        <p><strong>10) CLAUSE RÉSOLUTOIRE</strong><br>
        Il est expressément convenu qu'à défaut de paiement au terme convenu de tout ou partie du loyer, des charges, du dépôt de garantie, et DEUX (02) MOIS après un commandement de payer demeuré infructueux, la présente location sera résiliée de plein droit si bon semble au bailleur, sans aucune formalité judiciaire. L'occupant déchu de ses droits locatifs qui se refusera à restituer les lieux, pourra être expulsé sur simple ordonnance du juge des référés.</p>
        
        <p><strong>11) CLAUSE PÉNALE</strong><br>
        En cas de non paiement du loyer ou de ses accessoires et dès le premier acte d'huissier, le locataire devra payer en sus des frais de recouvrement au bailleur. En cas d'occupation des lieux après la cessation du bail, il sera dû par l'occupant une indemnité égale au double du loyer et des charges contractuels. En cas de résiliation du bail aux torts du locataire, le dépôt de garantie restera acquis au bailleur à titre d'indemnité conventionnelle.</p>
        
        <p><strong>12) ÉTAT DES LIEUX</strong><br>
        A défaut d'état d'entrée ou de sortie des lieux établi volontairement et contradictoirement, la partie la plus diligente est en droit d'en faire dresser un par huissier, à frais partagés.</p>
        
        <h2 style="font-size: 18px; text-align: center; margin-top: 40px; border-top: 1px solid #ccc; padding-top: 20px;">CONDITIONS PARTICULIÈRES</h2>
        
        <p><strong>Durée</strong><br>
        Le présent contrat est consenti pour une durée d'Un (01) An commençant à courir le <strong>[DATE_DEBUT_CONTRAT]</strong> et se terminant le <strong>[DATE_FIN_CONTRAT]</strong> sous réserve de reconduction tacite ou de renouvellement.</p>
        
        <p><strong>Dépôt de garantie</strong><br>
        Le dépôt de garantie est fixé à la somme de <strong>[CAUTION]</strong> correspondant à :<br>
        - Un (01) mois de loyer ;<br>
        - Un (01) mois de caution.<br>
        Le mois est payable d'avance.</p>
        
        <p><strong>Eau et Electricité :</strong><br>
        Les factures d'eau et d'électricité de l'appartement loué sont à la charge du locataire. La police d'abonnement doit être au nom du locataire, et au moment de rendre l'appartement toutes les factures doivent être payées avec présentation des reçus.</p>
        
        <p><strong>Clauses particulières supplémentaires :</strong><br>
        - Dans le but de respecter scrupuleusement la quiétude des voisins, le nombre de personnes ne peut dépasser six (04) par Studio.<br>
        - Les bruits sonores sont prohibés.<br>
        - Aucun animal domestique n'est toléré.<br>
        - D'autre part, le locataire étant son propre assureur, il lui est conseillé d'assurer ses biens et personnes à sa charge en cas de sinistre pour toute la durée du contrat. Le propriétaire ne peut en aucun cas être responsable ou réparation de tout sinistre qui frappe le preneur sauf en ce qui concerne les dégâts résultant de ses obligations.<br>
        - Aucune action judiciaire ne peut être enclenchée en son encontre en cas de vol.<br>
        - Toutefois, le bailleur, à sa charge, met à la disposition de l'immeuble une personne qui s'occupera de l'entretien des parties communes.</p>
        
        <p style="text-align: right; margin-top: 30px;">Fait à Dakar le <strong>[DATE_D_ETABLISSEMENT]</strong><br>
        En deux (02) originaux dont un pour chaque signataire.</p>
        
        <p style="font-style: italic; text-align: center;">Signature précédée de la mention « lu et approuvé »</p>
        
        <div style="margin-top: 40px; display: flex; justify-content: space-between;">
            <div style="text-align: left; width: 45%;">
                <p><strong>Le Bailleur</strong></p>
                <div style="height: 100px; border-bottom: 1px dotted #000;">[SIGNATURE_BAILLEUR]</div>
            </div>
            <div style="text-align: right; width: 45%;">
                <p><strong>Le Locataire</strong></p>
                <div style="height: 100px; border-bottom: 1px dotted #000;">[SIGNATURE_LOCATAIRE]</div>
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
