<template>
  <main class="container">
    <section class="section">
      <h1 class="title">
        Albumit
      </h1>

      <h2 class="subtitle">
        Satunnaisia kuvakokoelmia vuosien varrelta.
      </h2>
    </section>
    <AlbumList />
  </main>
</template>

<script>
// @ is an alias to /src
import AlbumList from '@/components/AlbumList'

export default {
  name: 'Home',
  components: {AlbumList},
}
</script>
