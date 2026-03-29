Polish Clue chrome, hide diagnostics by default, and improve stock seat play

- hide Clue diagnostics behind an explicit `Show Diagnostics` toggle and filter trace events out of the normal table logs unless diagnostics are enabled
- add a shared Clue footer across pages and strengthen the home-page hero contrast so the setup copy is readable again
- shrink the board again and redraw movement plus secret-passage routes as anchored curved paths with room-to-room color fades instead of blunt straight lines through rooms
- tighten autonomous accusation pacing with a shared evidence gate so heuristic and LLM seats stop accusing on the first merely-good hypothesis
- improve heuristic movement so stock seats steer toward more informative rooms rather than always taking the nearest legal target
- give stock autonomous seats distinct in-character public lines for suggestions, accusations, and secret-passage moves, and pass persona guidance through the LLM prompt path
- add regression coverage for the updated page chrome, heuristic accusation delay, heuristic move choice, stock-seat public flavor, and LLM accusation hold behavior
- verify with `pytest c:\\Users\\David\\Documents\\Local_Python\\clue\\tests`
- verify with `pytest c:\Users\David\Documents\Local_Python\clue\tests`
