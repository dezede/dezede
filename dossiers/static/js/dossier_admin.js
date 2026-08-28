/* Shows or hides the kind-specific parts of the dossier admin form from the
 * ticked « types de données » checkboxes:
 * - each kind's « Sélection manuelle » fieldset (`.dossier-kind-<kind>`);
 * - the kind-specific rows of the shared « Sélection dynamique » fieldset
 *   (circonstance and saisons apply to events only, genres to works only,
 *   types_de_sources to sources only);
 * - the whole « Sélection dynamique » fieldset when no kind is ticked.
 */
(function () {
    'use strict';

    // Kind-specific criteria rows of the shared dynamic-selection fieldset.
    var KIND_FIELDS = {
        evenements: ['circonstance', 'saisons'],
        oeuvres: ['genres'],
        sources: ['types_de_sources'],
    };

    function fieldRow(name) {
        var field = document.getElementById('id_' + name);
        if (!field) {
            return null;
        }
        // Both the vanilla admin (.form-row) and grappelli (.grp-row) wrap
        // each field line in a row element.
        return field.closest('.grp-row, .form-row');
    }

    function setDisplayed(element, displayed) {
        if (element) {
            element.style.display = displayed ? '' : 'none';
        }
    }

    function update() {
        var checkboxes = document.querySelectorAll(
            'input[name="types_de_donnees"]');
        var anyKind = false;
        checkboxes.forEach(function (checkbox) {
            var kind = checkbox.value;
            anyKind = anyKind || checkbox.checked;
            document.querySelectorAll('.dossier-kind-' + kind).forEach(
                function (fieldset) {
                    setDisplayed(fieldset, checkbox.checked);
                });
            (KIND_FIELDS[kind] || []).forEach(function (name) {
                setDisplayed(fieldRow(name), checkbox.checked);
            });
        });
        document.querySelectorAll('.dossier-selection-dynamique').forEach(
            function (fieldset) {
                setDisplayed(fieldset, anyKind);
            });
    }

    document.addEventListener('DOMContentLoaded', function () {
        var checkboxes = document.querySelectorAll(
            'input[name="types_de_donnees"]');
        if (!checkboxes.length) {
            return;
        }
        checkboxes.forEach(function (checkbox) {
            checkbox.addEventListener('change', update);
        });
        update();
    });
})();
