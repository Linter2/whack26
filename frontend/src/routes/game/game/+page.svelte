<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { getPlayers } from '../../../lib/players';
  import { session } from '../../../lib/stores.svelte';

  // An item card shown to the players (id comes from the backend / server).
  interface Item {
    id: string;
    name: string;
    image: string;
  }

  // The two players in this lobby (loaded from the lobby code set on the join page)
  let players = $state<string[]>([]);
  let me = $derived(session.username);
  let opponent = $derived.by(() => {
    const others = [...players];
    const i = others.indexOf(me);
    if (i !== -1) others.splice(i, 1);
    return others[0] ?? 'Opponent';
  });

  async function loadPlayers() {
    if (!session.lobbyCode) return;
    try {
      players = await getPlayers(session.lobbyCode);
    } catch (err) {
      console.error('Could not load players', err);
    }
  }

  let items = $state<Item[]>([]);
  let loading = $state(false);
  let error = $state<string | null>(null);
  let selectedItem = $state<Item | null>(null);
  let isReady = $state(false);

  const TOTAL_TIME = 30;
  let timeLeft = $state(TOTAL_TIME);
  let timerInterval: ReturnType<typeof setInterval> | undefined = undefined;

  // Compute stroke-dashoffset for SVG timer ring (Radius = 40, Circumference ≈ 251.32)
  const TIMER_RADIUS = 40;
  const CIRCUMFERENCE = 2 * Math.PI * TIMER_RADIUS;
  let strokeDashoffset = $derived(CIRCUMFERENCE - (timeLeft / TOTAL_TIME) * CIRCUMFERENCE);

  // Calculate progress percentage (100% down to 0%) for solid progress bar
  let timeProgress = $derived((timeLeft / TOTAL_TIME) * 100);

  // Hand rotation starts at 0 deg (North) at 30s and completes 360 deg at 0s
  let handRotation = $derived(((TOTAL_TIME - timeLeft) / TOTAL_TIME) * -360 + 90);

  // Toggle flag for mock mode vs backend API
  const USE_MOCK = false;

  const MOCK_ITEMS = [
    { id: 'Q12418', name: 'Mona Lisa', image: '/images/mona_lisa.jpg' },
    { id: 'Q11442', name: 'Bicycle', image: '/images/bicycle.jpg' },
    { id: 'Q11084', name: 'Guitar', image: '/images/guitar.png' },
    { id: 'Q838948', name: 'Nighthawks', image: '/images/nighthawks_painting.jpg' }
  ];

  
  async function fetchRandomItems() {
    loading = true;
    error = null;
    selectedItem = null;
    isReady = false;

    if (USE_MOCK) {
      await new Promise(resolve => setTimeout(resolve, 300));
      items = MOCK_ITEMS;
      loading = false;
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:8000/items');
      if (!response.ok) throw new Error(`Server status: ${response.status}`);
      const data = await response.json();
      console.log(data);
      items = data.slice(0, 4);
    } catch (err) {
      console.error('Fetch error:', err);
      error = 'Failed to load items from server.';
    } finally {
      loading = false;
    }
    console.log(items);
  }


  let isTimeUp = $state(false);

  function startTimer() {
    timerInterval = setInterval(() => {
      if (timeLeft > 0) {
        timeLeft -= 1;
      } else {
        clearInterval(timerInterval);
        isTimeUp = true;
      }
    }, 1000);
  }

  function selectCard(item: Item) {
    // Prevent selecting or deselecting cards once the user is ready
    if (isReady) return;

    if (selectedItem?.id === item.id) {
      selectedItem = null;
    } else {
      selectedItem = item;
    }
  }

  function toggleReady() {
    if (selectedItem !== null) {
      isReady = !isReady;
    }
  }

  onMount(() => {
    loadPlayers();
    fetchRandomItems();
    startTimer();
  });

  onDestroy(() => {
    if (timerInterval) clearInterval(timerInterval);
  });
</script>

