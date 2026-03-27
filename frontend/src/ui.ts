import type { Bean, Cafe } from "./types.ts";

function createSensoryBar(label: string, value: number | null): string {
  if (!value) return "";
  let dots = "";
  for (let i = 1; i <= 5; i++) {
    dots += `<div class="w-3 h-1 rounded-full ${i <= value ? "bg-primary" : "bg-outline-variant"}"></div>`;
  }
  return `
    <div class="text-center px-4 border-r border-outline-variant/20 last:border-r-0">
      <p class="text-[10px] uppercase font-bold mb-1">${label}</p>
      <div class="flex gap-0.5">${dots}</div>
    </div>
  `;
}

function renderGrainItem(bean: Bean, cafeId: number, idx: number): string {
  const id = `grain-${cafeId}-${bean.id}`;
  const hasSensory = bean.acidity || bean.sweetness || bean.body;
  const tastingNotes = bean.tasting_notes ? bean.tasting_notes.join(", ") : null;
  const altitude = bean.altitude ? `${bean.altitude}m` : null;
  const hasDetails = tastingNotes || bean.variety || bean.roast_level || hasSensory;

  return `
    <div class="group border border-outline-variant/15 rounded-xl p-5 hover:bg-surface-container-low transition-all ${hasDetails ? "cursor-pointer" : ""}"
         ${hasDetails ? `onclick="toggleGrain('${id}')"` : ""}>

      <div class="flex justify-between items-center">
        <div class="flex items-center gap-4">
          <div class="w-12 h-12 rounded-lg bg-surface-container overflow-hidden flex items-center justify-center flex-shrink-0">
            <i data-lucide="coffee" class="w-5 h-5 text-on-surface-variant"></i>
          </div>
          <div>
            <p class="font-bold text-primary text-sm">${bean.name}</p>
            <p class="text-xs text-on-surface-variant uppercase">
              ${[bean.roaster_name, bean.processing, altitude].filter(Boolean).join(" · ") || "Detalhes não disponíveis"}
            </p>
          </div>
        </div>
        ${
          hasDetails
            ? `
          <i data-lucide="chevron-down" id="chevron-${id}"
             class="chevron-icon w-5 h-5 text-outline-variant group-hover:text-primary transition-colors flex-shrink-0 ${idx === 0 ? "rotated" : ""}"></i>
        `
            : ""
        }
      </div>

      ${
        hasDetails
          ? `
        <div id="content-${id}" class="grain-content ${idx === 0 ? "expanded" : ""}">
          <div class="mt-6 pt-6 border-t border-outline-variant/10 grid grid-cols-2 md:grid-cols-3 gap-y-6 gap-x-4">
            ${tastingNotes ? `
              <div>
                <p class="text-[10px] uppercase tracking-widest text-on-surface-variant mb-1">Notas de Sabor</p>
                <p class="text-sm font-medium text-on-surface">${tastingNotes}</p>
              </div>
            ` : ""}
            ${bean.variety ? `
              <div>
                <p class="text-[10px] uppercase tracking-widest text-on-surface-variant mb-1">Variedade</p>
                <p class="text-sm font-medium text-on-surface">${bean.variety}</p>
              </div>
            ` : ""}
            ${bean.roast_level ? `
              <div>
                <p class="text-[10px] uppercase tracking-widest text-on-surface-variant mb-1">Torra</p>
                <p class="text-sm font-medium text-on-surface">${bean.roast_level}</p>
              </div>
            ` : ""}
            ${hasSensory ? `
              <div class="col-span-full bg-surface-container-high/40 p-3 rounded-lg flex justify-between">
                ${createSensoryBar("Acidez", bean.acidity)}
                ${createSensoryBar("Doçura", bean.sweetness)}
                ${createSensoryBar("Corpo", bean.body)}
              </div>
            ` : ""}
          </div>
        </div>
      `
          : ""
      }
    </div>
  `;
}

