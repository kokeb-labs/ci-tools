// Seeded violation: statements left behind in comments.
#include <cstdint>

namespace kv::dir_5_7_2::bad {

std::uint32_t scale(std::uint32_t v) {
  // const std::uint32_t old = v * 3U;
  // return old;
  return v << 1U;
}

}  // namespace kv::dir_5_7_2::bad
