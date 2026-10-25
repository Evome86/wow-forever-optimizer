-- QuestieDB's actual Source loader; no manual correction merge.
local config = dofile('src/config.lua')
config.correctionManifest = dofile('src/corrections/manifest.lua')
local client = dofile('emulator/client.lua')
local emulator = dofile('emulator/metadata.lua')
client.reset()
client.install({expansion='Forever', gameType='camelot', season='SoD'})
emulator.install(config.addonName, emulator.parse('QuestieDB.toc'))
local db, files = emulator.loadAddon('QuestieDB.toc', config.addonName)
assert(db.flavor.name == 'Forever', 'wrong flavor')
local ids = {94414,92595,92596,92646,92840,92850,92860,92871,92947,93089,93090,93320,93737,93738,93746,93835,93836,93958,94369,94411,94413,94946,95349,99260}
local function escape(v)
  v = tostring(v)
  return (v:gsub('%%','%%25'):gsub('\t','%%09'):gsub('\n','%%0A'):gsub('\r','%%0D'))
end
local function emit(...)
  local values = {...}
  for i=1,#values do values[i]=escape(values[i]) end
  io.write(table.concat(values,'\t'),'\n')
end
local function serialize(v, depth, seen)
  local kind=type(v)
  if kind~='table' then return tostring(v) end
  if depth>=3 then return '{DEPTH_LIMIT}' end
  if seen[v] then return '{CYCLE}' end
  seen[v]=true
  local keys={}
  for k in pairs(v) do keys[#keys+1]=k end
  table.sort(keys,function(a,b)return tostring(a)<tostring(b) end)
  local pieces={}
  for i=1,math.min(#keys,40) do
    local k=keys[i]
    pieces[#pieces+1]=tostring(k)..'='..serialize(v[k],depth+1,seen)
  end
  seen[v]=nil
  if #keys>40 then pieces[#pieces+1]='TRUNCATED' end
  return '{'..table.concat(pieces,',')..'}'
end
emit('META','flavor',db.flavor.name)
emit('META','source_file_count',#files)
local quest=db.Quest
assert(type(quest)=='table','db.Quest not table')
local names={}
for key,value in pairs(quest) do
  if type(key)=='string' then
    names[#names+1]={key=key,kind=type(value)}
  end
end
table.sort(names,function(a,b)return a.key<b.key end)
for _,entry in ipairs(names) do emit('METHOD',entry.key,entry.kind) end
-- Only documented, quest-ID keyed, read-only accessors. No global GetAllIds or GetAll.
local fields={'Exists','name','questLevel','requiredLevel','requiredMaxLevel','requiredRaces','requiredClasses','requiredSpecialization','preQuestSingle','preQuestGroup','nextQuestInChain','startedBy','finishedBy','zoneOrSort','objectives','objectivesText','exclusiveTo','inGroupWith','childQuests','breadcrumbForQuestId','breadcrumbs','availableStartingWith','availableUntilCompleted'}
for _,field in ipairs(fields) do
  local fn=quest[field]
  assert(type(fn)=='function','required accessor missing: '..field)
  for _,id in ipairs(ids) do
    local ok,value=pcall(fn,id)
    if not ok then emit('ERROR',id,field,tostring(value):sub(1,250))
    elseif value~=nil then emit('VALUE',id,field,type(value),serialize(value,0,{})) end
  end
end
emit('META','complete','true')
