# WoW Forever Optimizer v3.4 — gezielte Laufzeit-Codepfade

Kumulatives Overlay für `Evome86/wow-forever-optimizer` (v3.3 enthalten). ZIP **entpacken**, Ordnerstruktur ins Repository-Root übernehmen und committen.

**GitHub Actions:** `Forever v3.4 Targeted Runtime Codepaths` → `Run workflow` → Artefakt `forever-v34-runtime-codepaths` → `forever-v34-runtime-codepaths.json` zurückgeben.

## Inhalt
- Gezielte, priorisierte Auszüge aus Questie-Addon- und QuestieDB-Code mit 7 Zeilen Kontext für Rassenmasken und Quest-Voraussetzungen.
- Erfasst auch fehlenden Addon-Checkout, ohne falsche Bestätigung zu behaupten.
- Reproduzierbare Tests für die Audit-Logik.

## Wichtige Grenze
Ein statischer Code-Scan ist **kein** ausführbarer Laufzeittest. Der Checkout `Questie/Questie` ist nicht auf einen bestätigten Forever-Client-Build gepinnt. Daher bleiben die Maskensemantik, AND-/OR-Logik und Ingame-Spielbarkeit ausdrücklich unbestätigt; `route_gate=BLOCKED`. Die Auswertung soll die konkreten Runtime-Consumer und Test-Fixtures für v3.5 identifizieren, nicht bereits Quests freigeben.
