// Seeded violation: ## used with __VA_ARGS__.
#define KV_LOG(fmt, ...) kv_log(fmt, ##__VA_ARGS__)  // seeded

namespace kv::rule_19_3_1::bad_va {

inline int kv_log(const char* /*fmt*/, int a = 0) { return a; }

inline int run() { return KV_LOG("x", 1); }

}  // namespace kv::rule_19_3_1::bad_va
