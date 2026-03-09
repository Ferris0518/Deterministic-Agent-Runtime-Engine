## 1. Transport envelope cutover

- [x] 1.1 Remove `TransportEnvelope.event_type` and legacy raw payload acceptance from `dare_framework/transport/types.py`
- [x] 1.2 Update default channel and dispatcher so `message/action/control/select` accept only typed payload families and reply with typed payloads

## 2. Agent/runtime reply cutover

- [x] 2.1 Update `BaseAgent` transport loop and `ReactAgent` transport emitters to return typed message/action/control replies without `event_type`
- [x] 2.2 Remove `build_success_payload/build_error_payload` dict-wrapper usage from transport/runtime paths

## 3. Client/adapters/examples

- [x] 3.1 Update transport adapters (`stdio`/`websocket`/`direct`) and client event pumps to parse/render typed replies
- [x] 3.2 Update examples and CLI helpers to send typed request payloads and consume typed replies

## 4. Verification

- [x] 4.1 Update transport/runtime/example tests that still assert `event_type` or legacy raw payloads
- [x] 4.2 Run focused transport/runtime regressions and broader regression suite; sync evidence/docs/tasks
