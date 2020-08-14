<template>
  <main class="container">
    <div
      v-if="!loading && !error"
    >
      <div class="section">
        <h1 class="title">
          Albumit
        </h1>

        <h2 class="subtitle">
          Satunnaisia kuvakokoelmia vuosien varrelta.
        </h2>
      </div>
      <AlbumList
        :album-array="albums"
      />
    </div>

    <div v-else>
      <b-loading
        :is-full-page="true"
        :active.sync="loading"
      />
    </div>

    <div
      v-if="error"
      class="section is-one-third"
    >
      <div
        class="columns is-centered"
      >
        <div class="column is-two-fifths">
          <b-notification
            type="is-danger"
            has-icon
            closable="false"
            icon-pack="fas"
          >
            Virhe haettaessa sisältöä. <a @click="getData">Yritä uudelleen.</a>
          </b-notification>
        </div>
      </div>
    </div>
  </main>
</template>
<script>
// @ is an alias to /src
import axios from '../axios'
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
  created () {
    this.getData()
  },
  methods: {
    getData: function () {
      this.error = false
      axios.get('/albums')
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
<style scoped>

</style>
