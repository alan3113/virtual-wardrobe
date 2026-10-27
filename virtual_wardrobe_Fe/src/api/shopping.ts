import {client,demoMode,wait} from './client'
import {demoAnalysis} from '../data/demo'
import type {Product,ShoppingAnalysis} from '../types'
export async function analyzePurchase(product:Product):Promise<ShoppingAnalysis>{if(demoMode){await wait(1500);return {...demoAnalysis,id:crypto.randomUUID(),product}}const {data}=await client.post<ShoppingAnalysis>('/shopping/analyze',{product_id:product.id});return data}
