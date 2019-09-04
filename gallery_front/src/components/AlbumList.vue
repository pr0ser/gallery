<template>
  <div class="container">
    <div class="columns is-multiline">
      <div
        v-for="album in albums"
        :key="album.id"
        class="column is-one-quarter-fullhd is-one-quarter-desktop is-half-tablet is-full-mobile"
      >
        <router-link :to="'/album/' + album.id">
          <div class="card">
            <div class="card-image">
              <figure class="image">
                <img
                  v-if="album.album_cover"
                  :src="album.album_cover.hidpi_thumbnail_img"
                  :alt="album.title"
                >
                <img
                  v-else
                  src="../assets/no_image.png"
                  alt="Ei kuvaa"
                >
              </figure>
            </div>
            <div class="card-content">
              <div class="content">
                <p class="title is-6">
                  {{ album.title }}
                </p>
                <p class="content">
                  {{ album.description }}
                </p>
              </div>
            </div>
            <footer class="card-footer">
              <div class="card-footer-item level content is-small">
                <div class="level-left ">
                  <span class="icon">
                    <i class="fas fa-image" />
                  </span>
                  {{ album.photo_count }}
                </div>
                <div class="level-right">
                  {{ album.date | formatDate }}
                  <span
                    v-if="album.public === false"
                    class="icon"
                  >
                    <i class="fas fa-lock" />
                  </span>
                </div>
              </div>
            </footer>
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script>
  export default {
    name: "AlbumList",
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
      }
    }
  }
</script>

<style scoped>
.card {
   display: flex;
   flex-direction: column;
   height: 100%;
   border-radius: 5px;
}
.card .image img {
  border-radius: 5px 5px 0 0;
}
.card-footer {
   margin-top: auto;
}
.card-footer-item {
  color: #858585;
}
</style>
