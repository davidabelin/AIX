Add Clue telemetry, richer deduction ranking, and table-layout polish

- add structured Clue traces for tool snapshots, seat decisions, guardrail blocks, worker cycles, and rejected actions without changing the storage schema
- persist per-turn and per-game evaluation metrics inside game state, including latency, fallback, accusation, rejection, completion, and guardrail counters
- upgrade suggestion ranking from marginal scoring to information-gain scoring with repeat penalties and lightweight opponent-history hooks
- expose richer private debug payloads for autonomous seats, including entropy, top hypotheses, accusation confidence, and top-suggestion reasoning
- enforce tool-snapshot sampling budgets and pass explicit LLM turn timeouts through the OpenAI client while recording the active latency targets
- simplify the Clue game page by removing the move grid, moving public chat into the table-record column, replacing the round-table panel with the record layout, and adding LLM explainer plus seat-debug panels
- make the board more readable and interactive with shrunken board content, connection lines, room colors, character-colored markers and starts, and clickable movement targets
- fix duplicate character-name rendering in the marker grid
- update the rolling Clue to-do list only for items completed in this batch
- verify with `pytest c:\Users\David\Documents\Local_Python\clue\tests`
