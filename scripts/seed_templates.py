import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from logersn.models import MarketingCampaignTemplate

TEMPLATES = [
    {
        'name': 'Bienvenue (Nouveaux Inscrits)',
        'subject': 'Bienvenue chez Loger Togo ! 🏠',
        'content': """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
            <h2 style="color: #2D3436;">Bienvenue [PRENOM] !</h2>
            <p>Nous sommes ravis de vous compter parmi nos membres.</p>
            <p>Loger Togo est la plateforme numéro 1 pour trouver ou proposer des biens immobiliers de prestige au Togo.</p>
            <p>Commencez dès maintenant à explorer nos annonces ou déposez la vôtre gratuitement.</p>
            <div style="text-align: center; margin-top: 30px;">
                <a href="https://logertogo.com/annonces/" style="background: #E84393; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Voir les annonces</a>
            </div>
            <p style="margin-top: 30px; font-size: 12px; color: #636E72;">L'équipe Loger Togo</p>
        </div>
        """
    },
    {
        'name': 'Offre Spéciale Réduction',
        'subject': 'Offre Spéciale : -20% sur votre prochain Boost ! 🚀',
        'content': """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
            <h2 style="color: #2D3436;">Bonjour [PRENOM],</h2>
            <p>Boostez la visibilité de vos annonces et vendez plus vite !</p>
            <p>Utilisez le code promo <strong>LOGER20</strong> lors de votre prochain paiement pour bénéficier de 20% de réduction immédiate.</p>
            <p>Offre valable pendant 48h seulement.</p>
            <div style="text-align: center; margin-top: 30px;">
                <a href="https://logertogo.com/mon-compte/" style="background: #0984E3; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Accéder à mon compte</a>
            </div>
        </div>
        """
    },
    {
        'name': 'Incitation à poster (Annonce)',
        'subject': 'Vos biens méritent le meilleur écrin 💎',
        'content': """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
            <h2 style="color: #2D3436;">Cher [NOM],</h2>
            <p>Vous avez des biens immobiliers à proposer ? Ne les laissez pas dormir !</p>
            <p>Sur Loger Togo, vous touchez une clientèle qualifiée et sérieuse chaque jour.</p>
            <p><strong>Postez votre première annonce en moins de 2 minutes :</strong></p>
            <div style="text-align: center; margin-top: 30px;">
                <a href="https://logertogo.com/annonces/nouvelle/" style="background: #00B894; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Publier une annonce</a>
            </div>
        </div>
        """
    },
    {
        'name': 'Voeux de Fêtes',
        'subject': 'Toute l\'équipe Loger Togo vous souhaite de joyeuses fêtes ! ✨',
        'content': """
        <div style="font-family: Arial, sans-serif; text-align: center; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
            <h1 style="color: #D63031;">Bonnes Fêtes [PRENOM] !</h1>
            <p>En cette période de célébration, nous tenions à vous remercier pour votre confiance.</p>
            <p>Que cette nouvelle année vous apporte joie, santé et réussite dans tous vos projets immobiliers.</p>
            <img src="https://logertogo.com/static/img/logo.png" style="width: 150px; margin-top: 20px;" />
        </div>
        """
    },
    {
        'name': 'Promotion Flash (Visibility)',
        'subject': 'Vendez votre bien ce weekend ! ⚡',
        'content': """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; border: 1px solid #eee; padding: 20px;">
            <h2 style="color: #2D3436;">Flash Info [PRENOM],</h2>
            <p>Ce weekend, nous doublons la visibilité des annonces "Premium".</p>
            <p>C'est le moment idéal pour mettre votre villa ou terrain en avant sur notre page d'accueil.</p>
            <div style="text-align: center; margin-top: 30px;">
                <a href="https://logertogo.com/annonces/" style="background: #6C5CE7; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Mettre en avant mes biens</a>
            </div>
        </div>
        """
    }
]

def seed():
    for t in TEMPLATES:
        obj, created = MarketingCampaignTemplate.objects.get_or_create(
            name=t['name'],
            defaults={'subject': t['subject'], 'content': t['content']}
        )
        if created:
            print(f"Modèle '{t['name']}' créé.")
        else:
            print(f"Modèle '{t['name']}' déjà existant.")

if __name__ == '__main__':
    seed()
