<template>
  <div id="album-actions-button">
    <b-dropdown
      position="is-bottom-left"
    >
      <button
        slot="trigger"
        class="button is-dark"
        type="button"
      >
        <b-icon
          icon="cog"
          pack="fas"
        />
        <span>Muokkaa</span>
        <b-icon
          icon="caret-down"
          pack="fas"
        />
      </button>

      <b-dropdown-item
        aria-role="listitem"
        has-link
      >
        <router-link
          :to="{ name: 'albumEdit', params: {id: albumId }}"
        >
          <div class="media">
            <b-icon
              class="media-left"
              icon="edit"
              pack="fas"
            />
            <div class="media-content">
              <h3>Muokkaa</h3>
            </div>
          </div>
        </router-link>
      </b-dropdown-item>

      <b-dropdown-item
        @click="confirmAlbumDelete"
      >
        <div class="media">
          <b-icon
            class="media-left"
            icon="trash-alt"
            pack="fas"
          />
          <div class="media-content">
            <h3>Poista</h3>
          </div>
        </div>
      </b-dropdown-item>
    </b-dropdown>
  </div>
</template>
<script>
import axios from '@/axios'

export default {
  name: 'AlbumActionsButton',
  props: {
    albumId: {
      type: Number,
      required: true
    }
  },
  methods: {
    confirmAlbumDelete () {
      this.$buefy.dialog.confirm({
        message: 'Haluatko poistaa albumin?',
        confirmText: 'Poista',
        type: 'is-danger',
        hasIcon: false,
        cancelText: 'Peruuta',
        onConfirm: () => this.deleteAlbum()
      })
    },
    deleteAlbum () {
      axios.delete('albums/' + this.albumId).then(response => {
        this.$buefy.toast.open({
          message: 'Albumi poistettiin.',
          type: 'is-info',
          duration: 3000
        })
        this.$router.push('/')
      })
        .catch(error => {
          console.log(error)
          this.$buefy.toast.open({
            message: 'Albumin poisto epäonnistui.',
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
