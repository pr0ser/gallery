<template>
  <router-link :to="'/album/' + id">
    <div class="card">
      <div class="card-image">
        <b-image
          v-if="coverPhotos.small"
          :src="coverPhotos.small"
          :srcset="coverPhotos.small + ' 380w, ' + coverPhotos.large + ' 600w'"
          :alt="title"
          :lazy="true"
          responsive
          ratio="1by1"
        />
        <b-image
          v-else
          :src="placeholderImg"
          alt="Ei kuvaa"
          :lazy="true"
          responsive
          ratio="1by1"
        />
      </div>
      <div class="card-content">
        <div class="content">
          <p class="title is-6">
            {{ title }}
          </p>
          <p
            class="content"
          >
            {{ description | striphtml | truncate(120) }}
          </p>
        </div>
      </div>
      <footer class="card-footer">
        <div class="card-footer-item level content">
          <div class="level-left ">
            <b-icon icon="image" />
            {{ photoCount }}
          </div>
          <div class="level-right">
            {{ date | formatDate }}
            <span
              v-if="!isPublic"
              class="icon"
            >
              <b-icon icon="lock" />
            </span>
          </div>
        </div>
      </footer>
    </div>
  </router-link>
</template>

<script>
export default {
  name: 'AlbumCard',
  props: {
    id: {
      type: Number,
      required: true
    },
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      required: false,
      default: ''
    },
    coverPhotos: {
      type: Object,
      required: false,
      default: () => {}
    },
    photoCount: {
      type: Number,
      required: true,
      default: 0
    },
    date: {
      type: String,
      required: true,
      default: ''
    },
    isPublic: {
      type: Boolean,
      required: true,
      default: true
    }
  },
  computed: {
    placeholderImg () {
      return require('../assets/no_image.png')
    }
  }
}
</script>

<style>
.card {
   display: flex;
   flex-direction: column;
   height: 100%;
   border-radius: 5px;
   margin: auto;
}
.card .image img {
  border-radius: 5px 5px 0 0;
}
.card-footer {
   margin-top: auto;
}
.card-footer-item {
  color: #737373;
  font-size: 0.86em;
}
</style>
