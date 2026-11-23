// Fixture conforme : un test peut importer un type de l'API (preuve de correspondance de types).
import type { client } from '@/api/client';

export type TypeDuClient = typeof client;
