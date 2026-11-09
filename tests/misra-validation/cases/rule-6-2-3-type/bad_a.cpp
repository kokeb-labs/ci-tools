// Seeded violation: a class type defined in two source files.
#include <cstdint>

namespace kv::rule_6_2_3_type::bad {

struct SampleA {
  std::int32_t raw{0};
};

std::int32_t raw_a() { return SampleA{}.raw; }

}  // namespace kv::rule_6_2_3_type::bad

#include "zz_copy_b.inc"
