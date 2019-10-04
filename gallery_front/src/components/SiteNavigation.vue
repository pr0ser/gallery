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

      <template slot="end">
        <b-navbar-item
          tag="div"
          class="is-hidden-touch is-hidden-desktop-only"
        >
          <span class="icon">
            <i class="fas fa-sign-in-alt" />
          </span>
        </b-navbar-item>
        <b-navbar-item
          tag="div"
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
export default {
  name: 'SiteNavigation'
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
