// Seeded violation: arguments with a top-level operator, expanded next to unary minus and < without parentheses.
#include <cstdint>

#define KV_NEG(x) (-x)
#define KV_BELOW(x, lim) (x < lim)

namespace kv::rule_19_3_4::bad_unary {

std::int32_t neg(std::int32_t a, std::int32_t b) { return KV_NEG(a - b); }  // seeded
bool below(std::int32_t a, std::int32_t b) { return KV_BELOW(a | b, 10); }  // seeded

}  // namespace kv::rule_19_3_4::bad_unary
