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
              <i class="fas fa-edit" />
            </span>
            Muokkaa albumia
          </h1>
          <b-field label="Nimi">
            <b-input
              v-model="albumDetails.title"
              required
            />
          </b-field>
          <b-field label="Kuvaus">
            <b-input
              v-model="albumDetails.description"
              maxlength="255"
              type="textarea"
              required
            />
          </b-field>
          <b-field label="Päiväys">
            <b-datepicker
              v-model="date"
              locale="fi-FI"
              icon-pack="fas"
              :first-day-of-week="1"
              required
            />
          </b-field>
          <b-field label="Yläalbumi">
            <b-select
              v-model="albumDetails.parent"
              expanded
            >
              <option :value="null" />
              <option
                v-for="album in parentAlbums"
                :key="album.id"
                :value="album.id"
              >
                {{ album.title }}
              </option>
            </b-select>
          </b-field>
          <b-field label="Lajittelujärjestys">
            <b-select
              v-model="albumDetails.sort_order"
              expanded
            >
              <option
                selected="selected"
                value="title"
              >
                Nimi (nouseva)
              </option>
              <option value="-title">
                Nimi (laskeva)
              </option>
              <option value="date">
                Päiväys (nouseva)
              </option>
              <option value="-date">
                Päiväys (laskeva)
              </option>
            </b-select>
          </b-field>
          <b-field>
            <b-switch v-model="albumDetails.public">
              Julkinen
            </b-switch>
          </b-field>
          <b-field>
            <b-switch v-model="albumDetails.show_metadata">
              Näytä metatiedot
            </b-switch>
          </b-field>
          <b-field>
            <b-switch v-model="albumDetails.show_location">
              Näytä sijaintitiedot
            </b-switch>
          </b-field>
          <b-field>
            <b-switch v-model="albumDetails.downloadable">
              Salli lataukset
            </b-switch>
          </b-field>

          <b-field
            grouped
            position="is-right"
          >
            <b-button
              type="is-info"
              :class="{ 'is-loading': loading }"
              :disabled="!albumDetails.title || !albumDetails.description"
              @click="Submit"
            >
              Tallenna
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
  name: 'AlbumEdit',
  data () {
    return {
      loading: true,
      error: false,
      date: null,
      parentAlbums: {},
      albumDetails: {}
    }
  },
  created () {
    this.getData()
    this.getParentAlbums()
  },
  methods: {
    getData: function () {
      this.error = false
      axios.get('albums/' + this.$route.params.id)
        .then(response => {
          this.albumDetails = response.data
          this.loading = false
          this.stringToDate()
        })
        .catch(error => {
          console.log(error)
          this.error = true
          this.loading = false
        })
    },
    getParentAlbums: function () {
      axios.get('albums')
        .then(response => {
          this.parentAlbums = response.data.results
          this.stringToDate()
        })
        .catch(error => {
          console.log(error)
          this.error = true
        })
    },
    stringToDate: function () {
      const dateString = this.albumDetails.date
      this.date = new Date(dateString)
    },
    formatDateToISOString: function () {
      const date = this.date
      return new Date(date.getTime() - (date.getTimezoneOffset() * 60000))
        .toISOString()
        .split('T')[0]
    },
    Submit: function () {
      this.albumDetails.date = this.formatDateToISOString()
      this.loading = true
      axios.patch('albums/' + this.albumDetails.id, this.albumDetails).then(() => {
        this.loading = false
        this.$buefy.toast.open({
          message: 'Albumin tiedot päivitetty.',
          type: 'is-info',
          duration: 3000
        })
        this.$router.push('/album/' + this.albumDetails.id)
      })
        .catch(error => {
          console.log(error)
          this.error = true
          this.loading = false
          this.$buefy.toast.open({
            message: 'Albumin muokkaus epäonnistui',
            type: 'is-danger',
            duration: 3000
          })
        })
    }
  }
}
</script>

<style scoped>

</style>
