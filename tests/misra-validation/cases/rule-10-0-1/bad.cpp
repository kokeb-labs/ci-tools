// Seeded violation: two members and two locals declared in one declaration each.
#include <cstdint>

namespace kv::rule_10_0_1::bad {

struct Point {
  std::int32_t x, y;
};

std::int32_t manhattan(const Point& p) {
  std::int32_t dx = p.x, dy = p.y;
  return dx + dy;
}

}  // namespace kv::rule_10_0_1::bad
