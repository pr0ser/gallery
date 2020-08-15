<template>
  <div class="section is-one-third">
    <div
      class="columns is-centered"
    >
      <div class="column is-two-fifths">
        <b-notification
          type="is-danger"
          has-icon
          icon-pack="fas"
          :closable="false"
        >
          <slot />
          <a
            v-if="retry"
            @click="handleRetry()"
          >
            Yritä uudelleen.
          </a>
        </b-notification>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ErrorMessage',
  props: {
    retry: {
      type: Boolean,
      required: false,
      default: false
    }
  },
  methods: {
    handleRetry: function () {
      this.$emit('retry')
    }
  }
}
</script>

<style scoped>

</style>
