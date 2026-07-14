import paramiko
import os
import json

HOST = '157.180.127.70'
USER = 'root'
PASSWORD = 'AkueMax@2022'

# Local paths for generated images
FEATURED_LOCAL = r"C:\Users\mursd\.gemini\antigravity-ide\brain\1170fcec-a1ef-4c15-a41a-c47daebedddb\featured_lome_1780153148904.png"
VILLA_LOCAL = r"C:\Users\mursd\.gemini\antigravity-ide\brain\1170fcec-a1ef-4c15-a41a-c47daebedddb\villa_lome_1780153163332.png"

# Remote paths
REMOTE_MEDIA_UPLOADS = "/app/media/uploads"
REMOTE_MEDIA_BLOG = "/app/media/blog/posts/2026/05"

def deploy_article():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(HOST, username=USER, password=PASSWORD, timeout=30)
        sftp = ssh.open_sftp()
        
        print("Creating remote directories...")
        ssh.exec_command(f"mkdir -p {REMOTE_MEDIA_UPLOADS}")
        ssh.exec_command(f"mkdir -p {REMOTE_MEDIA_BLOG}")
        
        print("Uploading images...")
        sftp.put(FEATURED_LOCAL, f"{REMOTE_MEDIA_BLOG}/featured_lome.png")
        sftp.put(VILLA_LOCAL, f"{REMOTE_MEDIA_UPLOADS}/villa_lome.png")
        
        # Prepare content
        content = """<p>Trouver un logement &agrave; Lom&eacute; peut sembler &ecirc;tre un d&eacute;fi, mais avec la bonne approche, vous pouvez s&eacute;curiser votre futur chez-vous rapidement. Que vous soyez &agrave; la recherche d'une <strong>location d'appartement &agrave; Lom&eacute;</strong> ou d'une <strong>maison &agrave; louer</strong>, il est essentiel d'adopter une m&eacute;thodologie rigoureuse pour &eacute;viter les pi&egrave;ges du march&eacute;.</p>
<p>Voici les meilleures pratiques pour r&eacute;ussir votre projet immobilier au Togo.</p>

<h2>1. D&eacute;finir son budget pour une location immobili&egrave;re &agrave; Lom&eacute;</h2>
<p>Avant de parcourir les annonces, d&eacute;terminez votre capacit&eacute; financi&egrave;re. En plus du loyer mensuel, n'oubliez pas d'inclure dans votre calcul :</p>
<ul>
    <li>La caution et l'avance (standard au Togo).</li>
    <li>Les honoraires de votre <strong>agence immobili&egrave;re &agrave; Lom&eacute;</strong>.</li>
    <li>Les charges annexes (eau, &eacute;lectricit&eacute;, s&eacute;curit&eacute;, entretien).</li>
</ul>

<h2>2. Choisir le quartier adapt&eacute; &agrave; ses besoins</h2>
<p>Lom&eacute; propose des cadres de vie vari&eacute;s. Voici o&ugrave; chercher selon vos priorit&eacute;s :</p>
<ul>
    <li><strong>Tokoin</strong> : Le choix des cadres et expatri&eacute;s pour sa modernit&eacute; et sa centralit&eacute;.</li>
    <li><strong>Ago&egrave;</strong> : Id&eacute;al pour les familles cherchant un excellent rapport qualit&eacute;-prix.</li>
    <li><strong>Baguida</strong> : Le secteur pris&eacute; pour le calme et la proximit&eacute; avec la mer.</li>
    <li><strong>Adidogom&eacute;</strong> : Un quartier dynamique avec une offre diversifi&eacute;e de logements accessibles.</li>
    <li><strong>Ny&eacute;konakpo&egrave; et Kodjoviakop&eacute;</strong> : L'emplacement strat&eacute;gique au c&oelig;ur de l'activit&eacute; &eacute;conomique.</li>
</ul>

<img src="/media/uploads/villa_lome.png" alt="Villa moderne à Lomé Togo" style="width:100%; border-radius: 8px; margin: 20px 0;">

<h2>3. Utiliser une plateforme immobili&egrave;re fiable au Togo</h2>
<p>Pour &eacute;viter les d&eacute;placements inutiles, privil&eacute;giez les outils num&eacute;riques. Une plateforme comme <strong>Loger Togo</strong> vous permet de filtrer vos recherches par budget, zone g&eacute;ographique et type de bien (<strong>villa &agrave; louer Lom&eacute;</strong>, appartement meubl&eacute;, etc.). Utilisez les filtres avanc&eacute;s pour cibler uniquement les annonces v&eacute;rifi&eacute;es et gagner un temps pr&eacute;cieux.</p>

<h2>4. Visiter plusieurs biens avant de d&eacute;cider</h2>
<p>Ne vous fiez jamais uniquement aux photos. Lors de vos visites, v&eacute;rifiez :</p>
<ul>
    <li>L'&eacute;tat de la plomberie et l'acc&egrave;s &agrave; l'eau.</li>
    <li>La stabilit&eacute; de l'installation &eacute;lectrique.</li>
    <li>La qualit&eacute; du r&eacute;seau internet et la s&eacute;curit&eacute; du secteur.</li>
    <li>L'isolation phonique du b&acirc;timent.</li>
</ul>

<h2>5. Comment &eacute;viter les arnaques immobili&egrave;res ?</h2>
<p>La s&eacute;curit&eacute; est primordiale. Pour une recherche sereine :</p>
<ul>
    <li>Ne versez aucun argent avant d'avoir visit&eacute; physiquement le bien.</li>
    <li>Exigez de voir les titres de propri&eacute;t&eacute; ou le mandat de l'agence.</li>
    <li>Passez par des acteurs reconnus de l'<strong>immobilier Lom&eacute;</strong>.</li>
</ul>

<h2>6. Pr&eacute;parer son dossier de location</h2>
<p>&Agrave; Lom&eacute;, les meilleures offres partent tr&egrave;s vite. Soyez r&eacute;actif en pr&eacute;parant un dossier complet :</p>
<ul>
    <li>Pi&egrave;ce d'identit&eacute; en cours de validit&eacute;.</li>
    <li>Preuve de revenus ou contrat de travail.</li>
    <li>Coordonn&eacute;es d'un garant solide.</li>
</ul>

<h2>7. Comparer avant de signer son bail</h2>
<p>Ne signez pas la premi&egrave;re offre venue. Comparez le prix au m&egrave;tre carr&eacute;, la proximit&eacute; des transports, des &eacute;coles et des commerces. Une comparaison minutieuse vous garantit le meilleur rapport qualit&eacute;-prix pour votre location &agrave; Lom&eacute;.</p>

<h3>Conclusion : Trouvez votre futur logement en toute s&eacute;r&eacute;nit&eacute;</h3>
<p>La r&eacute;ussite de votre recherche immobili&egrave;re repose sur la pr&eacute;paration et l'utilisation de canaux de confiance. Ne laissez rien au hasard et entourez-vous de professionnels pour s&eacute;curiser votre transaction.</p>
<p><em>Vous recherchez actuellement un appartement, une villa ou une maison &agrave; louer &agrave; Lom&eacute; ?<br>
Consultez d&egrave;s maintenant les annonces v&eacute;rifi&eacute;es sur <a href="https://logertogo.com"><strong>Loger Togo, la plateforme immobili&egrave;re v&eacute;rifi&eacute;e</strong></a> pour trouver votre logement en toute confiance sur tout le territoire.</em></p>"""

        script_code = f"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'logertogo.settings')
