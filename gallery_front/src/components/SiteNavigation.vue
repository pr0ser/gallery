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
        <b-navbar-dropdown
          label="Menu"
          right
        >
          <b-navbar-item
            tag="router-link"
            to="/upload"
          >
            <b-icon icon="upload" />
            <span>Lisää kuvia</span>
          </b-navbar-item>
          <b-navbar-item
            tag="router-link"
            to="/new-album"
          >
            <b-icon icon="plus" />
            <span>Luo albumi</span>
          </b-navbar-item>
          <hr class="navbar-divider">
          <b-navbar-item href="https://gallery.fantti.net/admin/">
            <b-icon icon="cog" />
            <span>Ylläpito</span>
          </b-navbar-item>
          <hr class="navbar-divider">
          <b-navbar-item @click="signOut">
            <b-icon icon="sign-in-alt" />
            <span>Kirjaudu ulos</span>
          </b-navbar-item>
        </b-navbar-dropdown>
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
          <b-icon icon="sign-in-alt" />
        </b-navbar-item>
        <b-navbar-item
          tag="router-link"
          to="/login"
          title="Kirjaudu sisään"
          class="is-hidden-desktop"
        >
          <b-icon icon="sign-in-alt" />
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
</style>
