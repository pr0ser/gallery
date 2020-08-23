import Vue from 'vue'
import App from './App.vue'
import router from './router'
import {
  Navbar,
  Loading,
  Notification,
  Toast, Field, Input,
  Datepicker,
  Select,
  Switch,
  Button,
  Upload,
  Icon,
  Progress
} from 'buefy'
import store from './store'

require('@/store/subscriber')

Vue.use(Navbar)
Vue.use(Loading)
Vue.use(Notification)
Vue.use(Toast)
Vue.use(Field)
Vue.use(Input)
Vue.use(Datepicker)
Vue.use(Select)
Vue.use(Switch)
Vue.use(Button)
Vue.use(Upload)
Vue.use(Icon)
Vue.use(Progress)

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
