import axios from 'axios'
export const demoMode = import.meta.env.VITE_DEMO_MODE !== 'false'
export const client = axios.create({baseURL:import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',timeout:15000})
client.interceptors.request.use(config=>{const token=localStorage.getItem('wardrobe_token');if(token)config.headers.Authorization=`Bearer ${token}`;return config})
export const wait=(ms=350)=>new Promise<void>(resolve=>setTimeout(resolve,ms))
export function loadLocal<T>(key:string,fallback:T):T {try {const value=localStorage.getItem(key);return value?JSON.parse(value) as T:fallback}catch{return fallback}}
export function saveLocal<T>(key:string,value:T){localStorage.setItem(key,JSON.stringify(value))}
