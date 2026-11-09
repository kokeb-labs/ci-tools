// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::rule_4_1_3_signed_overflow::bad_edge {

std::int32_t product(std::int32_t a, std::int32_t b) { return a * b; }  // seeded
std::int32_t difference(std::int32_t a, std::int32_t b) { return a - b; }  // seeded

}  // namespace kv::rule_4_1_3_signed_overflow::bad_edge
