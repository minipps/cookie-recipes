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
        empty: 'Create an item to test the API connection.',
        saved: 'Saved item #{id}: {name}',
        error: 'Could not save the item. Please try again.',
      },
      es: {
        title: 'Elementos',
        name: 'Nombre del elemento',
        create: 'Crear elemento',
        saving: 'Guardando…',
        empty: 'Crea un elemento para probar la conexión con la API.',
        saved: 'Elemento guardado #{id}: {name}',
        error: 'No se pudo guardar el elemento. Inténtalo de nuevo.',
      },
    },
  });
}
