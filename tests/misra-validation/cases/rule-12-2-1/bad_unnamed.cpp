// Seeded violation (unnamed): an unnamed padding bit-field next to a named one.
#include <cstdint>

namespace kv::rule_12_2_1::bad_unnamed {

struct Reg {
  std::uint32_t low : 4;
  std::uint32_t : 4;
  std::uint32_t high : 8;
};

std::uint32_t high_of(const Reg& r) { return r.high; }

}  // namespace kv::rule_12_2_1::bad_unnamed
