// Edge case: zero written with more than one digit is an octal literal outside the single-digit exception.
#include <cstdint>

namespace kv::rule_5_13_3::bad_zeros {

std::uint32_t reset_value() { return 000U; }  // seeded

}  // namespace kv::rule_5_13_3::bad_zeros
