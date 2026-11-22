// Violation volontaire : un import d'openapi-fetch en dehors de src/api.
import createClient from 'openapi-fetch';

export const clientDirect = createClient({ baseUrl: '/api' });
