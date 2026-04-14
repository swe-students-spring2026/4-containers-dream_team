# MongoDB Joke Record Specification
This document defines the JSON shape for joke records stored in MongoDB.
## Record Fields
- `text`: string containing the potential joke text.
- `username`: string containing the username submitted with the text.
- `classification`: integer where `0` means the text is not a joke and `1` means the text is a joke.
- `funniness_score`: integer where the value is `-1` when `classification` is `0`, otherwise a value from `1` to `100`.
## Example Record
```json
{
  "text": "Why did the developer go broke? Because he used up all his cache.",
  "username": "joke_fan_01",
  "classification": 1,
  "funniness_score": 84
}
```
