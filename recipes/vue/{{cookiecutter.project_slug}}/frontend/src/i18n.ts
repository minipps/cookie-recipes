import { createI18n } from 'vue-i18n';

export function makeI18n() {
  return createI18n({
    legacy: false,
    locale: 'en',
    fallbackLocale: 'en',
    messages: {
      en: {
        title: 'Items',
        name: 'Item name',
        create: 'Create item',
        saving: 'Saving…',
{% if cookiecutter._backend %}        empty: 'Create an item to test the API connection.',
{% else %}        empty: 'Create an item. Items are kept in memory until you reload.',
{% endif %}
        saved: 'Saved item #{id}: {name}',
        error: 'Could not save the item. Please try again.',
      },
      es: {
        title: 'Elementos',
        name: 'Nombre del elemento',
        create: 'Crear elemento',
        saving: 'Guardando…',
{% if cookiecutter._backend %}        empty: 'Crea un elemento para probar la conexión con la API.',
{% else %}        empty: 'Crea un elemento. Los elementos se mantienen en memoria hasta recargar.',
{% endif %}
        saved: 'Elemento guardado #{id}: {name}',
        error: 'No se pudo guardar el elemento. Inténtalo de nuevo.',
      },
    },
  });
}
