/// <reference types="vite/client" />

// element-plus locale 型別宣告
declare module 'element-plus/dist/locale/zh-tw.mjs' {
  import type { Language } from 'element-plus/es/locale'
  const locale: Language
  export default locale
}
