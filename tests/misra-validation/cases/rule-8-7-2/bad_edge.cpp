// Edge cases of the seeded violation.
#include <cstddef>
#include <cstdint>

namespace kv::rule_8_7_2::bad_edge {

struct Pair {
  std::uint8_t left[4]{};
  std::uint8_t right[4]{};
};

std::ptrdiff_t across(Pair& p) {
  std::uint8_t* a = &p.left[0];
  std::uint8_t* b = &p.right[0];
  return b - a;
}

}  // namespace kv::rule_8_7_2::bad_edge
