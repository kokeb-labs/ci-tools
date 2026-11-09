// Compliant: one declarator per declaration, for members and locals.
#ifndef KV_RULE_10_0_1_OK_HPP
#define KV_RULE_10_0_1_OK_HPP

#include <cstdint>

namespace kv::rule_10_0_1::ok {

struct Point {
  std::uint32_t x;
  std::uint32_t y;
};

inline std::uint32_t both(const Point& p) {
  const std::uint32_t dx = p.x;
  const std::uint32_t dy = p.y;
  return dx | dy;
}

}  // namespace kv::rule_10_0_1::ok

#endif  // KV_RULE_10_0_1_OK_HPP
