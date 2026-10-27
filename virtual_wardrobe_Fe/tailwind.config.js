/** @type {import('tailwindcss').Config} */
export default { content: ['./index.html','./src/**/*.{js,ts,jsx,tsx}'], theme: { extend: { colors: { ink:'#242522', muted:'#8b8c85', cream:'#f8f7f4', line:'#e9e9e4', sage:'#66715c', pale:'#e8ece3' }, fontFamily: { sans:['DM Sans','sans-serif'], serif:['DM Serif Display','serif'] }, boxShadow: { soft:'0 20px 55px rgba(38,41,32,.07)' } } }, plugins: [] }
