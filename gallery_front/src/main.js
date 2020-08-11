import Vue from 'vue'
import App from './App.vue'
import router from './router'
import { Navbar, Loading } from 'buefy'
import store from './store'

require('@/store/subscriber')

Vue.use(Navbar)

Vue.use(Loading)

Vue.config.productionTip = false

store.dispatch('auth/attempt', localStorage.getItem('token'))

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')

Vue.filter('formatDate', function (value) {
  if (value) {
    let date = new Date(value)
    let year = date.getFullYear()
    let month = date.getMonth() + 1
    let day = date.getDate()

    return day + '.' + month + '.' + year
  }
})

Vue.filter('truncate', function (text, stop, clamp) {
  return text.slice(0, stop) + (stop < text.length ? clamp || '...' : '')
})

Vue.filter('striphtml', function (value) {
  let div = document.createElement('div')
  div.innerHTML = value
  let text = div.textContent || div.innerText || ''
  return text
})