django.setup()

from blog.models import Post, Category, Tag
from users.models import User

# Get an author
author = User.objects.filter(is_superuser=True).first()
if not author:
    author = User.objects.first()

# Create category
cat, _ = Category.objects.get_or_create(name="Guides & Conseils")

# Create tags
tag1, _ = Tag.objects.get_or_create(name="Immobilier Togo")
tag2, _ = Tag.objects.get_or_create(name="Location Lomé")

title = "Comment trouver un logement à Lomé en 2026 ? Le guide complet"
content = {repr(content)}

# Create post
post, created = Post.objects.get_or_create(
    title=title,
    defaults={{
        'author': author,
        'category': cat,
        'status': 'PUBLISHED',
        'content': content,
        'featured_image': 'blog/posts/2026/05/featured_lome.png'
    }}
)

if not created:
    post.content = content
    post.featured_image = 'blog/posts/2026/05/featured_lome.png'
    post.status = 'PUBLISHED'
    post.save()

post.tags.add(tag1, tag2)
print(f"Article '{{title}}' created successfully!")
"""
        with open("remote_create_post.py", "w", encoding="utf-8") as f:
            f.write(script_code)
            
        print("Uploading creation script...")
        sftp.put("remote_create_post.py", "/app/remote_create_post.py")
        
        print("Executing script on server...")
        stdin, stdout, stderr = ssh.exec_command("cd /app && docker compose exec -T web python remote_create_post.py")
        print(stdout.read().decode('utf-8', 'replace'))
        print(stderr.read().decode('utf-8', 'replace'))
        
        sftp.close()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    deploy_article()
