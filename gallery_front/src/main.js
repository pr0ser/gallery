import Vue from 'vue'
import App from './App.vue'
import router from './router'
import Buefy from 'buefy'
import store from './store'
import { library } from '@fortawesome/fontawesome-svg-core'
import {
  faUpload,
  faEdit,
  faTrashAlt,
  faCog,
  faSignInAlt,
  faSignOutAlt,
  faCaretDown,
  faPlus,
  faImage,
  faLock,
  faAngleLeft,
  faAngleRight,
  faExclamationCircle,
  faUser
} from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'

library.add(
  faUpload,
  faEdit,
  faTrashAlt,
  faCog,
  faSignInAlt,
  faSignOutAlt,
  faCaretDown,
  faPlus,
  faImage,
  faLock,
  faAngleLeft,
  faAngleRight,
  faExclamationCircle,
  faUser
)

Vue.component('vue-fontawesome', FontAwesomeIcon)

require('@/store/subscriber')

Vue.use(Buefy, {
  defaultIconComponent: 'vue-fontawesome',
  defaultIconPack: 'fas'
})

Vue.config.productionTip = false

router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // this route requires auth, check if logged in
    // if not, redirect to login page.
    if (!store.getters['auth/authenticated']) {
      next({
        path: '/login',
        query: { redirect: to.fullPath }
      })
    } else {
      next()
    }
  } else {
    next() // make sure to always call next()!
  }
})

store.dispatch('auth/attempt', localStorage.getItem('token')).then(() => {
  new Vue({
    router,
    store,
    render: h => h(App)
  }).$mount('#app')
})

Vue.filter('formatDate', function (value) {
  if (value) {
    const date = new Date(value)
    const year = date.getFullYear()
    const month = date.getMonth() + 1
    const day = date.getDate()

    return day + '.' + month + '.' + year
  }
})

Vue.filter('truncate', function (text, stop, clamp) {
  return text.slice(0, stop) + (stop < text.length ? clamp || '...' : '')
})

Vue.filter('striphtml', function (value) {
  const div = document.createElement('div')
  div.innerHTML = value
  const text = div.textContent || div.innerText || ''
  return text
})
