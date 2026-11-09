// Seeded violation: a function with external linkage that no header declares.
#include <cstdint>

namespace kv::rule_6_5_1::bad {

std::int32_t exported_sum(std::int32_t a, std::int32_t b) { return (a > 100 || b > 100) ? 0 : a + b; }

}  // namespace kv::rule_6_5_1::bad
