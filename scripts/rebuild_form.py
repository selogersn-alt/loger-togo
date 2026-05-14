import pathlib

SRC = pathlib.Path(r'd:\HDIGITAL\ANDROID_ANTIGRAVITY\LOGERTOGO\templates\property_form.html')

with open(SRC, 'r', encoding='utf-8') as f:
    content = f.read()

START_MARKER = '{% block content %}'
END_MARKER = '{% endblock %}'

start = content.find(START_MARKER)
end   = content.find(END_MARKER, start) + len(END_MARKER)

new_html = """\
{% block content %}
<div class="form-page-bg">
<div class="container" style="max-width:900px;">

  <div class="text-center mb-4">
    <span class="badge px-3 py-2 rounded-pill mb-2" style="background:rgba(11,70,41,.1);color:#0b4629;border:1px solid #28a745;">{% trans "Espace Bailleur" %}</span>
    <h1 class="fw-black" style="color:#0b4629;font-size:2rem;">{% if is_edit %}{% trans "Modifier l'annonce" %}{% else %}{% trans "Publier un bien" %}{% endif %}</h1>
    <p class="text-muted">{% trans "Remplissez les 4 étapes. Votre annonce sera vérifiée avant publication." %}</p>
  </div>

  <div class="steps-bar mb-4">
    <div class="step-item active" id="si-1"><div class="step-circle">1</div><div class="step-label">{% trans "Infos" %}</div></div>
    <div class="step-line" id="sl-1"></div>
    <div class="step-item" id="si-2"><div class="step-circle">2</div><div class="step-label">{% trans "Localisation" %}</div></div>
    <div class="step-line" id="sl-2"></div>
    <div class="step-item" id="si-3"><div class="step-circle">3</div><div class="step-label">{% trans "Détails" %}</div></div>
    <div class="step-line" id="sl-3"></div>
    <div class="step-item" id="si-4"><div class="step-circle">4</div><div class="step-label">{% trans "Photos" %}</div></div>
  </div>

  <form method="POST" enctype="multipart/form-data" id="property-form">
    {% csrf_token %}

    {% if form.errors %}
    <div class="alert alert-danger rounded-4 mb-4">
      <strong>⚠️ {% trans "Corrigez les erreurs :" %}</strong>
      <ul class="mb-0 mt-2">{% for f,errs in form.errors.items %}{% for e in errs %}<li>{{ e }}</li>{% endfor %}{% endfor %}</ul>
    </div>
    {% endif %}

    <!-- STEP 1 : INFOS GÉNÉRALES -->
    <div class="form-wizard-card mb-3 step-panel active" id="step-1">
      <div class="step-header">
        <h3><i class="fa-solid fa-file-lines me-2"></i>{% trans "Informations Générales" %}</h3>
        <p>{% trans "Titre, catégorie, prix et type de bien." %}</p>
      </div>
      <div class="step-body">
        <div class="row g-4">
          <div class="col-12">
            <label class="form-label">{{ form.title.label }}</label>
            {{ form.title }}
          </div>
          <div class="col-md-6">
            <label class="form-label">{{ form.listing_category.label }}</label>
            {{ form.listing_category }}
          </div>
          <div class="col-md-6">
            <label class="form-label" id="price_label">{{ form.price.label }}</label>
            <div class="input-group">{{ form.price }}<span class="input-group-text fw-bold" style="background:#28a745;color:white;border:none;border-radius:0 12px 12px 0;">FCFA</span></div>
          </div>
          {% with cat=form.listing_category.value %}
          <div class="col-md-6" id="price_per_night_container" style="display:{% if cat == 'FURNISHED' %}block{% else %}none{% endif %};">
            <label class="form-label">{{ form.price_per_night.label }}</label>
            <div class="input-group">{{ form.price_per_night }}<span class="input-group-text fw-bold" style="background:#f5c42f;color:#0b4629;border:none;border-radius:0 12px 12px 0;">/Nuit</span></div>
          </div>
          {% endwith %}
          <div class="col-md-6">
            <label class="form-label"><i class="fa-solid fa-tag me-1 text-success"></i>{{ form.discount_percentage.label }}</label>
            <div class="input-group">{{ form.discount_percentage }}<span class="input-group-text" style="background:#28a745;color:white;border:none;border-radius:0 12px 12px 0;">%</span></div>
          </div>
          <div class="col-md-6">
            <label class="form-label text-muted">{{ form.discount_price.label }}</label>
            {{ form.discount_price }}
            <small class="text-muted">{% trans "Calculé automatiquement." %}</small>
          </div>
          <div class="col-md-6">
            <label class="form-label">{{ form.property_type.label }}</label>
            {{ form.property_type }}
          </div>
          {% with cat=form.listing_category.value %}
          <div class="col-md-6" id="document_type_container" style="display:{% if cat == 'SALE' %}block{% else %}none{% endif %};">
            <label class="form-label">{{ form.document_type.label }} <span class="text-danger">*</span></label>
            {{ form.document_type }}
          </div>
          {% endwith %}
          {% with cat=form.listing_category.value %}
          <div class="col-12" id="rental_conditions_container" style="display:{% if cat == 'RENT' %}block{% else %}none{% endif %};">
            <div class="p-4 rounded-4" style="background:#f0f9f4;border:1px solid #c3e6cb;">
              <h6 class="fw-bold mb-3" style="color:#0b4629;"><i class="fa-solid fa-file-contract me-2"></i>{% trans "Conditions de Location" %}</h6>
              <div class="row g-3">
                <div class="col-md-4"><label class="form-label">{{ form.deposit_months.label }}</label>{{ form.deposit_months }}</div>
                <div class="col-md-4"><label class="form-label">{{ form.advance_months.label }}</label>{{ form.advance_months }}</div>
                <div class="col-md-4"><label class="form-label">{{ form.agency_fee_months.label }}</label>{{ form.agency_fee_months }}</div>
              </div>
            </div>
          </div>
          {% endwith %}
          <div class="col-md-6">
            <label class="form-label">{{ form.visit_fee.label }}</label>
            <div class="input-group">{{ form.visit_fee }}<span class="input-group-text" style="background:#0b4629;color:white;border:none;border-radius:0 12px 12px 0;">CFA</span></div>
          </div>
          <div class="col-12">
            <label class="form-label">{{ form.description.label }}</label>
            {{ form.description }}
          </div>
        </div>
        <div class="d-flex justify-content-end mt-4">
          <button type="button" class="btn-step-next" onclick="goStep(2)">{% trans "Suivant" %} <i class="fa-solid fa-arrow-right ms-2"></i></button>
        </div>
      </div>
    </div>

    <!-- STEP 2 : LOCALISATION GPS -->
    <div class="form-wizard-card mb-3 step-panel" id="step-2">
      <div class="step-header">
        <h3><i class="fa-solid fa-map-location-dot me-2"></i>{% trans "Localisation GPS" %}</h3>
        <p>{% trans "Placez votre bien sur la carte avec précision." %}</p>
      </div>
      <div class="step-body">
        <div class="row g-4 mb-4">
          <div class="col-md-6">
            <label class="form-label">{{ form.city.label }}</label>
            {{ form.city }}
          </div>
          <div class="col-md-6">
            <label class="form-label">{{ form.neighborhood.label }}</label>
            {{ form.neighborhood }}
            <datalist id="neighborhoods-list">{% for n in togo_neighborhoods %}<option value="{{ n }}">{% endfor %}</datalist>
          </div>
        </div>
        <div class="map-section">
          <div class="map-toolbar">
            <div>
              <h6><i class="fa-solid fa-crosshairs me-2"></i>{% trans "Carte Interactive" %}</h6>
              <small>{% trans "Cliquez ou glissez le marqueur." %}</small>
            </div>
            <div class="d-flex gap-2 flex-wrap">
              <button type="button" class="btn btn-sm btn-light rounded-pill px-3 fw-bold" onclick="geocodeAddr()"><i class="fa-solid fa-magnifying-glass-location me-1"></i>{% trans "Localiser" %}</button>
              <button type="button" class="btn btn-sm btn-warning rounded-pill px-3 fw-bold" onclick="useGPS()"><i class="fa-solid fa-location-dot me-1"></i>{% trans "Ma position" %}</button>
            </div>
          </div>
          <div id="form-map"></div>
          <div class="map-status-bar" id="form-map-status"></div>
          <div class="coord-row">
            <span>LAT :</span> <strong id="coord-lat-display">--</strong>
            <span class="ms-3">LNG :</span> <strong id="coord-lng-display">--</strong>
          </div>
        </div>
        <input type="hidden" name="latitude" id="id_latitude" value="{{ form.latitude.value|default:'' }}">
        <input type="hidden" name="longitude" id="id_longitude" value="{{ form.longitude.value|default:'' }}">
        <div class="d-flex justify-content-between mt-4">
          <button type="button" class="btn-step-prev" onclick="goStep(1)"><i class="fa-solid fa-arrow-left me-2"></i>{% trans "Retour" %}</button>
          <button type="button" class="btn-step-next" onclick="goStep(3)">{% trans "Suivant" %} <i class="fa-solid fa-arrow-right ms-2"></i></button>
        </div>
      </div>
    </div>

    <!-- STEP 3 : DÉTAILS TECHNIQUES -->
    <div class="form-wizard-card mb-3 step-panel" id="step-3">
      <div class="step-header">
        <h3><i class="fa-solid fa-ruler-combined me-2"></i>{% trans "Détails Techniques" %}</h3>
        <p>{% trans "Surface, pièces et équipements." %}</p>
      </div>
      <div class="step-body">
        <div class="row g-3 mb-4" id="technical-fields">
          <div class="col-6 col-md-3"><label class="form-label">{% trans "Surface (m²)" %}</label>{{ form.surface }}</div>
          <div class="col-6 col-md-3"><label class="form-label">{% trans "Chambres" %}</label>{{ form.bedrooms }}</div>
          <div class="col-6 col-md-3"><label class="form-label">{% trans "Toilettes" %}</label>{{ form.toilets }}</div>
          <div class="col-6 col-md-3"><label class="form-label">{% trans "Salons" %}</label>{{ form.salons }}</div>
          <div class="col-6 col-md-3"><label class="form-label">{% trans "Cuisines" %}</label>{{ form.kitchens }}</div>
          <div class="col-6 col-md-3"><label class="form-label">{% trans "Total pièces" %}</label>{{ form.total_rooms }}</div>
          <div class="col-6 col-md-3"><label class="form-label">{% trans "Ménages" %}</label>{{ form.households }}</div>
          <div class="col-6 col-md-3"><label class="form-label">{% trans "Étage" %}</label>{{ form.floor_level }}</div>
        </div>
        <h6 class="fw-bold mb-3" style="color:#0b4629;"><i class="fa-solid fa-check-double me-2"></i>{% trans "Caractéristiques" %}</h6>
        <div class="row g-2 mb-4">
          <div class="col-6 col-md-4"><label class="equip-chip">{{ form.has_balcony }}<i class="fa-solid fa-building"></i>{{ form.has_balcony.label }}</label></div>
          <div class="col-6 col-md-4"><label class="equip-chip">{{ form.has_terrace }}<i class="fa-solid fa-umbrella-beach"></i>{{ form.has_terrace.label }}</label></div>
          <div class="col-6 col-md-4"><label class="equip-chip">{{ form.has_courtyard }}<i class="fa-solid fa-tree"></i>{{ form.has_courtyard.label }}</label></div>
          <div class="col-6 col-md-4"><label class="equip-chip">{{ form.has_garden }}<i class="fa-solid fa-seedling"></i>{{ form.has_garden.label }}</label></div>
          <div class="col-6 col-md-4"><label class="equip-chip">{{ form.has_garage }}<i class="fa-solid fa-car"></i>{{ form.has_garage.label }}</label></div>
        </div>
        <h6 class="fw-bold mb-3" style="color:#0b4629;"><i class="fa-solid fa-plug me-2"></i>{% trans "Équipements" %}</h6>
        <div class="row g-2">
          <div class="col-6 col-md-4"><label class="equip-chip">{{ form.wifi }}<i class="fa-solid fa-wifi"></i>{{ form.wifi.label }}</label></div>
          <div class="col-6 col-md-4"><label class="equip-chip">{{ form.air_conditioning }}<i class="fa-solid fa-snowflake"></i>{{ form.air_conditioning.label }}</label></div>
          <div class="col-6 col-md-4"><label class="equip-chip">{{ form.swimming_pool }}<i class="fa-solid fa-water-ladder"></i>{{ form.swimming_pool.label }}</label></div>
          <div class="col-6 col-md-4"><label class="equip-chip">{{ form.gym }}<i class="fa-solid fa-dumbbell"></i>{{ form.gym.label }}</label></div>
          <div class="col-6 col-md-4"><label class="equip-chip">{{ form.refrigerator }}<i class="fa-solid fa-box"></i>{{ form.refrigerator.label }}</label></div>
          <div class="col-6 col-md-4"><label class="equip-chip">{{ form.washing_machine }}<i class="fa-solid fa-rotate"></i>{{ form.washing_machine.label }}</label></div>
          <div class="col-6 col-md-4"><label class="equip-chip">{{ form.microwave }}<i class="fa-solid fa-fire-burner"></i>{{ form.microwave.label }}</label></div>
          <div class="col-6 col-md-4"><label class="equip-chip">{{ form.tv_cable }}<i class="fa-solid fa-tv"></i>{{ form.tv_cable.label }}</label></div>
          <div class="col-6 col-md-4"><label class="equip-chip">{{ form.generator }}<i class="fa-solid fa-bolt"></i>{{ form.generator.label }}</label></div>
          <div class="col-6 col-md-4"><label class="equip-chip">{{ form.water_tank }}<i class="fa-solid fa-droplet"></i>{{ form.water_tank.label }}</label></div>
        </div>
        <div class="d-flex justify-content-between mt-4">
          <button type="button" class="btn-step-prev" onclick="goStep(2)"><i class="fa-solid fa-arrow-left me-2"></i>{% trans "Retour" %}</button>
          <button type="button" class="btn-step-next" onclick="goStep(4)">{% trans "Suivant" %} <i class="fa-solid fa-arrow-right ms-2"></i></button>
        </div>
      </div>
    </div>

    <!-- STEP 4 : PHOTOS + SUBMIT -->
    <div class="form-wizard-card mb-3 step-panel" id="step-4">
      <div class="step-header">
        <h3><i class="fa-solid fa-camera me-2"></i>{% trans "Photos & Publication" %}</h3>
        <p>{% trans "Ajoutez vos photos et publiez votre annonce." %}</p>
      </div>
      <div class="step-body">
        {% if is_edit and property.images.all %}
        <div class="p-3 rounded-4 border mb-4" style="background:#f8f9fa;">
          <label class="form-label fw-bold text-muted mb-2">{% trans "Photos en ligne" %}</label>
          <div class="d-flex flex-wrap gap-2">
            {% for img in property.images.all %}
            <div class="position-relative" style="width:80px;">
              <img src="{{ img.image_url.url }}" class="rounded-3" style="width:80px;height:80px;object-fit:cover;">
              <a href="{% url 'delete_property_image' img.id %}" class="btn btn-danger btn-sm position-absolute top-0 end-0 p-0 d-flex align-items-center justify-content-center" style="width:22px;height:22px;border-radius:50%;border:2px solid white;transform:translate(30%,-30%);" onclick="return confirm('Supprimer ?')"><i class="fa-solid fa-xmark" style="font-size:10px;"></i></a>
            </div>
            {% endfor %}
          </div>
        </div>
        {% endif %}
        <div class="upload-zone" id="drop-zone" onclick="document.getElementById('image-input').click()">
          <input type="file" id="image-input" multiple accept="image/*" class="d-none">
          <i class="fa-solid fa-cloud-arrow-up fa-3x text-success mb-3"></i>
          <h5 class="fw-bold">{% trans "Glissez vos photos ici" %}</h5>
          <p class="text-muted small">{% trans "JPG, PNG, WEBP — Compression automatique activée" %}</p>
          <span class="btn btn-sm btn-success rounded-pill px-4">{% trans "Parcourir" %}</span>
        </div>
        <div class="preview-grid" id="preview-container"></div>
        <div class="d-none">{{ form.images }}</div>
        <div class="p-4 rounded-4 mt-4" style="background:#f0f9f4;border:1px solid #c3e6cb;">
          <h6 class="fw-bold mb-3" style="color:#0b4629;"><i class="fa-solid fa-user-shield me-2"></i>{% trans "Infos Internes (Privées)" %}</h6>
          <div class="row g-3">
            <div class="col-md-6"><label class="form-label">{% trans "Référence source" %}</label><input type="text" name="internal_ref" class="form-control" placeholder="{% trans "Lien source" %}"></div>
            <div class="col-md-6"><label class="form-label">{% trans "Contact agent" %}</label><textarea name="private_contact_info" class="form-control" rows="2" placeholder="{% trans "Nom / Tel" %}"></textarea></div>
          </div>
        </div>
        <div class="d-flex justify-content-between mt-4">
          <button type="button" class="btn-step-prev" onclick="goStep(3)"><i class="fa-solid fa-arrow-left me-2"></i>{% trans "Retour" %}</button>
          <button type="submit" id="submit-btn" class="btn-step-next">
            <i class="fa-solid fa-paper-plane me-2"></i>
            {% if is_edit %}{% trans "Enregistrer" %}{% else %}{% trans "Publier l'annonce" %}{% endif %}
          </button>
        </div>
      </div>
    </div>

  </form>
</div>
</div>

<div id="upload-overlay">
  <div class="loading-card">
    <div class="spinner-ring"></div>
    <h3 class="fw-bold mb-2">{% trans "Optimisation en cours" %}</h3>
    <p id="upload-status-text" class="small opacity-75">{% trans "Compression de vos photos..." %}</p>
    <div class="progress-track"><div id="upload-progress-bar" class="progress-fill"></div></div>
    <div class="d-flex justify-content-between" style="font-size:.75rem;opacity:.6;">
      <span>{% trans "Traitement sécurisé" %}</span><span id="progress-percentage">0%</span>
    </div>
  </div>
</div>

{% endblock %}"""

result = content[:start] + new_html + content[end:]
with open(SRC, 'w', encoding='utf-8') as f:
    f.write(result)
print('DONE', SRC.stat().st_size, 'bytes')
