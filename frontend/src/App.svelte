<script>
    import { client } from './client';
	import { gql } from "@apollo/client/core";
	
	let userData;

	function getUser() {
		userData = client.query(gql`
			query getUser($userId: Int = 3){
				user(userId: $userId){
					username
					transactions {
						amount
						description
					}
				}
			}
		`);
	}


</script>

<h1>Welcome to SvelteKit</h1>
<p>Visit <a href="https://kit.svelte.dev">kit.svelte.dev</a> to read the documentation</p>
<button on:click={getUser}>Get User</button>
{#if userData}
    {#if $userData.loading}
        Loading...
    {:else if $userData.error}
        Error: {$userData.error.message}
    {:else}
		<h4>{$userData.data.user.username}</h4>
        <ul>
			
        {#each $userData.data.user.transactions as transaction}
            <li>
                {transaction.amount} - {transaction.description}
            </li>
        {/each}
        </ul>
    {/if}
{/if}