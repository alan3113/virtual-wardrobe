import {client,demoMode,loadLocal,saveLocal,wait} from './client'
import {demoOutfits} from '../data/demo'
import type {Outfit} from '../types'
const KEY='wardrobe_outfits'
export async function getOutfits():Promise<Outfit[]>{if(demoMode){await wait();return loadLocal(KEY,demoOutfits)}const {data}=await client.get<Outfit[]>('/outfits');return data}
export async function generateOutfits(itemId:string):Promise<Outfit[]>{if(demoMode){await wait(1200);return demoOutfits.map((outfit,i)=>({...outfit,id:`generated-${i}`,item_ids:[itemId,...outfit.item_ids.filter(id=>id!==itemId).slice(0,2)],saved:false}))}const {data}=await client.post<Outfit[]>('/outfits/generate',{item_id:itemId});return data}
export async function saveOutfit(outfit:Outfit):Promise<Outfit>{if(demoMode){await wait();const saved={...outfit,id:outfit.id.startsWith('generated')?crypto.randomUUID():outfit.id,saved:true};const outfits=loadLocal(KEY,demoOutfits);saveLocal(KEY,[saved,...outfits.filter(x=>x.id!==outfit.id)]);return saved}const {data}=await client.post<Outfit>('/outfits',outfit);return data}
export async function deleteOutfit(id:string):Promise<void>{if(demoMode){await wait();saveLocal(KEY,loadLocal(KEY,demoOutfits).filter(x=>x.id!==id));return}await client.delete(`/outfits/${id}`)}
