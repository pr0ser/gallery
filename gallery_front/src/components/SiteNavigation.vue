<template>
  <nav>
    <b-navbar type="is-black">
      <template slot="brand">
        <b-navbar-item
          id="logo"
          tag="router-link"
          to="/"
        >
          Galleria
        </b-navbar-item>
      </template>

      <template
        v-if="authenticated"
        slot="end"
      >
        <b-navbar-item
          tag="a"
          class="is-hidden-touch is-hidden-desktop-only"
          title="Kirjaudu ulos"
          @click="signOut"
        >
          <span class="icon">
            <i class="fas fa-sign-out-alt" />
          </span>
        </b-navbar-item>
        <b-navbar-item
          tag="a"
          class="is-hidden-desktop"
          title="Kirjaudu ulos"
          @click="signOut"
        >
          <span class="icon">
            <i class="fas fa-sign-out-alt" />
          </span>
          Kirjaudu ulos
        </b-navbar-item>
      </template>

      <template
        v-else
        slot="end"
      >
        <b-navbar-item
          tag="router-link"
          to="/login"
          title="Kirjaudu sisään"
          class="is-hidden-touch is-hidden-desktop-only"
        >
          <span class="icon">
            <i class="fas fa-sign-in-alt" />
          </span>
        </b-navbar-item>
        <b-navbar-item
          tag="router-link"
          to="/login"
          title="Kirjaudu sisään"
          class="is-hidden-desktop"
        >
          <span class="icon">
            <i class="fas fa-sign-in-alt" />
          </span>
          Kirjaudu
        </b-navbar-item>
      </template>
    </b-navbar>
  </nav>
</template>

<script>
import { mapActions, mapGetters } from 'vuex'

export default {
  name: 'SiteNavigation',

  computed: {
    ...mapGetters({
      authenticated: 'auth/authenticated',
      user: 'auth/user'
    })
  },

  methods: {
    ...mapActions({
      signOutAction: 'auth/signOut'
    }),

    signOut () {
      this.signOutAction().then(() => {
        this.$buefy.toast.open({
          message: 'Kirjauduit ulos',
          type: 'is-info',
          duration: 3000
        })
      })
    }
  }

}
</script>

<style lang="css" scoped>
#logo {
  font-family: 'Playfair Display SC', serif;
  font-size: 1.8em;
  font-weight: bold;
}
#app .navbar  {
  background-color: #000000;
}
</style>
