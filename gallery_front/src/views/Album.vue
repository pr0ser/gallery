<template>
  <main
    v-if="loading===false"
  >
    <Breadcrumb
      :albums="album.parent_albums"
      :currentPage="album.title"
    />
    <section class="section container">
      <h1 class="title">
        {{ album.title }}
      </h1>

      <h2
        v-if="album.description"
        class="subtitle"
      >
        {{ album.description }}
      </h2>
    </section>

    <div class="container">
      <div class="columns is-multiline is-mobile is-variable is-1">
        <div
          v-for="photo in sortedPhotos"
          :key="photo.id"
          class="column is-one-quarter-fullhd is-one-quarter-desktop is-one-quarter-tablet is-half-mobile"
        >
          <a
            @click="openModal(photo)"
          >
            <figure class="image is-square">

              <img
                :src="photo.hidpi_thumbnail_img"
                alt="photo.title"
              >
            </figure>
          </a>
        </div>
      </div>

      <b-modal
        :active.sync="isPhotoModalActive"
        width="1400px"
        custom-class="photo"
      >
        <img
          :src="selectedPhoto.hidpi_preview_img"
          :alt="selectedPhoto.title"
          class="image"
          @click="isPhotoModalActive=false"
        >
      </b-modal>
    </div>
  </main>
</template>

<script>
  import Breadcrumb from '../components/Breadcrumb'

  export default {
    name: "Album",
    components: {Breadcrumb},
    data() {
      return {
        loading: true,
        error: false,
        album: {},
        isPhotoModalActive: false,
        selectedPhoto: {}
      }
    },
    computed: {
      sortedPhotos: function () {
        const photos = this.album.photos
        return photos.sort((a, b) => (a.title > b.title) ? 1 : -1)
      }
    },
    watch: {
      $route(to, from) {
        this.getData()
      }
    },
    beforeMount() {
      this.getData()
    },
    methods: {
      getData: function () {
        this.$api.get('/albums/' + this.$route.params.id)
          .then(response => {
            this.album = response.data
            this.loading = false
          })
          .catch(error => {
            console.log(error)
            this.error = true
            this.loading = false
          })
      },
      openModal: function (photo) {
        this.selectedPhoto = photo
        this.isPhotoModalActive = true
      }
    }
  }
</script>

<style scoped>
.column {
  padding-bottom: 0.3em;
  padding-top: 0.25em;
}
.photo img {
  max-height: 95vh;
  margin: auto;
}

</style>
