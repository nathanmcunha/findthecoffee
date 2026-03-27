function setDropdownOpen(
  btn: HTMLElement,
  chevron: HTMLElement | null,
  open: boolean,
): void {
  if (open) {
    btn.classList.remove("rounded-md", "border-outline-variant/30", "hover:border-primary");
    btn.classList.add("rounded-t-md", "border-primary");
    chevron?.classList.add("rotate-180");
    chevron?.classList.remove("group-hover:translate-y-0.5");
  } else {
    btn.classList.remove("rounded-t-md", "border-primary");
    btn.classList.add("rounded-md", "border-outline-variant/30", "hover:border-primary");
    chevron?.classList.remove("rotate-180");
    chevron?.classList.add("group-hover:translate-y-0.5");
  }
}

function closeAllDropdowns(): void {
  (
    [
      ["roaster-dropdown-btn", "roaster-dropdown-panel", "roaster-chevron"],
      ["roast-dropdown-btn", "roast-dropdown-panel", "roast-chevron"],
    ] as [string, string, string][]
  ).forEach(([btnId, panelId, chevronId]) => {
    const panel = document.getElementById(panelId);
    if (panel && !panel.classList.contains("hidden")) {
      panel.classList.add("hidden");
      const btn = document.getElementById(btnId);
      const chevron = document.getElementById(chevronId);
      if (btn) setDropdownOpen(btn, chevron, false);
    }
  });
}

interface DropdownConfig {
  btnId: string;
  panelId: string;
  labelId: string;
  selectId: string;
  chevronId: string;
}

export function initCustomDropdowns(): void {
  const configs: DropdownConfig[] = [
    {
      btnId: "roaster-dropdown-btn",
      panelId: "roaster-dropdown-panel",
      labelId: "roaster-dropdown-label",
      selectId: "roaster-filter",
      chevronId: "roaster-chevron",
    },
    {
      btnId: "roast-dropdown-btn",
      panelId: "roast-dropdown-panel",
      labelId: "roast-dropdown-label",
      selectId: "roast-filter",
      chevronId: "roast-chevron",
    },
  ];

  configs.forEach(({ btnId, panelId, labelId, selectId, chevronId }) => {
    const btn = document.getElementById(btnId);
    const panel = document.getElementById(panelId);
    const label = document.getElementById(labelId);
    const select = document.getElementById(selectId) as HTMLSelectElement | null;
    const chevron = document.getElementById(chevronId);
    if (!btn || !panel) return;

    btn.addEventListener("click", (e) => {
      e.stopPropagation();
      const isOpen = !panel.classList.contains("hidden");
      closeAllDropdowns();
      if (!isOpen) {
        panel.classList.remove("hidden");
        setDropdownOpen(btn, chevron, true);
      }
    });

    panel.addEventListener("click", (e) => {
      const item = (e.target as HTMLElement).closest<HTMLElement>("[data-value]");
      if (!item) return;
      if (label) label.textContent = item.textContent?.trim() ?? "";
      if (select) {
        select.value = item.dataset["value"] ?? "";
        select.dispatchEvent(new Event("change"));
      }
      panel.classList.add("hidden");
      setDropdownOpen(btn, chevron, false);
    });
  });

  document.addEventListener("click", closeAllDropdowns);
}

export function populateRoasterDropdown(
  roasters: Array<{ id: number; name: string }>,
): void {
  const select = document.getElementById("roaster-filter") as HTMLSelectElement | null;
  const list = document.getElementById("roaster-dropdown-list");
  if (!select) return;

  while (select.options.length > 1) select.remove(1);
  if (list) while (list.children.length > 1) list.removeChild(list.lastChild!);

  roasters.forEach((roaster) => {
    const opt = document.createElement("option");
    opt.value = String(roaster.id);
    opt.textContent = roaster.name;
    select.appendChild(opt);

    if (list) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className =
        "px-6 py-3 text-left font-body text-sm text-on-surface hover:bg-surface-container-high transition-colors border-b border-outline-variant/10";
      btn.dataset["value"] = String(roaster.id);
      btn.textContent = roaster.name;
      list.appendChild(btn);
    }
  });
}