<div class="game-container">
  <!-- TOP: Opponent Hand (Hidden Face-Down Cards) -->
  <section class="opponent-section">
    <div class="player-name opponent-name">{opponent}</div>
    <div class="card-row">
      {#each Array(4) as _, i}
        <div class="card card-back">
          <div class="card-pattern"></div>
        </div>
      {/each}
    </div>
  </section>

  <!-- MIDDLE: Status Banner, Ready Button, Timer -->
  <section class="middle-section">
    <!-- Ready Button (Left with Green-to-Lime Gradient Border) -->
    <button 
      class="ready-btn" 
      class:active={isReady} 
      class:has-selection={selectedItem !== null} 
      onclick={toggleReady}
    >
      <!-- Only render waves if a card is selected AND user is not ready -->
      {#if selectedItem !== null && !isReady}
        <span class="wave-ring wave-1"></span>
        <span class="wave-ring wave-2"></span>
      {/if}

      <span class="ready-text">READY</span>
      <div class="check-circle">
        <svg viewBox="0 0 24 24" class="check-icon">
          <path d="M9 16.2L4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4L9 16.2z" />
        </svg>
      </div>
    </button>

    <!-- MIDDLE SECTION: Hide status text & progress bar when time is up -->
    <div class="status-title-container">
      {#if !isTimeUp}
        <h2 class="shimmer-text">Selecting cards...</h2>
        <div class="text-progress-track">
          <div 
            class="text-progress-fill" 
            style="width: {timeProgress}%; opacity: {0.35 + (timeProgress / 100) * 0.65};"
          ></div>
        </div>
      {/if}
    </div>

    <!-- Timer (Right: Starts North at 30s & Sweeps 360° Clockwise to North at 0s) -->
    <div class="timer-container">
      <div class="pulse-wrapper">
        <div class="progress-ring-wrapper">
          <svg class="progress-ring" viewBox="0 0 100 100">
            <!-- Background track circle -->
            <circle cx="50" cy="50" r={TIMER_RADIUS} class="ring-bg" />

            <!-- Orange progress ring starting at 12 o'clock -->
            <circle 
              cx="50" 
              cy="50" 
              r={TIMER_RADIUS} 
              class="ring-progress" 
              style="stroke-dasharray: {CIRCUMFERENCE}; stroke-dashoffset: {strokeDashoffset};"
            />

            <!-- Clock hand starting at North (0 deg) and rotating 360 deg -->
            <g class="clock-hands" style="transform: rotate({handRotation}deg); transform-origin: 50px 50px; transition: transform 1s linear;">
              <line x1="50" y1="50" x2="50" y2="22" stroke="currentColor" stroke-width="5" stroke-linecap="round" />
            </g>
            <circle cx="50" cy="50" r="4" class="timer-dot" />
          </svg>
          <span class="timer-value">{timeLeft}s</span>
        </div>
      </div>
    </div>
  </section>

  <!-- BOTTOM: Player Hand -->
  <!-- PLAYER SECTION: Apply disabled and float classes when time is up -->
  <section class="player-section" class:time-up={isTimeUp}>
    <div class="card-row">
      {#each items as item (item.id)}
        {@const isSelected = selectedItem?.id === item.id}
        <button 
          class="card card-front" 
          class:selected={isSelected}
          class:disabled-card={isTimeUp && !isSelected}
          class:floated-card={isTimeUp && isSelected}
          disabled={isTimeUp}
          onclick={() => selectCard(item)}
        >
          <img src={item.image} alt={item.name} loading="lazy" />
          <span class="card-title">{item.name}</span>
        </button>
      {/each}
    </div>
    <div class="you-indicator">{me || 'You'}</div>
  </section>
</div>

<style>
  .game-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 2rem;
    box-sizing: border-box;
  }

  /* Shared Card Layout */
  .card-row {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
  }

  /* Base Card Frame */
  .card {
    position: relative;
    width: 120px;
    height: 170px;
    border-radius: 16px;
    padding: 0.4rem;
    box-sizing: border-box;

    border: 5px solid transparent;
    background-origin: border-box;
    background-clip: padding-box, border-box;
    background-image: 
      linear-gradient(var(--game-white), var(--game-white)),
      linear-gradient(to bottom, var(--game-zinc-900), var(--game-zinc-500));

    box-shadow: 
      0 6px 14px color-mix(in srgb, var(--game-black) 30%, transparent),
      0 2px 4px color-mix(in srgb, var(--game-black) 20%, transparent);
    transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.2s ease;
  }

  .player-name {
    text-align: center;
    margin-bottom: 0.75rem;
    font-size: 1.4rem;
    font-weight: 700;
    color: var(--game-white);
  }

  /* Opponent Hand (Top) */
  .opponent-section {
    padding-top: 1rem;
  }

  .card-back {
    background-image: 
      linear-gradient(var(--game-gray-700), var(--game-gray-700)),
      linear-gradient(to bottom, var(--game-gray-900), var(--game-gray-500));
    background-clip: padding-box, border-box;
  }

  .card-pattern {
    width: 100%;
    height: 100%;
    border-radius: 8px;
    background-color: var(--game-gray-600);
    background-image: repeating-linear-gradient(
      45deg,
      var(--game-gray-700) 0,
      var(--game-gray-700) 10px,
      var(--game-gray-600) 10px,
      var(--game-gray-600) 20px
    );
  }

  /* Middle Section */
  .middle-section {
    display: flex;
    align-items: center;
    justify-content: space-between;
    width: 100%;
    max-width: 900px;
    margin: 0 auto;
  }

  /* Text & Solid Progress Bar */
  .status-title-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.6rem;
  }

  .shimmer-text {
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(
      90deg, 
      var(--game-white) 0%, 
      var(--game-gray-300) 25%, 
      var(--game-gray-400) 50%, 
      var(--game-gray-300) 75%, 
      var(--game-white) 100%
    );
    background-size: 200% auto;
    color: transparent;
    -webkit-background-clip: text;
    background-clip: text;
    animation: moveGradient 3s linear infinite;
  }

  @keyframes moveGradient {
    0% { background-position: 0% center; }
    100% { background-position: -200% center; }
  }

  /* Solid Dark Gray Track */
  .text-progress-track {
    width: 220px;
    height: 6px;
    background-color: var(--game-gray-800);
    border-radius: 4px;
    overflow: hidden;
  }

  /* Solid White Fill Bar with Dynamic Fade */
  .text-progress-fill {
    height: 100%;
    background-color: var(--game-white);
    border-radius: 4px;
    transition: width 1s linear, opacity 1s linear;
  }

  /* Ready Button (Green to Lime Gradient) */
  .ready-btn {
    position: relative;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    background: none;
    border: none;
    cursor: pointer;
    font-family: inherit;
    transition: transform 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  .ready-text {
    font-weight: 700;
    font-size: 1.2rem;
    color: var(--game-green-600);
    letter-spacing: 0.05em;
    transition: color 0.3s ease;
  }

  .check-circle {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    border: 4px solid transparent;
    background: 
      linear-gradient(var(--game-white), var(--game-white)) padding-box,
      linear-gradient(135deg, var(--game-green-700) 0%, var(--game-lime-500) 100%) border-box;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 10px color-mix(in srgb, var(--game-black) 15%, transparent);
    transition: transform 0.2s, box-shadow 0.3s;
  }

  .check-icon {
    width: 44px;
    height: 44px;
    fill: var(--game-green-600);
    transition: fill 0.3s ease;
  }

  .ready-btn.active .check-circle {
    background: 
      linear-gradient(var(--game-green-100), var(--game-green-100)) padding-box,
      linear-gradient(135deg, var(--game-green-700) 0%, var(--game-lime-500) 100%) border-box;
  }

  /* Ready Button Selection State */
  .ready-btn.has-selection {
    transform: scale(1.12);
  }

  .ready-btn.has-selection .ready-text {
    color: var(--game-yellow-500);
    text-shadow: 0 0 8px color-mix(in srgb, var(--game-yellow-500) 40%, transparent);
  }

  .ready-btn.has-selection .check-circle {
    background: 
      linear-gradient(to bottom, var(--game-cream) 0%, var(--game-amber-50) 100%) padding-box,
      linear-gradient(135deg, var(--game-green-700) 0%, var(--game-lime-500) 100%) border-box;
  }

  .ready-btn.has-selection .check-icon {
    fill: var(--game-green-600);
  }

  /* Button Inflation on Card Selection (Base 1.12x scaled + 10% inflation = ~1.23x total scale) */
  .ready-btn.has-selection {
    transform: scale(1.23);
  }

  /* Ready State when active (clicked while a card is selected) */
  .ready-btn.has-selection.active {
    transform: scale(0.95); /* Shrinks slightly */
    filter: opacity(0.7) grayscale(30%); /* Slightly grays out and softens */
  }

  .ready-btn.has-selection.active .ready-text {
    color: var(--game-green-700);
    text-shadow: none;
  }

  .ready-btn.has-selection.active .check-circle {
    background: 
      linear-gradient(var(--game-green-100), var(--game-green-200)) padding-box,
      linear-gradient(135deg, var(--game-green-600) 0%, var(--game-green-700) 100%) border-box;
    box-shadow: 0 2px 6px color-mix(in srgb, var(--game-black) 15%, transparent);
  }

  .ready-btn.has-selection.active .check-icon {
    fill: var(--game-green-700);
  }

  /* Base Wave Ring (Invisible by default to prevent static pop-in) */
  .wave-ring {
    position: absolute;
    top: 66%;
    left: 50%;
    width: 70px;
    height: 70px;
    border-radius: 50%;
    border: 3px solid var(--game-green-600);
    pointer-events: none;
    transform: translate(-50%, -50%);
    opacity: 0; /* Keeps delayed waves hidden until animation starts */
    animation: wavePulse 2s infinite cubic-bezier(0.215, 0.61, 0.355, 1);
  }

  .wave-ring.wave-1 {
    animation-delay: 0s;
  }

  .wave-ring.wave-2 {
    animation-delay: 1s;
  }

  @keyframes wavePulse {
    0% {
      width: 70px;
      height: 70px;
      opacity: 0.8;
      border-color: var(--game-yellow-400);
      box-shadow: 0 0 10px color-mix(in srgb, var(--game-yellow-400) 60%, transparent);
    }
    100% {
      width: 160px;
      height: 160px;
      opacity: 0;
      border-color: var(--game-yellow-600);
      box-shadow: 0 0 30px color-mix(in srgb, var(--game-yellow-600) 0%, transparent);
    }
  }

  /* Timer (Right: Circular Ring & Clock Hand aligned to North) */
  .timer-container {
    display: flex;
    flex-direction: column;
    align-items: center;
  }

  .pulse-wrapper {
    animation: pulseOut 1s infinite ease-in-out;
  }

  @keyframes pulseOut {
    0% { transform: scale(1); }
    50% { transform: scale(1.1); }
    100% { transform: scale(1); }
  }

  .progress-ring-wrapper {
    position: relative;
    width: 80px;
    height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .progress-ring {
    width: 100%;
    height: 100%;
    transform: rotate(-90deg); /* Aligns ring stroke origin to 12 o'clock North */
  }

  .ring-bg {
    fill: none;
    stroke: var(--game-gray-700);
    stroke-width: 8;
  }

  .ring-progress {
    fill: none;
    stroke: var(--game-orange-500);
    stroke-width: 8;
    stroke-linecap: round;
    transition: stroke-dashoffset 1s linear;
  }

  .clock-hands {
    color: var(--game-white);
    opacity: 0.9;
  }

  .timer-dot {
    fill: var(--game-white);
  }

  .timer-value {
    position: absolute;
    bottom: -1.4rem;
    font-weight: 700;
    font-size: 1rem;
    color: var(--game-white);
  }

  /* Player Hand (Bottom) */
  .player-section {
    position: relative;
    padding-bottom: 1rem;
  }

  .card-front {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: space-between;
    cursor: pointer;
    font-family: inherit;
  }

  .card-front:hover {
    transform: translateY(-6px);
    box-shadow: 
      0 10px 20px color-mix(in srgb, var(--game-black) 40%, transparent),
      0 4px 6px color-mix(in srgb, var(--game-black) 25%, transparent);
  }

  .card-front.selected {
    transform: translateY(-6px);
    background-image: 
      linear-gradient(var(--game-yellow-50), var(--game-yellow-200)),
      linear-gradient(to bottom, var(--game-amber-600), var(--game-yellow-600));
    box-shadow: 
      0 8px 18px color-mix(in srgb, var(--game-yellow-600) 30%, transparent),
      0 0 10px color-mix(in srgb, var(--game-yellow-200) 50%, transparent);
  }

  .card-front img {
    width: 100%;
    height: 105px;
    object-fit: cover;
    border-radius: 10px;
  }

  .card-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: var(--game-gray-900);
    text-align: center;
    line-height: 1.15;
  }

  .you-indicator {
    position: absolute;
    left: 2rem;
    bottom: 2rem;
    font-size: 2.5rem;
    font-weight: 700;
    color: var(--game-white);
    }

  /* Gray out unselected cards when timer ends */
  .card-front.disabled-card {
    opacity: 0.35;
    filter: grayscale(100%);
    cursor: not-allowed;
    transform: scale(0.95);
    transition: opacity 0.4s ease, filter 0.4s ease, transform 0.4s ease;
  }

  /* Float selected card upward into the center field */
  .card-front.floated-card {
    transform: translateY(-120px) scale(1.15);
    box-shadow: 
      0 16px 32px color-mix(in srgb, var(--game-black) 45%, transparent),
      0 0 20px color-mix(in srgb, var(--game-yellow-200) 70%, transparent);
    transition: transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.6s ease;
    z-index: 10;
  }

</style>
