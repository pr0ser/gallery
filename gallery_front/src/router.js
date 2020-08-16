import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
const Album = () => import('./views/Album.vue')
const Login = () => import('./views/Login.vue')

Vue.use(Router)

export default new Router({
  mode: 'history',
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
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    }
  ]
})
