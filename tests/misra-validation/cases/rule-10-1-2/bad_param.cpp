// Seeded violation (param): a volatile by-value parameter.
#include <cstdint>

namespace kv::rule_10_1_2::bad_param {

std::int32_t twice(volatile std::int32_t v) { return v * 2; }

}  // namespace kv::rule_10_1_2::bad_param