function renderVenueCard(venue: Cafe): string {
  const beans = venue.matching_beans || [];
  const beansHTML =
    beans.length > 0
      ? `
      <h4 class="text-xs font-bold text-primary mb-4 uppercase tracking-tighter">
        Grãos Disponíveis
      </h4>
      <div class="space-y-4">
        ${beans.map((bean, idx) => renderGrainItem(bean, venue.id, idx)).join("")}
      </div>
    `
      : `<p class="text-sm text-on-surface-variant italic text-center py-6">Nenhum grão inventariado no momento.</p>`;

  return `
    <div class="bg-surface-container-low rounded-xl p-1 transition-all">
      <div class="bg-surface-container-lowest rounded-lg p-8 h-full flex flex-col">

        <div class="flex justify-between items-start mb-6">
          <div>
            <span class="text-xs font-bold tracking-widest uppercase text-on-surface-variant mb-2 block">
              ${venue.location || "Localização não informada"}
            </span>
            <h3 class="font-headline text-3xl text-primary mb-1">${venue.name}</h3>
          </div>
          <div class="bg-secondary-container p-3 rounded-lg text-on-secondary-container flex-shrink-0">
            <i data-lucide="coffee" class="w-6 h-6"></i>
          </div>
        </div>

        <div class="mt-auto">
          ${beansHTML}
        </div>

      </div>
    </div>
  `;
}

export function renderResults(venues: Cafe[]): void {
  const countEl = document.getElementById("results-count");
  if (countEl) {
    countEl.textContent = `${venues.length} ${venues.length === 1 ? "encontrado" : "encontrados"}`;
  }

  const list = document.getElementById("results-list");
  if (!list) return;

  if (venues.length === 0) {
    list.innerHTML = `
      <div class="col-span-full py-16 text-center">
        <div class="bg-surface-container rounded-full w-20 h-20 flex items-center justify-center mx-auto mb-4">
          <i data-lucide="coffee" class="w-10 h-10 text-on-surface-variant"></i>
        </div>
        <h3 class="text-xl font-headline text-primary mb-2">Nenhum café encontrado</h3>
        <p class="text-on-surface-variant">Tente ajustar seus filtros ou termo de busca.</p>
      </div>
    `;
    lucide.createIcons();
    return;
  }

  list.innerHTML = venues.map(renderVenueCard).join("");
  lucide.createIcons();
}

export function showLoadingState(isFirstLoad: boolean): void {
  const list = document.getElementById("results-list");
  if (!list) return;

  if (isFirstLoad) {
    list.innerHTML = `
      <div class="col-span-full flex flex-col items-center py-16 gap-4">
        <div class="relative flex flex-col items-center">
          <span class="material-symbols-outlined text-4xl text-primary" style="visibility:visible">coffee_maker</span>
          <div class="w-0.5 bg-secondary/40 animate-drip my-1"></div>
          <span class="material-symbols-outlined text-2xl text-primary" style="visibility:visible">local_cafe</span>
        </div>
        <p class="text-on-surface-variant font-medium">Buscando o melhor café para você...</p>
      </div>
    `;
  } else {
    const skeletonCard = `
      <div class="bg-surface-container-lowest p-8 rounded-xl shadow-sm space-y-4">
        <div class="flex justify-between items-start">
          <div class="space-y-2 flex-1">
            <div class="h-6 w-3/4 bg-surface-container-high rounded skeleton-shimmer"></div>
            <div class="h-4 w-1/2 bg-surface-container-high rounded skeleton-shimmer"></div>
          </div>
          <div class="h-6 w-16 bg-surface-container-high rounded-full skeleton-shimmer ml-4"></div>
        </div>
        <div class="h-24 bg-surface-container-high rounded-lg skeleton-shimmer"></div>
        <div class="flex gap-2">
          <div class="h-4 w-16 bg-surface-container-high rounded skeleton-shimmer"></div>
          <div class="h-4 w-16 bg-surface-container-high rounded skeleton-shimmer"></div>
        </div>
      </div>
    `;
    list.innerHTML = skeletonCard + skeletonCard;
  }
}

export function showErrorState(): void {
  const list = document.getElementById("results-list");
  if (!list) return;
  list.innerHTML = `
    <div class="col-span-full py-12 text-center bg-surface-container-low rounded-2xl border border-outline-variant/20">
      <i data-lucide="alert-circle" class="w-10 h-10 text-error mx-auto mb-3"></i>
      <h3 class="text-lg font-medium text-on-surface">Erro ao carregar dados</h3>
      <p class="text-on-surface-variant mt-1 text-sm">O servidor backend está rodando?</p>
    </div>
  `;
  lucide.createIcons();
}
