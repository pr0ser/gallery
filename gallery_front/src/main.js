import Vue from 'vue'
import App from './App.vue'
import router from './router'
import Buefy from 'buefy'

Vue.config.productionTip = false
Vue.use(Buefy)

import axios from 'axios'

Vue.use({
    install (Vue) {
    Vue.prototype.$api = axios.create({
      baseURL: 'http://localhost:8000/api/'
    })
  }
})

new Vue({
  router,
  render: h => h(App)
}).$mount('#app')

Vue.filter('formatDate', function (value) {
  if (value) {
    let date = new Date(value);
    let year = date.getFullYear();
    let month = date.getMonth()+1;
    let day = date.getDate();

    return day + '.' + month + '.' + year
  }
})
