-- Full native Forever quest export; read-only accessors, no manual merge.
local config=dofile('src/config.lua')
config.correctionManifest=dofile('src/corrections/manifest.lua')
local client=dofile('emulator/client.lua')
local emulator=dofile('emulator/metadata.lua')
client.reset()
client.install({expansion='Forever',gameType='camelot',season='SoD'})
emulator.install(config.addonName,emulator.parse('QuestieDB.toc'))
local db,files=emulator.loadAddon('QuestieDB.toc',config.addonName)
assert(db.flavor.name=='Forever','unexpected flavor')
local q=db.Quest
assert(type(q)=='table' and type(q.GetAllIds)=='function','missing Quest.GetAllIds')
local function esc(v)
 return tostring(v):gsub('%%','%%25'):gsub('\t','%%09'):gsub('\n','%%0A'):gsub('\r','%%0D')
end
local function emit(...)
 local t={...}; for i=1,#t do t[i]=esc(t[i]) end
 io.write(table.concat(t,'\t'),'\n')
end
local function serialize(v,seen)
 local kind=type(v)
 if kind=='nil' then return 'null' end
 if kind=='number' then assert(v==v and v~=math.huge and v~=-math.huge);return tostring(v) end
 if kind=='boolean' then return tostring(v) end
 if kind=='string' then
  return '"'..v:gsub('\\','\\\\'):gsub('"','\\"'):gsub('\n','\\n'):gsub('\r','\\r'):gsub('\t','\\t'):gsub('%c',function(c)return string.format('\\u%04x',string.byte(c)) end)..'"'
 end
 assert(kind=='table','unsupported value type '..kind)
 assert(not seen[v],'cyclic table encountered')
 seen[v]=true
 local keys={}; for k in pairs(v) do assert(type(k)=='number' or type(k)=='string','invalid key');keys[#keys+1]=k end
 table.sort(keys,function(a,b) if type(a)==type(b) then return a<b end return type(a)<type(b) end)
 local out={}; for _,k in ipairs(keys) do out[#out+1]='"'..tostring(k)..'":'..serialize(v[k],seen) end
 seen[v]=nil
 return '{'..table.concat(out,',')..'}'
end
local ids=q.GetAllIds()
assert(type(ids)=='table','GetAllIds returned non-table')
local sorted={}; local unique={}
for k,v in pairs(ids) do
 local id=nil
 if type(v)=='number' and v>0 and v%1==0 then id=v
 elseif type(k)=='number' and k>0 and k%1==0 and v==true then id=k end
 if id then unique[id]=true end
end
for id in pairs(unique) do sorted[#sorted+1]=id end
table.sort(sorted)
assert(#sorted>1000,'unexpectedly few quest IDs: '..#sorted)
emit('META','flavor',db.flavor.name)
emit('META','source_file_count',#files)
emit('META','quest_count',#sorted)
local fields={'Exists','name','questLevel','requiredLevel','requiredMaxLevel','requiredRaces','requiredClasses','requiredSpecialization','preQuestSingle','preQuestGroup','nextQuestInChain','startedBy','finishedBy','zoneOrSort','objectives','objectivesText','exclusiveTo','inGroupWith','childQuests','breadcrumbForQuestId','breadcrumbs','availableStartingWith','availableUntilCompleted','questFlags','specialFlags','parentQuest','disabledByQuest'}
for _,f in ipairs(fields) do assert(type(q[f])=='function','missing accessor '..f) end
local error_count=0;local value_count=0
for _,id in ipairs(sorted) do
 emit('QUEST',id)
 for _,f in ipairs(fields) do
  local ok,v=pcall(q[f],id)
  if not ok then error_count=error_count+1;emit('ERROR',id,f,tostring(v):sub(1,500))
  elseif v~=nil then
   local encoded_ok,encoded=pcall(serialize,v,{})
   if not encoded_ok then error_count=error_count+1;emit('ERROR',id,f,tostring(encoded):sub(1,500))
   else value_count=value_count+1;emit('VALUE',id,f,encoded) end
  end
 end
end
emit('META','value_count',value_count)
emit('META','error_count',error_count)
emit('META','complete','true')
assert(error_count==0,'accessor/serialization errors: '..error_count)
