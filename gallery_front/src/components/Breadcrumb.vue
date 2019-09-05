<template>
  <div
    id="breadcrumb"
    class="section container"
  >
    <nav class="breadcrumb">
      <ul>
        <li>
          <router-link to="/">
            Etusivu
          </router-link>
        </li>
        <li
          v-for="album in albums"
          :key="album.id"
        >
          <router-link :to="'/album/' + album.id">
            {{ album.title }}
          </router-link>
        </li>
        <li class="is-active">
          <a href="#">{{ currentPage }}</a>
        </li>
      </ul>
    </nav>
  </div>
</template>

<script>
  export default {
    name: "Breadcrumb",
    props: {
      albums: {
        type: Array,
        required: false,
        default: () => []
      },
      currentPage: {
        type: String,
        required: true
      }
    }
  }
</script>

<style scoped>
#breadcrumb {
  padding-top: 1.5rem;
  padding-bottom: 0;
}

</style>
