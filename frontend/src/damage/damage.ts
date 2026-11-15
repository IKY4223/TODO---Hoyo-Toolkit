import { isArrayOf, isNumber, isRecord, postJson } from '../api/http'
import type { components } from '../api/schema'

export type Damage = components['schemas']['Damage']
export type DamageRequest = components['schemas']['DamageRequest']

const DAMAGE_URL = '/api/damage'

const isDamage = (value: unknown): value is Damage =>
  isRecord(value) && isNumber(value.non_crit) && isNumber(value.crit) && isNumber(value.average)

export async function fetchDamage(request: DamageRequest): Promise<Damage> {
  return postJson(DAMAGE_URL, request, isDamage)
}

type Schemas = components['schemas']
export type ArtifactComparison = Schemas['ArtifactComparison']
export type ArtifactRequest = Schemas['ArtifactRequest']
type BaseStat = Schemas['BaseStat']
type Artifact = Schemas['Artifact']

/** An artifact another character in the showcase wears. */
export interface Candidate {
  readonly owner: string
  readonly artifact: Artifact
}

const isComparison = (value: unknown): value is ArtifactComparison =>
  isRecord(value) && isDamage(value.current) && isArrayOf(value.candidates, isDamage)

export const isBaseStat = (stat: {
  readonly key: string
  readonly value: number
}): stat is BaseStat => stat.key === 'hp' || stat.key === 'atk' || stat.key === 'def'

export async function fetchComparison(request: ArtifactRequest): Promise<ArtifactComparison> {
  return postJson(`${DAMAGE_URL}/artifacts`, request, isComparison)
}
