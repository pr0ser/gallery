import Vue from 'vue'
import Router from 'vue-router'
import Home from './views/Home.vue'
import Album from './views/Album.vue'
const Login = () => import('./views/Login.vue')
const AlbumNew = () => import(/* webpackChunkName: "authenticated" */ './views/AlbumNew')
const AlbumEdit = () => import(/* webpackChunkName: "authenticated" */ './views/AlbumEdit.vue')
const Upload = () => import(/* webpackChunkName: "authenticated" */ './views/Upload.vue')

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
      props: true,
      meta: { requiresAuth: true }
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    }
  ]
})
