<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useItems } from '../stores/items';

const { t } = useI18n();
const items = useItems();
const name = ref('');
</script>

{% raw %}<template>
  <h1>{{ t('title') }}</h1>
  <form @submit.prevent="items.create(name)">
    <label for="name">{{ t('name') }}</label>
{% endraw %}{% if cookiecutter._backend %}{% raw %}    <input id="name" v-model="name" required maxlength="200" :disabled="items.saving" />
    <button type="submit" :disabled="items.saving">
      {{ t(items.saving ? 'saving' : 'create') }}
    </button>
  </form>
  <p v-if="items.failed" role="alert">{{ t('error') }}</p>
  <p v-else-if="items.item" role="status">{{ t('saved', items.item) }}</p>
{% endraw %}{% else %}{% raw %}    <input id="name" v-model="name" required maxlength="200" />
    <button type="submit">{{ t('create') }}</button>
  </form>
  <p v-if="items.item" role="status">{{ t('saved', items.item) }}</p>
{% endraw %}{% endif %}{% raw %}
  <p v-else>{{ t('empty') }}</p>
</template>
{% endraw %}