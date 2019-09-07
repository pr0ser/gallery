<template>
  <div id="app">
    <SiteNavigation />
    <transition name="fade">
      <router-view />
    </transition>
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
