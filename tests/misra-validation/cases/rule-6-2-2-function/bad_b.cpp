// Seeded violation (with bad_a.cpp): this declaration disagrees with the one in bad_a.cpp.
#include <cstdint>

std::int64_t kv_rule_6_2_2_reading(std::int32_t channel);  // seeded

namespace kv::rule_6_2_2_function::bad {

std::int64_t sample_b() { return kv_rule_6_2_2_reading(2); }

}  // namespace kv::rule_6_2_2_function::bad
