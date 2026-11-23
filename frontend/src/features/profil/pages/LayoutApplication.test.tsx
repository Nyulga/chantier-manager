// Tests du cadre commun : barre latérale (logo, navigation, profil) et contenu de la page.
import { useMutation } from '@tanstack/react-query';
import { fireEvent, screen, within } from '@testing-library/react';
import { http, HttpResponse } from 'msw';
import { Route, Routes } from 'react-router';
import { afterEach, expect, it } from 'vitest';

import { afficherAvecFournisseurs } from '@/test/afficherAvecFournisseurs';
import { installerServeurApi } from '@/test/serveurApiSimule';
import { Alerte, Bouton } from '@/ui';
import { verifierAccessibilite } from '@/test/verifierAccessibilite';

import { LayoutApplication } from './LayoutApplication';

const serveur = installerServeurApi();

afterEach(() => {
  localStorage.clear();
});

function afficherLayout(adresse = '/') {
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([{ id: 'un' }, { id: 'deux' }])));
  return afficherAvecFournisseurs(
    <Routes>
      <Route element={<LayoutApplication />}>
        <Route index element={<p>Contenu de la page</p>} />
        <Route path="chantiers" element={<p>Contenu des chantiers</p>} />
      </Route>
    </Routes>,
    adresse,
  );
}

it('affiche le logo, le sélecteur de profil dans la barre latérale et la page dans la zone principale', () => {
  afficherLayout();

  expect(screen.getByText('Chantier Manager')).toBeVisible();
  expect(screen.getByRole('radio', { name: 'Chef' })).toBeChecked();
  expect(screen.getByRole('main')).toHaveTextContent('Contenu de la page');
});

it('propose la navigation principale, avec le tableau de bord pour page courante', async () => {
  afficherLayout();

  const navigation = screen.getByRole('navigation', { name: 'Navigation principale' });
  expect(within(navigation).getByRole('link', { name: 'Tableau de bord' })).toHaveAttribute(
    'aria-current',
    'page',
  );
  expect(await within(navigation).findByRole('link', { name: 'Mes chantiers 2' })).toHaveAttribute(
    'href',
    '/chantiers',
  );
});

it('marque « Mes chantiers » comme page courante sur la liste des chantiers', async () => {
  afficherLayout('/chantiers');

  expect(await screen.findByRole('link', { name: 'Mes chantiers 2' })).toHaveAttribute(
    'aria-current',
    'page',
  );
});

it('affiche « Équipe » et « Inviter un utilisateur » désactivés, avec la mention « Bientôt »', () => {
  afficherLayout();

  expect(screen.queryByRole('link', { name: /Équipe/ })).not.toBeInTheDocument();
  expect(screen.queryByRole('link', { name: /Inviter/ })).not.toBeInTheDocument();
  expect(screen.getByText('Équipe')).toBeVisible();
  expect(screen.getByText('Inviter un utilisateur')).toBeVisible();
  expect(screen.getAllByText('Bientôt')).toHaveLength(2);
});

it("ne montre pas de compteur tant que la liste n'est pas chargée", () => {
  afficherLayout();

  expect(screen.getByRole('link', { name: 'Mes chantiers' })).toBeVisible();
});

it("change de profil quand l'utilisateur choisit Ouvrier", () => {
  afficherLayout();

  fireEvent.click(screen.getByRole('radio', { name: 'Ouvrier' }));

  expect(screen.getByRole('radio', { name: 'Ouvrier' })).toBeChecked();
  expect(localStorage.getItem('chantier-manager.profil')).toBe('ouvrier');
});

/** Page de test dont l'action échoue toujours : elle garde l'alerte de sa mutation à l'écran. */
function PageQuiEchoue() {
  const action = useMutation({
    mutationFn: () => Promise.reject(new Error('Impossible de valider cette étape.')),
  });

  return (
    <>
      <Bouton
        onClick={() => {
          action.mutate();
        }}
      >
        Valider
      </Bouton>
      {action.isError && <Alerte>{action.error.message}</Alerte>}
    </>
  );
}

it("efface l'alerte d'une action ratée quand l'utilisateur change de profil", async () => {
  serveur.use(http.get('/api/chantiers', () => HttpResponse.json([])));
  afficherAvecFournisseurs(
    <Routes>
      <Route element={<LayoutApplication />}>
        <Route index element={<PageQuiEchoue />} />
      </Route>
    </Routes>,
  );
  fireEvent.click(screen.getByRole('button', { name: 'Valider' }));
  expect(await screen.findByRole('alert')).toHaveTextContent('Impossible de valider cette étape.');

  fireEvent.click(screen.getByRole('radio', { name: 'Ouvrier' }));

  expect(screen.queryByRole('alert')).not.toBeInTheDocument();
});

it("n'a aucun défaut d'accessibilité détectable par axe", async () => {
  const { container } = afficherLayout();
  await screen.findByRole('link', { name: 'Mes chantiers 2' });

  await verifierAccessibilite(container);
});
