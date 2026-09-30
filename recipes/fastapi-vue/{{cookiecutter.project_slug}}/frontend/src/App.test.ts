import { createPinia } from 'pinia';
import { createApp, nextTick } from 'vue';
import { createMemoryHistory } from 'vue-router';
import { expect, test, vi } from 'vitest';
import App from './App.vue';
import { makeI18n } from './i18n';
import { makeRouter } from './router';

test('creates an API item, switches language, and reports a failed request', async () => {
  const fetchMock = vi.fn().mockResolvedValue(Response.json({ id: 1, name: 'Example' }));
  vi.stubGlobal('fetch', fetchMock);
  const router = makeRouter(createMemoryHistory());
  await router.push('/');
  await router.isReady();
  const host = document.createElement('div');
  document.body.append(host);
  const app = createApp(App).use(createPinia()).use(makeI18n()).use(router);
  app.mount(host);
  try {
    const input = host.querySelector<HTMLInputElement>('#name')!;
    input.value = 'Example';
    input.dispatchEvent(new Event('input'));
    await nextTick();
    host.querySelector('form')!.dispatchEvent(new Event('submit', { cancelable: true }));
    await vi.waitFor(() =>
      expect(host.querySelector('[role="status"]')?.textContent).toBe('Saved item #1: Example'),
    );
    expect(fetchMock).toHaveBeenCalledWith('/api/v1/items', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name: 'Example' }),
    });

    const language = host.querySelector<HTMLSelectElement>('#language')!;
    language.value = 'es';
    language.dispatchEvent(new Event('change'));
    await nextTick();
    expect(host.querySelector('h1')?.textContent).toBe('Elementos');

    fetchMock.mockResolvedValue(new Response(null, { status: 500 }));
    host.querySelector('form')!.dispatchEvent(new Event('submit', { cancelable: true }));
    await vi.waitFor(() =>
      expect(host.querySelector('[role="alert"]')?.textContent).toBe(
        'No se pudo guardar el elemento. Inténtalo de nuevo.',
      ),
    );
    expect(host.querySelector('button')?.disabled).toBe(false);
  } finally {
    app.unmount();
    host.remove();
  }
});
