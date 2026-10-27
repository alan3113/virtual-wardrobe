import type { ClothingItem, Outfit, Product, ShoppingAnalysis, WardrobeGap } from '../types'
const img=(id:string)=>`/images/${id}.jpg`
export const demoItems:ClothingItem[] = [
  {id:'1',name:'White Oxford Shirt',category:'Tops',color:'White',style:'Classic',material:'Cotton',occasion:'Work',season:'All season',image_url:img('photo-1598032895397-b9472444bf93'),created_at:'2026-09-24'},
  {id:'2',name:'Navy Linen Shirt',category:'Tops',color:'Navy',style:'Relaxed',material:'Linen',occasion:'Casual',season:'Summer',image_url:img('photo-1602810318383-e386cc2a3ccf'),created_at:'2026-09-22'},
  {id:'3',name:'Black Straight Jeans',category:'Bottoms',color:'Black',style:'Minimal',material:'Denim',occasion:'Everyday',season:'All season',image_url:img('photo-1542272604-787c3835535d'),created_at:'2026-09-20'},
  {id:'4',name:'Beige Tailored Chinos',category:'Bottoms',color:'Beige',style:'Classic',material:'Cotton',occasion:'Work',season:'All season',image_url:img('photo-1473966968600-fa801b869a1a'),created_at:'2026-09-18'},
  {id:'5',name:'White Leather Sneakers',category:'Shoes',color:'White',style:'Minimal',material:'Leather',occasion:'Everyday',season:'All season',image_url:img('photo-1676379827610-c380c52db0c6'),created_at:'2026-09-15'},
  {id:'6',name:'Brown Leather Loafers',category:'Shoes',color:'Brown',style:'Classic',material:'Leather',occasion:'Work',season:'All season',image_url:img('photo-1533867617858-e7b97e060509'),created_at:'2026-09-12'},
  {id:'7',name:'Navy Structured Blazer',category:'Outerwear',color:'Navy',style:'Tailored',material:'Wool',occasion:'Work',season:'Autumn',image_url:img('photo-1740710748146-a15d840d6f40'),created_at:'2026-09-10'},
  {id:'8',name:'Brown Bomber Jacket',category:'Outerwear',color:'Brown',style:'Relaxed',material:'Cotton',occasion:'Casual',season:'Autumn',image_url:img('photo-1520975954732-35dd22299614'),created_at:'2026-09-08'},
  {id:'9',name:'Cream Knit Poncho',category:'Tops',color:'Cream',style:'Minimal',material:'Knit',occasion:'Casual',season:'Winter',image_url:img('photo-1434389677669-e08b4cac3105'),created_at:'2026-09-04'},
  {id:'10',name:'Black Leather Belt',category:'Accessories',color:'Black',style:'Classic',material:'Leather',occasion:'Everyday',season:'All season',image_url:img('photo-1603805752838-aa579d77da72'),created_at:'2026-08-27'},
]
export const demoOutfits:Outfit[]=[
  {id:'o1',name:'The Weekend Edit',item_ids:['2','4','5'],occasion:'Weekend',description:'Effortless layers for your off-duty days.',saved:true,created_at:'2026-09-25'},
  {id:'o2',name:'Modern Classic',item_ids:['1','3','7','6'],occasion:'Work',description:'Sharp pieces with a relaxed point of view.',saved:true,created_at:'2026-09-22'},
  {id:'o3',name:'Easy Elegance',item_ids:['9','4','6'],occasion:'Everyday',description:'Soft texture meets understated tailoring.',saved:false,created_at:'2026-09-20'},
]
export const demoGaps:WardrobeGap[]=[
  {id:'g1',category:'Accessories',title:'The finishing touch',description:'A versatile watch or everyday accessory would bring more personality to your looks.',priority:'High',image_url:img('photo-1523275335684-37898b6baf30'),pairs_with:['White Oxford Shirt','Navy Blazer']},
  {id:'g2',category:'Outerwear',title:'A lighter layer',description:'A neutral overshirt can bridge the gap between warmer afternoons and cool evenings.',priority:'Medium',image_url:img('photo-1596755094514-f87e34085b2c'),pairs_with:['Black Jeans','White Sneakers']},
  {id:'g3',category:'Shoes',title:'Something for the weekend',description:'A darker casual shoe would give your everyday outfits another direction.',priority:'Low',image_url:img('photo-1525966222134-fcfa99b8ae77'),pairs_with:['Beige Chinos','Cream Knit Sweater']},
]
export const demoProduct:Product={id:'p1',name:'Blue Denim Overshirt',brand:'ARKET',price:'$89',category:'Outerwear',color:'Blue',image_url:img('photo-1596755094514-f87e34085b2c')}
export const demoAnalysis:ShoppingAnalysis={id:'a1',product:demoProduct,wardrobe_match:91,similar_item_owned:1,compatible_items:7,new_outfits:5,duplicate_risk:'Low',wardrobe_gap:false,explanation:'This piece works beautifully with what you already own. Its relaxed blue texture adds variety while creating fresh combinations with your everyday essentials.',outfit_item_ids:[['3','5'],['1','4'],['2','6']]}
export const editorial={hero:img('photo-1515886657613-9f3515b0c78f'),studio:img('photo-1539109136881-3be0616acf4b'),shopping:img('photo-1483985988355-763728e1935b')}
