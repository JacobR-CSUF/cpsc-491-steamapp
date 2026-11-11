# Requirements Test Report

## Test information

- Ticket: KAN-71
- Date: November 10, 2026
- Tester: Matthew Estrada
- Environment: Local Docker Compose stack, launched from Windows PowerShell
- Starting state: Database and cache reset with `docker compose down -v`,
  followed by `docker compose up -d --build`
- Primary browser: Chrome — full requirements pass
- Secondary browser: Firefox — landing and results flow
- Profiles: Two public Steam profiles with shared games; private-profile
  and private-game-details cases; nonexistent ID 76561190000000000
- Exact public SteamID64s and browser versions were not recorded.
- Manual results below were confirmed by the tester.

## Requirements baseline

Requirements 1–20 use the Software Design Description dated
September 22, 2026.

Requirements 1 and 3 reflect the approved change to direct SteamID64
entry. Steam login and vanity URLs are outside the implemented scope.

Requirement 21 is based on KAN-68 and KAN-69 because it is absent from
this SDD version.

The Expected column uses the SDD postconditions except for the stated
scope adjustments and requirement 21.

## Requirements results

| # | Requirement | Steps | Expected | Result | Notes |
| --- | --- | --- | --- | --- | --- |
| 1 | Enter two SteamID64s | Enter two different public SteamID64s and click Compete. | Both IDs are accepted and the comparison flow starts without Steam login. | Pass | Adapted from the original authentication requirement. |
| 3 | Select player to compare | Enter a valid opponent SteamID64 and submit. | A valid target player is selected and ready for comparison. | Pass | SteamID64 entry replaces login and vanity-URL assumptions. |
| 21 | Privacy policy and CAPTCHA | Open Privacy from the footer; clear the completion marker; start a comparison; complete all four categories and Continue. | The policy is accessible and the privacy check completes before comparison requests start. | Pass | Wrong-color clicks did nothing; correct clicks selected chunks and revealed more content; five-second pauses worked. Later comparisons skipped the completed check. |
| 2 | Retrieve Steam profile data | Inspect both player headers and query the players table. | Profile data is displayed and stored/updated in the database. | Pass | Both tested players appeared in the database query. |
| 4 | Compare achievements | Review totals, completion rates, and differences for both players. | Achievement comparison results are generated and displayed. | Pass | Displayed differences matched the compared totals. |
| 5 | Calculate 100% completed games | Inspect completion counts for both players. | 100% completion counts are shown for both users. | Pass | Counts displayed successfully. |
| 6 | Interactive charts and statistics | Inspect charts and hover over bars or points. | Charts render correctly and reflect the latest comparison data. | Pass | Interactive tooltips worked. |
| 9 | General overview panel | Inspect summarized statistics; minimize and reopen the overview. | The general overview panel is rendered with both users’ summarized stats and can be minimized by the user. | Pass | Collapse and expand worked. |
| 10 | Achievement completion date on hover | Hover over unlocked and locked achievements. | A tooltip showing the completion date is displayed for the hovered achievement or trophy. | Pass | Locked achievements did not show a false unlock date. |
| 11 | Achievement detail card | Click an achievement and close its card with X. | The achievement card is displayed with its description, or is dismissed and the user is returned to the overview panel. | Pass | Description and dismissal worked. |
| 12 | Quick playtime preview | Hover over a library game tile. | A tooltip showing the game’s total playtime is displayed. | Pass | Playtime preview appeared. |
| 13 | Library game detail modal | Click a library game and inspect its details and screenshot area. | The modal is displayed with the selected game’s detailed statistics and screenshots. | Pass | Tester confirmed the modal check passed. |
| 14 | Playtime-vs-achievement graph | Open a game with unlocked achievements; expand Playtime and inspect graph points. | An interactive graph is displayed correlating playtime with achievement completion. | Pass | Playtime is estimated because Steam does not provide historical playtime. |
| 15 | Close library game modal | Click the modal’s X button. | The modal is closed and the general overview panel is displayed. | Pass | Returned to the comparison view. |
| 16 | Advanced statistics view | Expand Advanced. | The advanced view expands and displays graphs and charts tailored to a video game of interest. | Pass | Game-specific information appeared. |
| 17 | AI achievement suggestions and ratios | Select a game with locked achievements; inspect ratios and missing achievements; click Get tips. | Achievement statistics and AI-generated suggestions are displayed for the selected game. | Pass | Initially blocked by missing Gemini configuration. Added the team key, recreated the backend, and successfully retested. |
| 18 | Graph date range | Switch between 30, 60, and 90 days. | The graphs update to reflect achievement data within the selected date range. | Pass | All three ranges were checked. |
| 19 | Game-of-interest dropdown | Select a different game in Advanced. | The charts and graphs update to reflect data for the newly selected game. | Pass | Statistics and charts changed with the selection. |
| 20 | Reset search and view | Click Reset View. | All comparison data is cleared and the user is returned to the initial search screen. | Pass | Inputs and displayed results cleared. Saved database history remains available. |
| 8 | Save comparison history | Open History, find the completed comparison, and click View. | A comparison record is stored and viewable in the user’s history page. | Pass | Both players and the comparison time appeared. History is shared by users of this app instance. |
| 7 | Cache Steam API results | Repeat the same comparison and scan Redis for steam:* keys. | Data is stored in cache and subsequent requests return faster until cache expires/refreshes. | Pass | Tester confirmed faster repeat loading and Redis keys. Exact timings were not recorded. |

