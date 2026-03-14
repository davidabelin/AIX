# AIX Running List of Assorted Changes

## AIX
- *Fonts and font sizes* need to be standardized and well-proportioned *across the board*

### /c4/rl 
- needs 'i' popups or explanatory notes for hyperparams, opponents, etc
- lose 'seed' box
- force limit on number episodes
- explanation panel for developers about how tabular Q-learning policy agents are structured, used, implemented in pseudocode, anything else interesting

### /c4/training
![alt text](image.png)
- fix jumble of different fonts and sizes, improve 'i' info symbols or icons
- Make a 'Delete' button for sessions, too, but keep 'Exclude',...
- lose the "How are "samples from moves" calculated?" box -- it's trivial here. Just say: "Samples: 395 (minimum 20) from 26 sessions. Ready to train."

### /c4/play
- Board panel: put Notes (now in upper right corner) in its own panel, below the Board panel and same width but constant height that fits longest content, so it's not so jerky and annoying every time it updates.
 - Change wording to say 'Estimated likelihood choosing a column will result in a win for the player'.
- Do a cleanup pass on all the fonts and fonts sizes that appear on this page, make consistent, smooth, and viewer-friendly in annticipation of actual human gameplay

### /c4/arena
- fonts!
- record the column probs that each agent sees in realtime
 - in replay give option to see them like in /c4/play
 - flash the choice of column as each agent makes it, timed proportional to replay speed
**attention to style *flourishes* and small details like this flashing *matters*** and creates an overall vibe or feel I want to evoke consistently across AIX and its arms.

### polyfolds-dot-aix-labs.uw.r.appspot.com
This isn't right, this url should point to what is currently at https://polyfolds-dot-aix-labs.uw.r.appspot.com/polyfolds/ (and aix-labs.uw.r.appspot.com/polyfolds)
![Polyfolds AIX-service stand-alone should not land here!](image-1.png)

### directed-sonar-429119-u2.uw.r.appspot.com/inventory
- **"Not Found"**
 - *"The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again."*
- linked to from aix-labs.uw.r.appspot.com/drl/

### aix-labs.uw.r.appspot.com/drl/
- **FIX**:
 - "*Live sister app*: https://directed-sonar-429119-u2.uw.r.appspot.com" / *"Open in DRL"* buttons / any other bad links
  - points to **RPS Agent Lab** *not* to the **DRL** "sister app"
   - **RPS/play** at directed-sonar-429119-u2.uw.r.appspot.com/play STILL (!) has "counter-revolutionary" as default opponent, let's have active_agent followed by strong to weak heuristic agents
   - rps/play should be like aix-labs.uw.r.appspot.com/rps/play
    - aix-labs/rps/play has pretty good fonts and size proportionalities: still needs work, but it's better than most other pages; could serve as a first-pass font-fix and reproprotioning aim-point for the others
  - this is why **drl/inventory** wasn't found
