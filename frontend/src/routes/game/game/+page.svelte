<script>
  import { onMount, onDestroy } from 'svelte';
  import { getPlayers } from '../../../lib/players';
  import { session } from '../../../lib/stores.svelte';

  // The two players in this lobby (loaded from the lobby code set on the join page)
  let players = $state([]);
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

  let items = $state([]);
  let loading = $state(false);
  let error = $state(null);
  let selectedItem = $state(null);
  let isReady = $state(false);

  const TOTAL_TIME = 30;
  let timeLeft = $state(TOTAL_TIME);
  let timerInterval = null;

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

  function selectCard(item) {
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
            <circle cx="50" cy="50" r="4" fill="#ffffff" />
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
  @import url('https://fonts.googleapis.com/css2?family=Quicksand:wght@400;500;600;700&display=swap');

  .game-container {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 2rem;
    background-color: #505153;
    font-family: 'Quicksand', system-ui, sans-serif;
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
      linear-gradient(#ffffff, #ffffff),
      linear-gradient(to bottom, #18181b, #71717a);

    box-shadow: 
      0 6px 14px rgba(0, 0, 0, 0.3),
      0 2px 4px rgba(0, 0, 0, 0.2);
    transition: transform 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.2s ease;
  }

  .player-name {
    text-align: center;
    margin-bottom: 0.75rem;
    font-size: 1.4rem;
    font-weight: 700;
    color: #ffffff;
  }

  /* Opponent Hand (Top) */
  .opponent-section {
    padding-top: 1rem;
  }

  .card-back {
    background-image: 
      linear-gradient(#374151, #374151),
      linear-gradient(to bottom, #111827, #6b7280);
    background-clip: padding-box, border-box;
  }

  .card-pattern {
    width: 100%;
    height: 100%;
    border-radius: 8px;
    background-color: #4b5563;
    background-image: repeating-linear-gradient(
      45deg,
      #374151 0,
      #374151 10px,
      #4b5563 10px,
      #4b5563 20px
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
      #ffffff 0%, 
      #d1d5db 25%, 
      #9ca3af 50%, 
      #d1d5db 75%, 
      #ffffff 100%
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
    background-color: #1f2937;
    border-radius: 4px;
    overflow: hidden;
  }

  /* Solid White Fill Bar with Dynamic Fade */
  .text-progress-fill {
    height: 100%;
    background-color: #ffffff;
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
    color: #16a34a;
    letter-spacing: 0.05em;
    transition: color 0.3s ease;
  }

  .check-circle {
    width: 70px;
    height: 70px;
    border-radius: 50%;
    border: 4px solid transparent;
    background: 
      linear-gradient(#ffffff, #ffffff) padding-box,
      linear-gradient(135deg, #15803d 0%, #84cc16 100%) border-box;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 10px rgba(0, 0, 0, 0.15);
    transition: transform 0.2s, box-shadow 0.3s;
  }

  .check-icon {
    width: 44px;
    height: 44px;
    fill: #16a34a;
    transition: fill 0.3s ease;
  }

  .ready-btn.active .check-circle {
    background: 
      linear-gradient(#dcfce7, #dcfce7) padding-box,
      linear-gradient(135deg, #15803d 0%, #84cc16 100%) border-box;
  }

  /* Ready Button Selection State */
  .ready-btn.has-selection {
    transform: scale(1.12);
  }

  .ready-btn.has-selection .ready-text {
    color: #eab308;
    text-shadow: 0 0 8px rgba(234, 179, 8, 0.4);
  }

  .ready-btn.has-selection .check-circle {
    background: 
      linear-gradient(to bottom, #fffdfa 0%, #fffbeb 100%) padding-box,
      linear-gradient(135deg, #15803d 0%, #84cc16 100%) border-box;
  }

  .ready-btn.has-selection .check-icon {
    fill: #16a34a;
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
    color: #15803d;
    text-shadow: none;
  }

  .ready-btn.has-selection.active .check-circle {
    background: 
      linear-gradient(#dcfce7, #bbf7d0) padding-box,
      linear-gradient(135deg, #16a34a 0%, #15803d 100%) border-box;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  }

  .ready-btn.has-selection.active .check-icon {
    fill: #15803d;
  }

  /* Base Wave Ring (Invisible by default to prevent static pop-in) */
  .wave-ring {
    position: absolute;
    top: 66%;
    left: 50%;
    width: 70px;
    height: 70px;
    border-radius: 50%;
    border: 3px solid #16a34a;
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
      border-color: #facc15;
      box-shadow: 0 0 10px rgba(250, 204, 21, 0.6);
    }
    100% {
      width: 160px;
      height: 160px;
      opacity: 0;
      border-color: #ca8a04;
      box-shadow: 0 0 30px rgba(202, 138, 4, 0);
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
    stroke: #374151;
    stroke-width: 8;
  }

  .ring-progress {
    fill: none;
    stroke: #f97316;
    stroke-width: 8;
    stroke-linecap: round;
    transition: stroke-dashoffset 1s linear;
  }

  .clock-hands {
    color: #ffffff;
    opacity: 0.9;
  }

  .timer-value {
    position: absolute;
    bottom: -1.4rem;
    font-weight: 700;
    font-size: 1rem;
    color: #ffffff;
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
      0 10px 20px rgba(0, 0, 0, 0.4),
      0 4px 6px rgba(0, 0, 0, 0.25);
  }

  .card-front.selected {
    transform: translateY(-6px);
    background-image: 
      linear-gradient(#fef9c3, #fef08a),
      linear-gradient(to bottom, #d97706, #ca8a04);
    box-shadow: 
      0 8px 18px rgba(202, 138, 4, 0.3),
      0 0 10px rgba(254, 240, 138, 0.5);
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
    color: #111827;
    text-align: center;
    line-height: 1.15;
  }

  .you-indicator {
    position: absolute;
    left: 2rem;
    bottom: 2rem;
    font-size: 2.5rem;
    font-weight: 700;
    color: #ffffff;
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
      0 16px 32px rgba(0, 0, 0, 0.45),
      0 0 20px rgba(254, 240, 138, 0.7);
    transition: transform 0.6s cubic-bezier(0.34, 1.56, 0.64, 1), box-shadow 0.6s ease;
    z-index: 10;
  }

</style>
