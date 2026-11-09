// Seeded violation (with bad_b.cpp): one external object declared with two different types.
#include <cstdint>

extern std::int32_t const kv_rule_6_2_2_threshold;  // seeded

namespace kv::rule_6_2_2_object::bad {

std::int32_t read_a() { return kv_rule_6_2_2_threshold; }

}  // namespace kv::rule_6_2_2_object::bad
