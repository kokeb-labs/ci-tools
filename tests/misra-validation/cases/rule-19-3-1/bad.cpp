// Seeded violation: the stringising and token-pasting operators.
#define KV_NAME(x) #x
#define KV_JOIN(a, b) a##b

namespace kv::rule_19_3_1::bad {

constexpr const char* kName = KV_NAME(adc);
constexpr int KV_JOIN(k, Value) = 1;

}  // namespace kv::rule_19_3_1::bad
