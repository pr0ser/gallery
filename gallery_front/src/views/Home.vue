<template>
  <main
    v-if="loading===false"
    class="container"
  >
    <section class="section">
      <h1 class="title">
        Albumit
      </h1>

      <h2 class="subtitle">
        Satunnaisia kuvakokoelmia vuosien varrelta.
      </h2>
    </section>
    <AlbumList
      :album-array="albums"
    />
  </main>
  <main v-else>
    <b-loading
      :is-full-page="true"
      :active.sync="loading"
    />
  </main>
</template>

<script>
// @ is an alias to /src
import AlbumList from '@/components/AlbumList'

export default {
  name: 'Home',
  components: { AlbumList },
  data () {
    return {
      loading: true,
      error: false,
      albums: []
    }
  },
  beforeMount () {
    this.getData()
  },
  methods: {
    getData: function () {
      this.$api.get('/albums/')
        .then(response => {
          this.albums = response.data.results
          this.loading = false
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
