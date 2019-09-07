import Vue from 'vue'
import App from './App.vue'
import router from './router'
import axios from 'axios'
import Buefy from 'buefy'

Vue.config.productionTip = false
Vue.use(Buefy)

Vue.use({
    install (Vue) {
    Vue.prototype.$api = axios.create({
      baseURL: process.env.VUE_APP_APIBASEURL
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
