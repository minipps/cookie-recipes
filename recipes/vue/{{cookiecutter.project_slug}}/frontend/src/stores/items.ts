import { defineStore } from 'pinia';
import { ref } from 'vue';

interface Item {
  id: number;
  name: string;
}

export const useItems = defineStore('items', () => {
  const item = ref<Item | null>(null);
{% if cookiecutter._backend %}  const saving = ref(false);
  const failed = ref(false);

  async function create(name: string) {
    saving.value = true;
    failed.value = false;
    try {
      const response = await fetch('/api/v1/items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      item.value = (await response.json()) as Item;
    } catch {
      failed.value = true;
    } finally {
      saving.value = false;
    }
  }

  return { item, saving, failed, create };
{% else %}
  function create(name: string) {
    item.value = { id: (item.value?.id ?? 0) + 1, name: name.trim() };
  }

  return { item, create };
{% endif %}});