## Error-case retest

| Case | Expected | Result |
| --- | --- | --- |
| Nonexistent SteamID64: 76561190000000000 | Missing-profile message beneath the affected field. | Pass |
| Private Steam profile | Private-profile message beneath the affected field. | Pass |
| Public profile with private game details | Private-game-details message beneath the affected field. | Pass |
| Same valid SteamID64 twice in a comparison URL | Choose two different Steam profiles. | Pass |
| Incomplete comparison URL: /compare?a=123 | Incomplete-link message and a link back to Compare. | Pass |
| Unknown route: /does-not-exist | Page not found with a link back to Compare. | Pass |
| Backend stopped during landing-page submission | The app’s server isn’t responding. | Pass |
| Backend stopped when loading comparison results | Server-not-responding message with Try again. | Pass |
| Backend restarted, then Try again | Comparison loads successfully. | Pass |

For privacy-setting tests, Steam settings were changed for the test,
time was allowed for propagation, and Redis was cleared between cases.
Settings were restored afterward.

## Browser coverage

| Browser | Coverage | Result |
| --- | --- | --- |
| Chrome | All 21 requirements and the error-case retest above. | Pass |
| Firefox | Landing-page ID entry, privacy check, comparison results, profiles, statistics, charts, and Reset View. | Pass |

## Automated checks

| Command | Result |
| --- | --- |
| `docker compose exec backend python -m pytest` | 135 passed in 4.15 seconds |
| `docker compose exec frontend npx tsc --noEmit` | Passed; no diagnostics |
| `docker compose exec frontend npm run lint` | Passed; no reported lint errors |

## Issues and resolutions

- AI tips initially displayed “AI tips aren’t set up on this server.”
  The Gemini API key was configured in the local environment and the
  backend was recreated. The tester confirmed that tips then worked.
  No API key is included in this report.
- No remaining failures were reported in this test pass.
- No additional bug tickets were required.

## KAN-72 visual polish verification

Updated page titles, theme icon, keyboard focus outlines, shared skeletons,
image fallbacks, number formatting, and layout consistency.
Manual results below were reported by the tester.

| Check | Result | Notes |
| --- | --- | --- |
| TypeScript on prepared files | Pass | Checked the proposed replacement files against the local frontend project before copying. |
| ESLint on prepared files | Pass | Checked all changed TypeScript files using the local frontend configuration before copying. |
| Final Docker TypeScript and lint checks | Pass | Tester confirmed both Docker commands passed after the privacy-layout and landing-link fixes. |
| 375, 768, and 1280 pixel layouts | Pass | Tester checked landing, results, library modal, advanced view, History, and Privacy. No overflow or cut-off controls were reported. |
| Lighthouse accessibility: landing | Pass — 100 | Initially 96 because the help link relied on color. Added a permanent underline and retested successfully. |
| Lighthouse accessibility: results | Pass — 100 | Chrome Lighthouse accessibility audit. |
| Lighthouse accessibility: History | Pass — 100 | Chrome Lighthouse accessibility audit. |
| Lighthouse accessibility: Privacy | Pass — 100 | Chrome Lighthouse accessibility audit. |
| Final demo path | Pass | Tester confirmed Compete, privacy check, overview, library modal, advanced view, History, and Privacy all worked after the fixes. |

### Issues fixed during KAN-72 verification

- The nested privacy layout rendered duplicate HTML and body elements inside
  the root layout's main element, causing a hydration error. Replaced the
  nested layout with a fragment containing its children. The tester confirmed
  the page worked afterward.
- The landing page help link was distinguished by color until hovered.
  Added a permanent underline. The tester confirmed the Lighthouse retest
  passed.

### Verification complete

The tester confirmed that the final Docker TypeScript and lint checks passed
and the complete demo walkthrough worked after the fixes. All KAN-72
verification checks above are complete. The KAN-71 automated results above
remain the results from the earlier requirements pass.
