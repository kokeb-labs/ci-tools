// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_7_0_6::bad_edge {

inline std::int16_t keep(std::int16_t v) { return v; }

std::int16_t pass(std::int32_t wide) { return keep(wide); }

std::int16_t give_back(std::int32_t wide) { return wide; }

std::int32_t truncate(float f) {
  std::int32_t const i = f;
  return i;
}

}  // namespace kv::rule_7_0_6::bad_edge
