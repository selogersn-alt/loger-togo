from django.utils.translation import gettext_lazy as _

PROPERTY_TYPE_CHOICES = [
    ('UNE_PIECE', _('Une pièce')),
    ('CHAMBRE_SALON', _('Chambre salon')),
    ('DEUX_CHAMBRES_SALON', _('2 chambres salon')),
    ('TROIS_CHAMBRES_SALON', _('3 chambres salon')),
    ('STUDIO', _('Studio')),
    ('APPARTEMENT', _('Appartement')),
    ('CHAMBRE', _('Chambre')),
    ('IMMEUBLE', _('Immeuble')),
    ('TERRAIN', _('Terrain')),
    ('PARCELLES', _('Parcelles')),
    ('VILLA', _('Villa')),
    ('MAISON', _('Maison')),
    ('HOTEL', _('Hôtel')),
    ('AUBERGE', _('Auberge')),
    ('MUSEE', _('Musée')),
    ('BUSINESS', _('Espace Business / Bureau')),
]

CITY_CHOICES = [
    ('LOME', 'Lomé (Grand Lomé)'),
    ('KARA', 'Kara'),
    ('SOKODE', 'Sokodé'),
    ('ATAKPAME', 'Atakpamé'),
    ('KPALIME', 'Kpalimé'),
    ('TSEVIE', 'Tsévié'),
    ('ANEHO', 'Aného'),
    ('DAPAONG', 'Dapaong'),
    ('VOGAN', 'Vogan'),
    ('TABLIGBO', 'Tabligbo'),
    ('NOTSE', 'Notsé'),
    ('BADOU', 'Badou'),
    ('AMLAME', 'Amlamé'),
    ('KANDE', 'Kandé'),
    ('NIAMTOUGOU', 'Niamtougou'),
    ('BASSAR', 'Bassar'),
    ('BAFILO', 'Bafilo'),
    ('TCHAMBA', 'Tchamba'),
    ('SOTOUBOUA', 'Sotouboua'),
    ('BLITTA', 'Blitta'),
    ('MANGO', 'Mango'),
    ('SANGUERA', 'Sanguéra'),
    ('BAGUIDA', 'Baguida'),
]

AMENITIES_CHOICES = [
    ('WIFI', _('WiFi')),
    ('POOL', _('Piscine')),
    ('GYM', _('Salle de sport / Gym')),
    ('GARAGE', _('Garage / Parking')),
    ('AC', _('Climatisation')),
    ('SECURITY', _('Gardiennage / Sécurité')),
    ('GENERATOR', _('Groupe électrogène')),
    ('WATER_TANK', _('Réservoir d\'eau / Surpresseur')),
    ('TV_CABLE', _('TV par câble')),
    ('WASHING_MACHINE', _('Machine à laver')),
    ('DRYER', _('Sèche-linge')),
    ('MICROWAVE', _('Micro-ondes')),
    ('REFRIGERATOR', _('Réfrigérateur')),
    ('SAUNA', _('Sauna')),
    ('LAWN', _('Pelouse / Jardin')),
    ('OUTDOOR_SHOWER', _('Douche extérieure')),
    ('WINDOW_COVERINGS', _('Stores / Rideaux')),
]

COUNTRY_CHOICES = [
    ('TG', 'Togo'),
    ('BJ', 'Bénin'),
    ('CI', 'Côte d\'Ivoire'),
    ('BF', 'Burkina Faso'),
    ('NE', 'Niger'),
    ('GH', 'Ghana'),
    ('FR', 'France'),
    ('ML', 'Mali'),
    ('GN', 'Guinée'),
    ('MR', 'Mauritanie'),
    ('GM', 'Gambie'),
    ('CM', 'Cameroun'),
    ('GA', 'Gabon'),
    ('MA', 'Maroc'),
    ('TN', 'Tunisie'),
    ('US', 'États-Unis'),
    ('CA', 'Canada'),
    ('ES', 'Espagne'),
    ('IT', 'Italie'),
    ('OTHER', 'Autre'),
]

TOGO_NEIGHBORHOODS = [
    "Adidogomé", "Agoè", "Agoè-Assiyéyé", "Agoè-Logopé", "Amoutiévé", "Anfamé", "Avedji", "Baguida", "Be", "Bè-Kpota", 
    "Cassablanca", "Deckon", "Djidjole", "Dogbé", "Gbadago", "Hanoukopé", "Hedzranawoé", "Kanyikopé", "Kegue", "Kodjoviakopé", 
    "Lomé-Port", "Nyakonakpoé", "N'lessi", "Octaviano-Neto", "Tokoin", "Tokoin-Casablanca", "Tokoin-Forever", "Tokoin-Hopital", 
    "Tokoin-N'kafu", "Tokoin-Ouest", "Zongo", "Aflao", "Adamavo", "Adakpamé", "Ségbé", "Légbassito", "Vakpossito", "Totsi", 
    "Sanguéra", "Zanguéra", "Ablogamé", "Akodésséwa", "Katanga", "Kpéhénou", "Souza-Nétimé"
]


