# v2.2 — Native quest accessor whitelist

This replaces the broad v2.1 introspection with a fixed list of ID-keyed read-only QuestieDB accessors. `GetAll` needs `requestedKeys` and `GetAllIds` ignores the quest ID; neither is called.

CI requires 24 quest IDs to return Exists, name, requiredRaces, requiredLevel, with zero invocation errors. Quest 94414 must have race mask zero. These checks are native data consistency checks, NOT in-game availability verification or leveling route optimization.

Run workflow **Forever Native Quest Accessor v2.2**, download artifact `forever-native-quest-v22` and upload JSON and LOG. Source SHA pinned in workflow.
