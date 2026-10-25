import {getLanguage,questName,mountLanguageSelector,translate} from './language-selector.js';
export {getLanguage,questName,mountLanguageSelector,translate};
export async function loadQuestNames(url='/data/forever-v30-bilingual-quests.json') {
 const response=await fetch(url);if(!response.ok)throw new Error(`Quest names unavailable: ${response.status}`);
 const payload=await response.json();if(payload.version!=='3.0'||!Array.isArray(payload.quests))throw new Error('Unexpected quest dataset');
 return new Map(payload.quests.map(quest=>[Number(quest.id),quest]));
}
export function displayQuestById(id,questMap,language=getLanguage()) {
 const q=questMap.get(Number(id));return q?questName(q,language):`Quest #${id}`;
}
export function bindQuestNameElements(root,questMap) {
 function render(){root.querySelectorAll('[data-quest-id]').forEach(el=>{el.textContent=displayQuestById(el.dataset.questId,questMap);});}
 document.addEventListener('forever:language-changed',render);render();return render;
}
