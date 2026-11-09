// Edge cases of the seeded violation.
#include <cstdint>

namespace kv::rule_8_9_1::bad_edge {

struct Pair {
  std::uint8_t left[4]{};
  std::uint8_t right[4]{};
};

bool after(Pair& p) { return &p.right[0] > &p.left[0]; }

bool not_before() {
  std::uint8_t one[2] = {};
  std::uint8_t two[2] = {};
  std::uint8_t* a = &one[0];
  std::uint8_t* b = &two[0];
  return a >= b;
}

}  // namespace kv::rule_8_9_1::bad_edge
