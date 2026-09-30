<script setup lang="ts">
import { useI18n } from 'vue-i18n';
import { RouterView } from 'vue-router';

const { locale } = useI18n();
</script>

<template>
  <main>
    <label for="language">Language / Idioma</label>
    <select id="language" v-model="locale">
      <option value="en">English</option>
      <option value="es">Español</option>
    </select>
    <RouterView />
  </main>
</template>
