// Seeded violation: #elif expands a macro that produces the defined operator.
#define KV_HAS_DEBUG defined(KV_DEBUG)

#if 0
#elif KV_HAS_DEBUG
namespace kv::rule_19_1_1_elif::bad {
constexpr int kDebug = 1;
}  // namespace kv::rule_19_1_1_elif::bad
#endif
