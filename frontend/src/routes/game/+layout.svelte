<script lang="ts">
    import { onDestroy, onMount } from "svelte"
    import type { LayoutProps } from "./$types"
    import { leaveGame, session } from "../../lib/stores.svelte"
    import { goto } from "$app/navigation";

    let { children }: LayoutProps = $props()

    onMount(() => {
        if (!session.username)
            goto("/")
    })

    // Runs when navigating out of the /game route group. This covers every
    // page under /game (current and future), and does not fire when moving
    // between pages inside the group.
    onDestroy(leaveGame)
</script>

{@render children()}
