import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
const Album = () => import('./views/Album.vue')

Vue.use(Router)

export default new Router({
  mode: 'history',
  scrollBehavior (to, from, savedPosition) {
    if (savedPosition) {
      return savedPosition
    } else {
      return { x: 0, y: 0 }
    }
  },
  routes: [
    {
      path: '/',
      name: 'home',
      component: Home
    },
    {
      path: '/album/:id',
      name: 'album',
      component: Album
      // route level code-splitting
      // this generates a separate chunk (about.[hash].js) for this route
      // which is lazy-loaded when the route is visited.
    }
  ]
})
