# Privacy check

## Reference

Shuning Zhang, Xin Yi, Shixuan Li, Haobin Xing, and Hewu Li.
2025. PrivCAPTCHA: Interactive CAPTCHA to Facilitate Effective
Comprehension of APP Privacy Policy. Proceedings of the 2025 CHI
Conference on Human Factors in Computing Systems, Article 385, 1–20.
https://doi.org/10.1145/3706598.3713928

## Our adaptation

Our privacy check runs in the browser before the first comparison,
rather than during Android app registration. The policy is written
by hand rather than extracted with GPT-4o.

The structured policy below uses these fields:

[Category] - [Data we collect] - [How it is sent or kept] - [Who sees or receives it] - [What it is used for]

The final field is our addition for the pink purpose chunks.

## Structured policy

[Steam profile] - [SteamID64, Display name, Avatar, Profile link, Profile visibility] - [Looked up over HTTPS, Saved in the app's database] - [Steam Web API, Anyone using this app] - [Side-by-side comparison]

[Game library] - [Owned games, Total playtime, Recent playtime, Last-played dates, Screenshot links] - [Library saved in the database, Screenshot links cached for 1 hour; images stay on Steam] - [Steam Web API, Anyone using this app] - [Library comparison, Account value estimate]

[Achievements] - [Unlocked achievements, Unlock dates, Locked achievements] - [Saved in the app's database, Gemini only when you click Get tips, SteamID64 never sent to Gemini] - [Steam Web API, Google Gemini, Anyone using this app] - [Comparison charts, AI tips]

[Comparison history] - [Who you compared, When you compared] - [Saved in the app's database, Kept until removed or the database resets] - [Anyone using this app] - [History page, Recent opponents]

## Interaction

- Show a legend before the four category screens.
- Ask users to click every orange data-collection chunk.
- Correct clicks turn the chunk white with orange text.
- Wrong-color clicks do nothing.
- Start with nine chunks. Each new correct click reveals one more.
- If no unclicked orange chunk is visible while chunks remain hidden,
  reveal all remaining chunks.
- Put a pink purpose chunk last.
- After all orange chunks are found, reveal all chunks and block grid
  interaction for five seconds before advancing.
- Closing the dialog does not save completion.
- Only Continue on the final screen saves completion.

## Browser storage

The localStorage key `privcap-version` stores the completed policy
version. It contains no SteamID64 or profile information.

Increase PRIVCAP_VERSION in frontend/src/lib/privcap.ts whenever the
policy changes. Clearing site data also brings the check back.

If browser storage is blocked, completion still allows the current
comparison, but it may not be remembered for the next visit.

## Scope

This is a privacy education interaction, not a security or anti-bot
control. It does not prevent direct API calls.

Comparison requests are blocked until completion. Profile previews
and landing-page profile checks may already have requested public
Steam information before the check opens.

The full policy at /privacy explains retention, sharing, and choices.
Gemini receives the game name and up to 10 locked achievements with
their names, descriptions, and global unlock percentages. It does not
receive SteamID64s or profile details.