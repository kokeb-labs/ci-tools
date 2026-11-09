// Seeded violation (param): a volatile by-value parameter and a volatile pointer parameter.
#include <cstdint>

namespace kv::rule_10_1_2::bad_param {

std::int32_t twice(volatile std::int32_t v) { return v * 2; }  // seeded

std::int32_t first(const std::int32_t* volatile p) { return *p; }  // seeded

}  // namespace kv::rule_10_1_2::bad_param
