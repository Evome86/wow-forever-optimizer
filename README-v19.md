# WOW Forever Optimizer v1.9 — Quest-Evidenz (kontrollierter Zwischenschritt)

## Warum noch kein behaupteter Runtime-Questexport?

Der erfolgreiche v1.8-Test bestätigt die **Prioritätsregeln der QuestieDB-Quellen**, nicht die konkrete Auflösung der 24 Questdatensätze. Ohne gesicherte QuestieDB-API wäre ein selbst gebauter Merge möglicherweise falsch. Dieses Paket exportiert deshalb **nachprüfbare Quelldaten plus erfolgreichen nativen Test**, nicht vermeintlich effektive Questwerte. `effective_quest_values_verified=false` und `route_eligibility_gate=BLOCKED_NO_EFFECTIVE_QUEST_EXPORT` sind absichtlich gesetzt.

## Benutzung

ZIP ins bestehende GitHub-Repository entpacken, committen, Actions → **Forever Quest Evidence v1.9** → Run workflow. Artifact `forever-quest-evidence-v19` herunterladen und die JSON- sowie LOG-Datei hier hochladen.

## Enthalten

- Fixierter QuestieDB-Commit und Hashes von vier Datenquellen
- Nach Quest-ID gruppierte Quelltextausschnitte für die 24 Kandidaten
- Native Lua-5.1-Tests mit vollständigem Protokoll
- Strikte Fehler bei falschem Commit, fehlenden Quellen oder fehlgeschlagenen Tests

## Danach

Gezielte Untersuchung des QuestieDB-Provider-Aufrufs und Aufbau eines **tatsächlichen effektiven Questexports**, erst danach Race/Prerequisite/XP-Routenfreigabe. Quelltextausschnitte sind auf 32 Folgezeilen begrenzt und können abgeschnitten sein; sie sind ausdrücklich keine geparsten Questwerte.
