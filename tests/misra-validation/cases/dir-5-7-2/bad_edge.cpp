// Edge cases: more forms of the violation.
#include <cstdint>

namespace kv::dir_5_7_2::bad_edge {

std::uint32_t clamp(std::uint32_t v) {
  /* if (v > 7U) { v = 7U; } */
  std::uint32_t out = v & 7U;
  // out = out | 8U;
  return out;
}

}  // namespace kv::dir_5_7_2::bad_edge
