// Seeded violation: parameters as operands of unary minus and of < without parentheses.
#include <cstdint>

#define KV_NEG(x) (-x)
#define KV_BELOW(x, lim) (x < lim)

namespace kv::rule_19_3_4::bad_unary {

std::int32_t neg(std::int32_t a, std::int32_t b) { return KV_NEG(a - b); }
bool below(std::int32_t a) { return KV_BELOW(a, 10); }

}  // namespace kv::rule_19_3_4::bad_unary
