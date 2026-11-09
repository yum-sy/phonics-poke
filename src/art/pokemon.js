import roster from './pokemon-roster.json' with { type: 'json' }

// Per-stage identity preserves the curriculum sound, even when a species returns.
export const POKEMON_CHARACTERS = Object.create(null)
const BASE = `${import.meta.env?.BASE_URL || '/'}art/pokemon/`
export function applyPokemonRoster(chapters) {
  return chapters.map(chapter => ({ ...chapter, stages: chapter.stages.map(stage => {
    const entry = roster.assignments[stage.id]
    if (!entry) throw new Error(`Missing Pokémon roster: ${stage.id}`)
    const characters = {}
    for (const role of ['hero', 'villain']) {
      const id = entry[role], art = `pokemon-${stage.id}-${role}`
      const asset = roster.assets[id]
      if (!asset) throw new Error(`Missing Pokémon asset: ${id}`)
      POKEMON_CHARACTERS[art] = { ...asset, speciesId: id,
        soundArt: stage[role].art, role: role === 'hero' ? entry.heroRole : 'villain' }
      characters[role] = { name: asset.name, art, style: 'pokemon' }
    }
    return { ...stage, ...characters }
  }) }))
}
const escape = text => text.replace(/[&<>"']/g, c => ({ '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;' }[c]))
export function renderPokemon(spec, { idle = false } = {}) {
  const asset = POKEMON_CHARACTERS[spec.art]
  if (!asset) return null
  const label = escape(asset.name)
  // A picture's reduced-motion source stops the GIF, not merely its CSS transform.
  const animation = idle && asset.idle
    ? `<picture class="pokemon-idle"><source media="(prefers-reduced-motion: reduce)" srcset="${BASE}${asset.static}"><img src="${BASE}${asset.idle}" alt="" width="256" height="256"></picture>` : ''
  return `<span class="carbot-art pokemon-art" data-pokemon-id="${asset.speciesId}" data-pokemon-role="${asset.role}" role="img" aria-label="${label}"><img class="pokemon-still" src="${BASE}${asset.static}" alt="" width="256" height="256">${animation}</span>`
}
