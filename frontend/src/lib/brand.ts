const LEGACY_DEMO_ORGANIZATION = 'ZohoFlow Enterprise';

export function getOrganizationDisplayName(name?: string | null): string {
  if (!name || name === LEGACY_DEMO_ORGANIZATION) {
    return 'NexusCRM Enterprise';
  }

  return name;
}
