import Vue from 'vue'
import Router from 'vue-router'
// import store from '@/store'
import Home from './views/Home.vue'
const Album = () => import('./views/Album.vue')
const AlbumNew = () => import('./views/AlbumNew')
const AlbumEdit = () => import('./views/AlbumEdit.vue')
const Login = () => import('./views/Login.vue')
const Upload = () => import('./views/Upload.vue')

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
      path: '/album/:id/edit',
      name: 'albumEdit',
      component: AlbumEdit
    },
    {
      path: '/new-album',
      name: 'albumnew',
      component: AlbumNew,
      meta: { requiresAuth: true }
    },
    {
      path: '/upload',
      name: 'upload',
      component: Upload,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    }
  ]
})
