<template>
  <div id="app">
    <SiteNavigation />
    <router-view />
  </div>
</template>

<script>
  import SiteNavigation from './components/SiteNavigation'
  export default {
    components: {SiteNavigation}
  }
</script>

<style lang="scss">
@import "/assets/main.scss";
</style>
