# WOW Forever Optimizer v2.0 — Native Provider Probe

**Ziel:** Den konkreten, von QuestieDB selbst verwendeten Runtime-Provider und seinen Aufrufvertrag identifizieren, statt einen möglicherweise inkorrekten Lua-Merge zu erfinden.

## Installation

1. ZIP im Stammverzeichnis des bestehenden GitHub-Repositories entpacken (Dateien zusammenführen).
2. Commit und Push.
3. GitHub → Actions → **Forever Native Provider Probe v2.0** → **Run workflow**.
4. Artifact `forever-provider-probe-v20` herunterladen und `forever-provider-probe-v20.json` sowie `forever-native-v20.log` hier hochladen.

## Was v2.0 leistet

- Verifiziert den gepinnten QuestieDB-Commit und Pflichtquellen per SHA-256.
- Findet potenzielle Runtime-Provider-Funktionen mit Datei-/Zeilenbelegen (maximal 450 Einträge; Gesamtzahl wird separat berichtet).
- Exportiert den vollständigen Inhalt von `emulator/native-source.test.lua` und `src/config.lua` als zeilennummerierte Evidenz, damit der echte Initialisierungs- und Datenzugriffspfad nachgebaut werden kann.
- Führt die nativen Lua-5.1-Tests erneut aus; Fehler verhindern grünen Probe-Status.

## Strenge Grenze

**Dies ist ein Discovery-Schritt, kein effektiver Questexport.** `effective_quest_values_verified=false` und `route_eligibility_gate=BLOCKED_AWAITING_NATIVE_PROVIDER_CALL` sind absichtlich gesetzt. Erst nach Bestätigung des konkreten Provider-Aufrufs wird die Auflösung für 24 Quests und anschließend die Horde-Skyborne-Eignung implementiert. Keine erfundenen Race-Masks oder XP-Werte.
