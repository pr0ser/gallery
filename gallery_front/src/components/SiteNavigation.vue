<template>
  <nav>
    <b-navbar class="is-black">
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
        <b-navbar-item tag="div">
          test
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

</style>
