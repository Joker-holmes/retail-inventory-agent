# Historical versions

The experimental V8-V13 development history is intentionally kept outside the core public API.

Recommended practice:

- keep stable production-style code under `src/`
- keep reproducible historical experiments here
- do not place private datasets or credentials in the repository
- use Git history for major public releases

Historical experiments can be added later after sensitive data and machine-specific paths have been removed.
