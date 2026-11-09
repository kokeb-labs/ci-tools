// Seeded violation: assignments that narrow and change signedness implicitly.
#include <cstdint>

namespace kv::rule_7_0_6::bad {

std::int16_t narrow(std::int32_t wide) {
  std::int16_t const small = wide;  // seeded
  return small;
}

std::uint32_t unsigned_from(std::int32_t s) {
  std::uint32_t const u = s;  // seeded
  return u;
}

}  // namespace kv::rule_7_0_6::bad
