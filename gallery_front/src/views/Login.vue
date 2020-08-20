<template>
  <div
    id="login"
    class="section container"
  >
    <div
      v-if="!authenticated"
      class="columns is-centered"
    >
      <div class="column is-6">
        <div
          class="box"
        >
          <h1 class="title is-4">
            <span class="icon is-large">
              <i class="fas fa-sign-in-alt" />
            </span>
            Kirjaudu sisään
          </h1>
          <form
            class="is-large"
            @submit.prevent="login()"
          >
            <div class="field">
              <p class="control has-icons-left">
                <input
                  v-model="credentials.username"
                  class="input is-medium"
                  type="text"
                  placeholder="Käyttäjätunnus"
                  required
                >
                <span class="icon is-small is-left">
                  <i class="fas fa-user" />
                </span>
              </p>
            </div>
            <div class="field">
              <p class="control has-icons-left">
                <input
                  v-model="credentials.password"
                  class="input is-medium"
                  type="password"
                  placeholder="Salasana"
                  required
                >
                <span class="icon is-small is-left">
                  <i class="fas fa-lock" />
                </span>
              </p>
            </div>
            <div class="field">
              <p class="control">
                <button
                  type="submit"
                  class="button is-info is-medium is-fullwidth"
                  :class="{ 'is-loading': loading }"
                >
                  Kirjaudu
                </button>
              </p>
            </div>
            <b-notification
              :active.sync="error"
              type="is-danger"
              has-icon
              icon-pack="fas"
              aria-close-label="Sulje ilmoitus"
              role="alert"
            >
              Ei voitu kirjautua annetuilla tunnuksilla. Tarkista käyttäjätunnus ja salasana.
            </b-notification>
          </form>
        </div>
      </div>
    </div>

    <div
      v-if="authenticated"
      class="columns is-centered"
    >
      <div class="column is-6">
        <div class="box">
          <h1 class="title">
            Käyttäjätiedot
          </h1>
          <p>Olet kirjautunut sisään käyttäjänä {{ user.username }} ({{ user.email }}).</p>
          <div class="content">
            <p class="buttons">
              <button
                id="logout"
                class="button is-info"
                :class="{ 'is-loading': loading }"
                @click="signOut"
              >
                Kirjaudu ulos
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  data () {
    return {
      title: 'Kirjaudu sisään',
      credentials: {
        username: null,
        password: null
      },
      loggedIn: false,
      loading: false,
      error: null
    }
  },
  computed: {
    ...mapGetters({
      authenticated: 'auth/authenticated',
      user: 'auth/user'
    })
  },

  methods: {
    ...mapActions({
      signIn: 'auth/signIn'
    }),

    ...mapActions({
      signOutAction: 'auth/signOut'
    }),

    signOut () {
      this.loading = true
      this.signOutAction().then(() => {
        this.loading = false
      })
    },

    login () {
      this.loading = true
      this.signIn(this.credentials).then(() => {
        this.loading = false
        if (this.$route.query.redirect) {
          this.$router.push(this.$route.query.redirect || '/login')
        }
      })
        .catch(error => {
          console.log(error)
          this.error = true
          this.loading = false
        })
    }
  }
}
</script>
.
<style scoped>
#logout {
  margin-top: 1em;
}
</style>
