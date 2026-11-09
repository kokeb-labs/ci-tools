// Seeded violation: a class type defined in two source files.
#include <cstdint>

namespace kv::rule_6_2_3_type::bad {

struct SampleB {
  std::int32_t raw{0};
};

std::int32_t raw_b() { return SampleB{}.raw; }

}  // namespace kv::rule_6_2_3_type::bad

#include "zz_copy_a.inc"
