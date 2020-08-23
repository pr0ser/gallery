<template>
  <div
    id="album-list"
    class="container"
  >
    <div class="columns is-multiline">
      <div
        v-for="album in albumArray"
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
</template>

<script>
import AlbumCard from './AlbumCard'
export default {
  name: 'AlbumList',
  components: { AlbumCard },
  props: {
    albumArray: {
      type: Array,
      required: true
    }
  },
  methods: {
    getCoverPhotos: function (album) {
      if (album.album_cover) {
        return {
          small: album.album_cover.thumbnail_img,
          large: album.album_cover.hidpi_thumbnail_img
        }
      } else {
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
