// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_7_0_6::bad_edge {

inline std::int16_t keep(std::int16_t v) { return v; }

std::int16_t pass(std::int32_t wide) { return keep(wide); }  // seeded

std::int16_t give_back(std::int32_t wide) { return wide; }  // seeded

std::int32_t truncate(float f) {
  std::int32_t const i = f;  // seeded
  return i;
}

}  // namespace kv::rule_7_0_6::bad_edge
