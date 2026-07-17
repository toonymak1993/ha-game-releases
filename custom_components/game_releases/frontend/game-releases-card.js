class GameReleasesCard extends HTMLElement {
  static getStubConfig() {
    return { entity: "sensor.game_releases_upcoming_releases", limit: 8 };
  }

  setConfig(config) {
    if (!config.entity) throw new Error("Game Releases Card requires an entity");
    this._config = { title: "Game Releases", limit: 8, ...config };
    this._signature = undefined;
  }

  set hass(hass) {
    this._hass = hass;
    const state = hass.states[this._config?.entity];
    const signature = `${state?.last_updated || "missing"}:${this._config?.limit}`;
    if (signature !== this._signature) {
      this._signature = signature;
      this._render();
    }
  }

  getCardSize() {
    return 6;
  }

  _escape(value) {
    return String(value ?? "").replace(
      /[&<>'"]/g,
      (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" })[char]
    );
  }

  _safeUrl(value) {
    try {
      const url = new URL(value);
      return url.protocol === "https:" ? url.href : "";
    } catch (_error) {
      return "";
    }
  }

  _isGerman() {
    return (this._hass?.locale?.language || navigator.language || "en")
      .toLowerCase()
      .startsWith("de");
  }

  _labels(days) {
    if (days === 0) return this._isGerman() ? "Heute" : "Today";
    if (days === 1) return this._isGerman() ? "Morgen" : "Tomorrow";
    return this._isGerman() ? `in ${days} Tagen` : `in ${days} days`;
  }

  _formatDate(value) {
    const language = this._hass?.locale?.language || navigator.language;
    const date = new Date(`${value}T12:00:00`);
    return new Intl.DateTimeFormat(language, {
      day: "2-digit",
      month: "short",
      year: "numeric",
    }).format(date);
  }

  _renderGame(game, index) {
    const image = this._safeUrl(game.image);
    const target = this._safeUrl(game.url);
    const platforms = (game.platforms || []).slice(0, 3);
    return `
      <article class="game" tabindex="0" role="link" data-index="${index}" data-url="${this._escape(target)}">
        <div class="cover" style="${image ? `background-image:url('${this._escape(image)}')` : ""}">
          <span class="countdown">${this._escape(this._labels(game.days_until))}</span>
          ${game.metacritic ? `<span class="score"><ha-icon icon="mdi:star"></ha-icon>${this._escape(game.metacritic)}</span>` : ""}
        </div>
        <div class="details">
          <strong title="${this._escape(game.name)}">${this._escape(game.name)}</strong>
          <span class="date">${this._escape(this._formatDate(game.released))}</span>
          <div class="platforms">${platforms.map((platform) => `<span>${this._escape(platform)}</span>`).join("")}</div>
        </div>
      </article>`;
  }

  _render() {
    if (!this._config || !this._hass) return;
    const state = this._hass.states[this._config.entity];
    const games = (state?.attributes?.games || []).slice(0, Number(this._config.limit) || 8);
    const german = this._isGerman();
    const subtitle = state
      ? (german ? `${games.length} kommende Releases` : `${games.length} upcoming releases`)
      : (german ? "Dein persönlicher Release-Radar" : "Your personal release radar");

    let content;
    if (!state) {
      content = `
        <div class="setup">
          <div class="setup-art"><ha-icon icon="mdi:controller-classic"></ha-icon></div>
          <div class="setup-copy">
            <strong>${german ? "Bereit für neue Games?" : "Ready for new games?"}</strong>
            <span>${german ? "Aktiviere den kostenlosen Steam-Releasefeed – ganz ohne Konto oder API-Key." : "Enable the free Steam release feed — no account or API key required."}</span>
          </div>
          <button class="setup-button" type="button">
            <ha-icon icon="mdi:link-variant"></ha-icon>
            ${german ? "Jetzt verbinden" : "Connect now"}
          </button>
        </div>`;
    } else if (!games.length) {
      content = `<div class="empty"><ha-icon icon="mdi:calendar-search"></ha-icon><span>${german ? "In deinem Zeitraum wurden keine Releases gefunden." : "No releases were found in your selected range."}</span></div>`;
    } else {
      content = `<div class="grid">${games.map((game, index) => this._renderGame(game, index)).join("")}</div>`;
    }

    this.innerHTML = `
      <ha-card>
        <div class="accent"></div>
        <div class="header">
          <div class="heading-icon"><ha-icon icon="mdi:gamepad-variant"></ha-icon></div>
          <div class="heading-copy"><h2>${this._escape(this._config.title)}</h2><p>${this._escape(subtitle)}</p></div>
          ${games.length ? `<span class="total">${games.length}</span>` : ""}
        </div>
        ${content}
        <a class="attribution" href="https://store.steampowered.com/" target="_blank" rel="noopener">${german ? "Release-Daten von Steam" : "Release data by Steam"}<ha-icon icon="mdi:open-in-new"></ha-icon></a>
      </ha-card>
      <style>
        :host { --release-radius: var(--ha-card-border-radius, 22px); }
        ha-card { position:relative; padding:20px; overflow:hidden; border-radius:var(--release-radius); background:linear-gradient(145deg,color-mix(in srgb,var(--card-background-color) 94%,var(--primary-color)),var(--card-background-color)); }
        .accent { position:absolute; width:220px; height:220px; right:-90px; top:-130px; border-radius:50%; background:var(--primary-color); opacity:.12; filter:blur(2px); pointer-events:none; }
        .header { position:relative; display:flex; align-items:center; gap:12px; margin-bottom:18px; }
        .heading-icon { display:grid; place-items:center; width:46px; height:46px; flex:0 0 46px; border-radius:16px; color:var(--primary-color); background:color-mix(in srgb,var(--primary-color) 15%,var(--card-background-color)); box-shadow:0 8px 20px color-mix(in srgb,var(--primary-color) 18%,transparent); }
        .heading-icon ha-icon { --mdc-icon-size:27px; }
        .heading-copy { min-width:0; flex:1; }
        h2 { margin:0; font-size:1.28rem; line-height:1.25; color:var(--primary-text-color); }
        .header p { margin:4px 0 0; color:var(--secondary-text-color); font-size:.82rem; }
        .total { display:grid; place-items:center; min-width:28px; height:28px; padding:0 4px; border-radius:10px; color:var(--primary-color); background:color-mix(in srgb,var(--primary-color) 13%,transparent); font-size:.78rem; font-weight:800; }
        .grid { display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:13px; }
        .game { min-width:0; overflow:hidden; border-radius:18px; background:var(--secondary-background-color); cursor:pointer; box-shadow:0 7px 22px rgba(0,0,0,.14); transition:transform .18s ease,box-shadow .18s ease; outline:none; }
        .game:hover,.game:focus-visible { transform:translateY(-4px); box-shadow:0 13px 28px rgba(0,0,0,.22); }
        .cover { position:relative; aspect-ratio:16/10; background:linear-gradient(135deg,var(--primary-color),var(--accent-color)); background-size:cover; background-position:center; }
        .cover::after { content:""; position:absolute; inset:auto 0 0; height:42%; background:linear-gradient(transparent,rgba(0,0,0,.32)); }
        .countdown,.score { position:absolute; z-index:1; top:10px; display:flex; align-items:center; gap:3px; padding:5px 8px; border:1px solid rgba(255,255,255,.16); border-radius:999px; color:#fff; font-size:.69rem; font-weight:750; backdrop-filter:blur(12px); background:rgba(15,18,25,.7); }
        .countdown { left:10px; } .score { right:10px; background:rgba(35,130,72,.86); }
        .score ha-icon { --mdc-icon-size:12px; }
        .details { padding:12px; display:flex; flex-direction:column; gap:5px; }
        .details strong { color:var(--primary-text-color); white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-size:.92rem; }
        .date { color:var(--secondary-text-color); font-size:.76rem; }
        .platforms { display:flex; flex-wrap:wrap; gap:4px; min-height:20px; margin-top:4px; }
        .platforms span { padding:3px 7px; border-radius:8px; background:color-mix(in srgb,var(--primary-color) 14%,transparent); color:var(--primary-text-color); font-size:.62rem; }
        .setup { position:relative; display:grid; grid-template-columns:auto 1fr auto; align-items:center; gap:16px; padding:18px; border:1px solid color-mix(in srgb,var(--primary-color) 22%,transparent); border-radius:20px; background:color-mix(in srgb,var(--primary-color) 7%,var(--secondary-background-color)); }
        .setup-art { display:grid; place-items:center; width:58px; height:58px; border-radius:19px; color:#fff; background:linear-gradient(135deg,var(--primary-color),var(--accent-color)); box-shadow:0 10px 25px color-mix(in srgb,var(--primary-color) 30%,transparent); }
        .setup-art ha-icon { --mdc-icon-size:33px; }
        .setup-copy { display:flex; flex-direction:column; gap:5px; min-width:0; }
        .setup-copy strong { color:var(--primary-text-color); font-size:1rem; }
        .setup-copy span { color:var(--secondary-text-color); font-size:.8rem; line-height:1.4; }
        .setup-button { display:flex; align-items:center; gap:7px; border:0; border-radius:14px; padding:11px 14px; color:var(--text-primary-color,#fff); background:var(--primary-color); font:inherit; font-size:.78rem; font-weight:700; cursor:pointer; box-shadow:0 7px 18px color-mix(in srgb,var(--primary-color) 28%,transparent); }
        .setup-button ha-icon { --mdc-icon-size:18px; }
        .empty { display:flex; align-items:center; justify-content:center; gap:10px; min-height:110px; color:var(--secondary-text-color); }
        .empty ha-icon { color:var(--primary-color); }
        .attribution { display:flex; align-items:center; justify-content:flex-end; gap:4px; margin-top:13px; color:var(--secondary-text-color); font-size:.66rem; text-decoration:none; opacity:.82; }
        .attribution ha-icon { --mdc-icon-size:11px; }
        @media (max-width:700px) { .setup { grid-template-columns:auto 1fr; } .setup-button { grid-column:1 / -1; justify-content:center; } }
        @media (max-width:500px) { ha-card { padding:15px; } .grid { display:flex; overflow-x:auto; scroll-snap-type:x mandatory; padding:2px 1px 8px; } .game { flex:0 0 76%; scroll-snap-align:start; } .setup { padding:14px; gap:12px; } }
      </style>`;

    this.querySelectorAll(".game").forEach((element) => {
      const open = () => {
        if (element.dataset.url) window.open(element.dataset.url, "_blank", "noopener");
      };
      element.addEventListener("click", open);
      element.addEventListener("keydown", (event) => {
        if (event.key === "Enter" || event.key === " ") open();
      });
    });

    this.querySelector(".setup-button")?.addEventListener("click", () => {
      history.pushState(null, "", "/config/integrations/dashboard/add?domain=game_releases");
      window.dispatchEvent(new Event("location-changed"));
    });
  }
}

customElements.define("game-releases-card", GameReleasesCard);
window.customCards = window.customCards || [];
window.customCards.push({
  type: "game-releases-card",
  name: "Game Releases Card",
  description: "Upcoming game releases with covers and countdowns.",
  preview: true,
});
