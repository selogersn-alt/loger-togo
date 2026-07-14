
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from blog.models import Post, Category, Tag
from users.models import User

author = User.objects.filter(is_superuser=True).first()
if not author:
    author = User.objects.first()

cat, _ = Category.objects.get_or_create(name="Guides & Conseils")
tag1, _ = Tag.objects.get_or_create(name="Immobilier Togo")
tag2, _ = Tag.objects.get_or_create(name="Location Lomé")
tag3, _ = Tag.objects.get_or_create(name="Agence Immobilière")
tag4, _ = Tag.objects.get_or_create(name="Investissement")

articles = [
    {
        'title': "Pourquoi investir dans l'immobilier à Lomé en 2026 ?",
        'content': '<p>L\'<strong>immobilier &agrave; Lom&eacute;</strong> est en plein boom. Avec une croissance &eacute;conomique soutenue et une urbanisation galopante, la capitale togolaise attire de plus en plus d\'investisseurs locaux et de la diaspora. Si vous h&eacute;sitez encore &agrave; vous lancer, voici pourquoi 2026 est l\'ann&eacute;e id&eacute;ale pour <strong>investir dans l\'immobilier au Togo</strong>.</p>\n<h2>1. Une demande locative en forte hausse</h2>\n<p>La population de Lom&eacute; ne cesse de cro&icirc;tre, cr&eacute;ant un besoin constant en <strong>appartements &agrave; louer</strong> et en <strong>maisons familiales</strong>. Les quartiers comme Ago&egrave;, Adidogom&eacute; ou Baguida voient leur valeur fonci&egrave;re augmenter, offrant une excellente rentabilit&eacute; locative.</p>\n<h2>2. Le d&eacute;veloppement des infrastructures</h2>\n<p>De nouvelles routes, des centres commerciaux et des infrastructures modernes transforment la physionomie de la ville. L\'achat d\'un <strong>terrain &agrave; vendre &agrave; Lom&eacute;</strong> dans des zones en d&eacute;veloppement est un investissement strat&eacute;gique &agrave; fort potentiel de plus-value.</p>\n<h2>3. Un cadre l&eacute;gal s&eacute;curis&eacute; avec Loger Togo</h2>\n<p>Aujourd\'hui, il est plus facile que jamais d\'investir gr&acirc;ce &agrave; des plateformes comme <strong><a href="https://logertogo.com">Loger Togo</a></strong>. Nous offrons une garantie de transparence, des <strong>agences immobili&egrave;res v&eacute;rifi&eacute;es</strong> et un accompagnement complet pour s&eacute;curiser votre investissement.</p>\n<p><em>Pr&ecirc;t &agrave; sauter le pas ? D&eacute;couvrez nos meilleures opportunit&eacute;s de <a href="https://logertogo.com/recherche/?type=VILLA">villas &agrave; vendre</a> et d\'investissements rentables sur notre portail.</em></p>',
        'image': 'blog/posts/2026/05/invest_lome.png',
        'tags': [tag1, tag4]
    },
    {
        'title': "Les 5 documents indispensables pour louer un appartement au Togo",
        'content': '<p>Trouver un <strong>appartement &agrave; louer &agrave; Lom&eacute;</strong> est une chose, mais signer le contrat de bail en est une autre ! Pour &ecirc;tre s&ucirc;r d\'obtenir le logement de vos r&ecirc;ves sans stress, il est primordial de constituer un dossier de location complet et rassurant pour le propri&eacute;taire ou l\'<strong>agence immobili&egrave;re</strong>.</p>\n<h2>1. Une pi&egrave;ce d\'identit&eacute; valide</h2>\n<p>Qu\'il s\'agisse de votre carte nationale d\'identit&eacute; (CNI), de votre passeport ou d\'une carte consulaire pour les expatri&eacute;s, c\'est le premier document que vous demandera tout propri&eacute;taire s&eacute;rieux.</p>\n<h2>2. Une preuve de revenus</h2>\n<p>Les bailleurs veulent s\'assurer que vous pouvez payer votre loyer. Fournissez vos trois derni&egrave;res fiches de paie ou, si vous &ecirc;tes entrepreneur, vos extraits de compte bancaire et votre carte CFE.</p>\n<h2>3. L\'apport initial (Caution et Avance)</h2>\n<p>Au Togo, il est courant de payer une avance et une caution &eacute;quivalant &agrave; plusieurs mois de loyer. Pr&eacute;parez ce budget &agrave; l\'avance pour ne pas rater une opportunit&eacute; en or.</p>\n<h2>4. Les coordonn&eacute;es d\'un garant</h2>\n<p>Un garant solide est souvent exig&eacute; pour s&eacute;curiser le <strong>contrat de bail au Togo</strong>. Assurez-vous d\'avoir la copie de sa pi&egrave;ce d\'identit&eacute; et ses coordonn&eacute;es compl&egrave;tes.</p>\n<h2>5. Un contrat de travail</h2>\n<p>Il permet de rassurer le bailleur sur la p&eacute;rennit&eacute; de votre situation professionnelle &agrave; Lom&eacute;.</p>\n<p><em>Besoin d\'aide pour trouver votre prochain cocon ? Parcourez nos <a href="https://logertogo.com">annonces d\'appartements v&eacute;rifi&eacute;s sur Loger Togo</a> et louez en toute s&eacute;r&eacute;nit&eacute; !</em></p>',
        'image': 'blog/posts/2026/05/docs_location.png',
        'tags': [tag1, tag2]
    },
    {
        'title': "Comment bien choisir son agence immobilière à Lomé ?",
        'content': '<p>Le march&eacute; de l\'<strong>immobilier au Togo</strong> est vaste, et il n\'est pas toujours facile de savoir &agrave; qui faire confiance. Que vous cherchiez &agrave; d&eacute;l&eacute;guer la <strong>gestion locative</strong> de votre bien ou &agrave; trouver une <strong>maison &agrave; louer &agrave; Lom&eacute;</strong>, le choix de votre agence est crucial.</p>\n<h2>1. V&eacute;rifier la l&eacute;galit&eacute; et l\'existence physique</h2>\n<p>Assurez-vous que l\'agence poss&egrave;de une vraie structure (bureaux physiques) et qu\'elle est enregistr&eacute;e (carte professionnelle, registre du commerce). &Eacute;vitez les d&eacute;marcheurs informels sans garanties.</p>\n<h2>2. Consulter la r&eacute;putation et les avis</h2>\n<p>Une bonne <strong>agence immobili&egrave;re &agrave; Lom&eacute;</strong> a des clients satisfaits. Cherchez des avis en ligne ou demandez des recommandations. Sur <a href="https://logertogo.com/professionnels/">notre annuaire de professionnels</a>, nous ne r&eacute;f&eacute;ren&ccedil;ons que des acteurs v&eacute;rifi&eacute;s.</p>\n<h2>3. La transparence des tarifs</h2>\n<p>Les frais d\'agence (g&eacute;n&eacute;ralement 1 mois de loyer pour une location) et les frais de visite doivent &ecirc;tre annonc&eacute;s clairement d&egrave;s le d&eacute;part. M&eacute;fiez-vous des agences qui exigent des paiements avant toute prestation concr&egrave;te.</p>\n<h2>4. L\'expertise locale</h2>\n<p>Privil&eacute;giez une agence qui ma&icirc;trise parfaitement le secteur que vous visez (ex: une agence sp&eacute;cialis&eacute;e sur Baguida ou Ago&egrave; aura de meilleures offres dans ces zones).</p>\n<p><em>Simplifiez-vous la vie en choisissant parmi nos <strong><a href="https://logertogo.com/professionnels/">partenaires de confiance sur Loger Togo</a></strong>. Des experts s&eacute;lectionn&eacute;s pour vous offrir un service premium.</em></p>',
        'image': 'blog/posts/2026/05/agency_lome.png',
        'tags': [tag1, tag3]
    }
]

for a in articles:
    post, created = Post.objects.get_or_create(
        title=a['title'],
        defaults={
            'author': author,
            'category': cat,
            'status': 'PUBLISHED',
            'content': a['content'],
            'featured_image': a['image']
        }
    )
    if not created:
        post.content = a['content']
        post.featured_image = a['image']
        post.status = 'PUBLISHED'
        post.save()
    post.tags.add(*a['tags'])
    print(f"Article '{a['title']}' processed!")
