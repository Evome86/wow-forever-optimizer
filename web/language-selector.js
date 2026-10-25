/* Include this module on your existing frontend; no route recalculation on locale changes. */
export const SUPPORTED_LANGUAGES = ['deDE', 'enUS'];
const translations = {
  deDE: {language:'Sprache',faction:'Fraktion',race:'Volk',class:'Klasse',specialization:'Spezialisierung',startLevel:'Startlevel',targetLevel:'Ziellevel'},
  enUS: {language:'Language',faction:'Faction',race:'Race',class:'Class',specialization:'Specialization',startLevel:'Start level',targetLevel:'Target level'}
};
export function getLanguage(){try{const value=localStorage.getItem('wowForeverLanguage');return SUPPORTED_LANGUAGES.includes(value)?value:'deDE';}catch{return 'deDE';}}
export function setLanguage(lang){if(!SUPPORTED_LANGUAGES.includes(lang))throw new Error('Unsupported locale');try{localStorage.setItem('wowForeverLanguage',lang);}catch{}document.documentElement.lang=lang==='deDE'?'de':'en';document.dispatchEvent(new CustomEvent('forever:language-changed',{detail:{language:lang}}));}
export function translate(key,lang=getLanguage()){return translations[lang][key]??key;}
export function questName(quest,lang=getLanguage()){return quest?.names?.[lang]||quest?.names?.enUS||quest?.name||`Quest #${quest?.id??'?'}`;}
export function mountLanguageSelector(parent){const label=document.createElement('label');const span=document.createElement('span');const select=document.createElement('select');select.id='forever-language';select.name='language';for(const [value,name] of [['deDE','Deutsch'],['enUS','English']]){const option=document.createElement('option');option.value=value;option.textContent=name;select.append(option);}select.value=getLanguage();const render=()=>{span.textContent=translate('language')+': ';select.value=getLanguage();};select.addEventListener('change',()=>setLanguage(select.value));document.addEventListener('forever:language-changed',render);label.append(span,select);parent.append(label);render();return label;}
