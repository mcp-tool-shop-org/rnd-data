# via_bf16 rung (R&D, 2026-10-19, rule 1): the exact convert path Super-VL took, on a small Apache model on Colab CPU.
# pin_window at role-set #98 head (uploaded to /content); one MODELS entry added for the rung, nothing else changed.
import sys
sys.path.insert(0, "/content")
import pin_window as pw  # noqa: E402

pw.MODELS.append({"served_as": "qwen2.5-0.5b-instruct", "how": "convert", "repo": "Qwen/Qwen2.5-0.5B-Instruct",
                  "revision": "7ae557604adf67be50417f59c2c2f167def9a775", "tokenizer_check": True, "via_bf16": True})
raise SystemExit(pw.main())
