<template>
  <section class="section container">
    <div
      class="columns is-centered"
    >
      <div class="column is-6">
        <div
          class="box"
        >
          <h1 class="title is-4">
            <span class="icon is-large">
              <i class="fas fa-upload" />
            </span>
            Lisää kuvia
          </h1>
          <b-field label="Albumi">
            <b-select
              v-model="album"
              expanded
            >
              <option
                v-for="alb in albums"
                :key="alb.id"
                :value="alb.id"
              >
                {{ alb.title }}
              </option>
            </b-select>
          </b-field>
          <b-field label="Kuva(t)">
            <b-upload
              v-model="files"
              multiple
              drag-drop
              type="is-info"
              accept="image/*"
              expanded
            >
              <section class="section">
                <div class="content has-text-centered">
                  <p>
                    <b-icon
                      icon="upload"
                      size="is-large"
                      pack="fas"
                    />
                  </p>
                  <p>Raahaa kuvat tähän tai klikkaa.</p>
                </div>
              </section>
            </b-upload>
          </b-field>

          <div class="tags">
            <span
              v-for="(file, index) in files"
              :key="index"
              class="tag is-info"
            >
              {{ file.name }}
              <button
                class="delete is-small"
                type="button"
                @click="deleteFile(index)"
              />
            </span>
          </div>
          <b-progress
            v-if="uploadStarted"
            size="is-large"
            type="is-info"
            show-value
            format="percent"
            :value="uploadPercentage"
          >
            {{ uploadPercentage }} %
          </b-progress>
          <b-field
            grouped
            position="is-right"
          >
            <b-button
              type="is-info"
              :disabled="uploadComplete || !album || !files"
              :class="{ 'is-loading': loading }"
              @click="upload"
            >
              Lähetä
            </b-button>
          </b-field>
        </div>
      </div>
    </div>
  </section>
</template>

<script>
import axios from '@/axios'

export default {
  name: 'Upload',
  props: {
    albumId: {
      type: Number,
      required: false,
      default: null
    }
  },
  data () {
    return {
      loading: true,
      error: false,
      albums: {},
      uploadStarted: false,
      uploadComplete: false,
      uploadPercentage: 0,
      album: null,
      files: [],
      results: null
    }
  },
  created () {
    this.getData()
  },
  methods: {
    getData: function () {
      this.error = false
      axios.get('/all-albums')
        .then(response => {
          this.albums = response.data.results
          if (this.albumId) {
            this.album = this.albumId
          }
          this.loading = false
        })
        .catch(error => {
          console.log(error)
          this.error = true
          this.loading = false
        })
    },
    upload: function () {
      this.error = false
      this.loading = true
      this.uploadStarted = true
      const formData = new FormData()
      this.files.forEach(file => formData.append('files', file))
      formData.append('album', this.album)

      axios.post('/upload',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: function (evt) {
            if (evt.lengthComputable) {
              this.uploadPercentage = Math.trunc(evt.loaded / evt.total * 100)
            }
          }.bind(this)
        }
      ).then((response) => {
        this.results = response.data
        this.loading = false
        this.uploadComplete = true
        this.$buefy.toast.open({
          message: this.results.newPhotos + ' kuva(a) lisätty',
          type: 'is-info',
          duration: 3000
        })
        if (this.results.rejectedPhotos) {
          this.$buefy.toast.open({
            message: this.results.rejectedPhotos + ' tiedosto(a) hylättiin',
            type: 'is-warning',
            duration: 3000
          })
        }
        this.$router.push('album/' + this.album)
      })
        .catch(error => {
          this.loading = false
          this.error = true
          this.results = error.response.data
        })
    },
    deleteFile (index) {
      this.files.splice(index, 1)
    }
  }
}

</script>

<style scoped>

</style>
