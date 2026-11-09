// Seeded violation: #if expands a macro that produces the defined operator.
#define KV_HAS_TRACE defined(KV_TRACE)

#if KV_HAS_TRACE
namespace kv::rule_19_1_1::bad {
constexpr int kTrace = 1;
}  // namespace kv::rule_19_1_1::bad
#endif
