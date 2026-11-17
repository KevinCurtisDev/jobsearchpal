# DPIA 0002 · Interview practice recordings

**Status:** Draft. Sign-off required before Stage 10 launch.

## 1. Processing
The user records an answer. **Video stays in the browser and is never uploaded.** Only the
audio track is uploaded, transcribed by a self-hosted model (faster-whisper) in our worker,
then deleted (max 24 hours). Transcript and delivery metrics (words per minute, fillers,
pauses, structure) are kept 30 days unless the user ticks "Keep". AI content feedback sends
the redacted transcript only. Basis: consent (`voice_practice`).

## 2. Necessity and proportionality
Text practice is available without any recording. No face, emotion, voice-tone or
appearance analysis (CLAUDE.md rule 6; EU AI Act prohibits emotion recognition in some
contexts and we avoid it entirely). Voice is not used to identify anyone (not biometric
processing under Art 9: no unique identification).

## 3. Risks
| Risk | Likelihood | Severity |
| --- | --- | --- |
| Audio retained longer than intended | Remote | Medium — retention job + test |
| Transcript contains third-party details | Possible | Low — redaction before AI; 30-day limit |

## 4. Measures
Browser-only video (tested: no video upload endpoint exists), pre-signed upload with 20 MB
limit, deletion after processing, nightly safety-net retention, export and delete.

## 5. Residual risk — to be completed
## 6. Sign-off
