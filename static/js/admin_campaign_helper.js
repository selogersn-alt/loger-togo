document.addEventListener('DOMContentLoaded', function() {
    const templateSelect = document.querySelector('#id_template');
    const subjectInput = document.querySelector('#id_subject');
    const contentInput = document.querySelector('#id_content');

    if (templateSelect) {
        templateSelect.addEventListener('change', function() {
            const templateId = this.value;
            if (templateId) {
                fetch(`/admin/marketing/template/${templateId}/`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.subject) subjectInput.value = data.subject;
                        if (data.content) {
                            // Si vous utilisez un éditeur WYSIWYG type CKEditor, 
                            // il faudra peut-être une commande spécifique ici.
                            contentInput.value = data.content;
                        }
                    })
                    .catch(error => console.error('Erreur lors de la récupération du modèle:', error));
            }
        });
    }
});
