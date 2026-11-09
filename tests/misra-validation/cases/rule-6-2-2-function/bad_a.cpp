// Seeded violation (with bad_b.cpp): the same external function declared with another return type.
#include <cstdint>

std::int32_t kv_rule_6_2_2_reading(std::int32_t channel);  // seeded

namespace kv::rule_6_2_2_function::bad {

std::int32_t sample_a() { return kv_rule_6_2_2_reading(1); }

}  // namespace kv::rule_6_2_2_function::bad
