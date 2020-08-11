import axios from 'axios'

const API_URL = process.env.VUE_APP_APIBASEURL
const headers = { 'Content-Type': 'application/json' }

const instance = axios.create({
  baseURL: API_URL,
  headers: headers
})

export default instance
