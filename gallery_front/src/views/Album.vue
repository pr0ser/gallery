<template>
  <main>
    <div
      v-if="!loading && !error"
    >
      <Breadcrumb
        :albums="album.parent_albums"
        :current-page="album.title"
      />
      <section class="section container">
        <div class="is-pulled-right">
          <AlbumActionsButton
            v-if="authenticated"
            :album-id="album.id"
          />
        </div>
        <h1 class="title">
          {{ album.title }}
        </h1>

        <h2
          v-if="album.description"
          class="subtitle"
          v-html="album.description"
        />
      </section>

      <div
        v-if="hasSubAlbums"
        id="subalbums"
        class="container"
      >
        <hr class="hr">
        <section class="section container">
          <h2 class="title is-4">
            Alialbumit
          </h2>
        </section>
        <AlbumList
          :album-array="album.subalbums"
        />
        <hr class="hr hr-bottom">
      </div>
      <div class="container">
        <div class="columns is-multiline is-mobile is-variable is-1">
          <div
            v-for="photo in sortedPhotos"
            :key="photo.id"
            class="column is-one-quarter-fullhd is-one-quarter-desktop is-one-quarter-tablet is-half-mobile"
          >
            <a @click="openModal(photo)">
              <b-image
                :src="photo.thumbnail_img"
                :srcset="photo.thumbnail_img + ' 380w, ' + photo.hidpi_thumbnail_img + ' 600w'"
                :alt="photo.title"
                ratio="1by1"
                responsive
                :lazy="true"
              />
            </a>
          </div>
        </div>
      </div>
      <transition name="fade">
        <div
          v-if="isPhotoModalActive"
          class="photo-modal"
        >
          <div
            class="photo-modal-background"
            @click="isPhotoModalActive = false"
          >
            <transition name="fade">
              <img
                v-show="!isPhotoLoading"
                id="photo"
                :src="getPreviewPhoto('small')"
                :srcset="getPreviewPhoto('small') + ' 1327w, ' + getPreviewPhoto('large') + ' 2340w'"
                sizes="100vw"
                :alt="selectedPhoto.title"
                @load="showPhoto"
                @click="isPhotoModalActive = false"
              >
            </transition>

            <b-loading
              :is-full-page="true"
              :active.sync="isPhotoLoading"
            />

            <button
              class="modal-close is-large"
              @click="isPhotoModalActive === false"
            />
          </div>
        </div>
      </transition>
    </div>
    <div v-else>
      <b-loading
        :is-full-page="true"
        :active.sync="loading"
      />
    </div>
    <ErrorMessage
      v-if="error"
      :retry="true"
      @retry="getData"
    >
      Virhe haettaessa tietoja.
    </ErrorMessage>
  </main>
</template>

<script>
import Breadcrumb from '../components/Breadcrumb'
import AlbumList from '../components/AlbumList'
import AlbumActionsButton from '@/components/AlbumActionsButton'
import ErrorMessage from '@/components/ErrorMessage'
import axios from '../axios'
import { mapGetters } from 'vuex'

export default {
  name: 'Album',
  components: { ErrorMessage, AlbumList, Breadcrumb, AlbumActionsButton },
  data () {
    return {
      loading: true,
      error: false,
      album: {},
      hasSubAlbums: false,
      isPhotoModalActive: false,
      isPhotoLoading: false,
      selectedPhoto: {}
    }
  },
  computed: {
    sortedPhotos: function () {
      const photos = this.album.photos
      const sortOrder = this.album.sort_order

      switch (sortOrder) {
        case 'title':
          return photos.sort((a, b) => (a.title > b.title) ? 1 : -1)
        case '-title':
          return photos.sort((a, b) => (a.title < b.title) ? 1 : -1)
        case 'date':
          return photos.sort((a, b) => (a.date > b.date) ? 1 : -1)
        case '-date':
          return photos.sort((a, b) => (a.date < b.date) ? 1 : -1)
      }
      return photos
    },
    ...mapGetters({
      authenticated: 'auth/authenticated',
      user: 'auth/user'
    })
  },
  watch: {
    $route (to, from) {
      this.getData()
    }
  },
  created () {
    this.getData()
  },
  methods: {
    getData: function () {
      this.error = false
      axios.get('albums/' + this.$route.params.id)
        .then(response => {
          this.album = response.data
          this.hasSubAlbums = !!this.album.subalbums.length
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
      this.isPhotoLoading = true
    },
    showPhoto: function () {
      this.isPhotoLoading = false
    },
    getPreviewPhoto: function (size) {
      if (size === 'large' && this.selectedPhoto.hidpi_preview_img) {
        return this.selectedPhoto.hidpi_preview_img
      }
      if (size === 'small' && this.selectedPhoto.preview_img) {
        return this.selectedPhoto.preview_img
      } else {
        return this.selectedPhoto.image
      }
    }
  }
}
</script>

<style scoped>
.column {
  padding-bottom: 0.3em;
  padding-top: 0.25em;
}

.photo-modal {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
  background: black;
  background: rgba(0, 0, 0, 0.80);
  z-index: 50;
}
.photo-modal-background {
  height: 100%;
  width: 100%;
  overflow: auto;
  margin: auto;
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
}
#photo {
  height: auto;
  position: absolute;
  overflow: hidden;
  max-height: 100%;
  margin: auto;
  top: 0;
  left: 0;
  bottom: 0;
  right: 0;
}
#subalbums {
  padding-top: 0;
  padding-bottom: 3em;
}
.hr {
  background-color: #3d3d3d;
  border: none;
  display: block;
  height: 2px;
  margin: 0;
}
.hr-bottom {
  margin-top: 2em;
}
</style>
