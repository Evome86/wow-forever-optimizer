# v1.8 Native Runtime Validation

Copy files to repository root. Run GitHub Actions > Forever Native Runtime Validation v1.8 > Run workflow. Download artifact `forever-native-runtime-v18` and upload both JSON and log.

This stage **executes** upstream QuestieDB `emulator/native-source.test.lua` in Lua 5.4, rather than claiming static text inspection verifies runtime behavior. Passing tests verify only the upstream emulator's own test assertions; they do **not** establish a validated Skyborne leveling route. The next step is a custom emulator export for the exact character and levels.
