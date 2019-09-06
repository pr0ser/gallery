<template>
  <div
    v-if="loading===false"
    id="album-list"
    class="container"
  >
    <div class="columns is-multiline">
      <div
        v-for="album in albums"
        :key="album.id"
        class="column is-one-quarter-fullhd is-one-quarter-desktop is-half-tablet is-full-mobile"
      >
        <AlbumCard
          :id="album.id"
          :title="album.title"
          :description="album.description"
          :cover-photos="getCoverPhotos(album)"
          :photo-count="album.photo_count"
          :date="album.date"
          :is-public="album.public"
        />
      </div>
    </div>
  </div>
  <div
    v-else
    class="container section"
  >
    <b-loading
      :is-full-page="false"
      :active.sync="loading"
    />
  </div>
</template>

<script>
  import AlbumCard from './AlbumCard'
  export default {
    name: "AlbumList",
    components: {AlbumCard},
    data() {
      return {
        loading: true,
        error: false,
        albums: []
      }
    },
    beforeMount() {
      this.getData()
    },
    methods: {
      getData: function () {
        this.$api.get('/albums')
          .then(response => {
            this.albums = response.data.results
            this.loading = false
          })
          .catch(error => {
            console.log(error)
            this.error = true
            this.loading = false
          })
      },
      getCoverPhotos: function (album) {
        if (album['album_cover']) {
          return {
            "small": album.album_cover.thumbnail_img,
            "large": album.album_cover.hidpi_thumbnail_img
          }
        }
        else {
          return {}
        }
      }
    }
  }
</script>

<style scoped>
  #album-list {
    margin-left: 5px;
    margin-right: 5px;
  }
</style>
