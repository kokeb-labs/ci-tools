// Edge cases: a full function-template specialisation, a variable and a static data member defined in a header.
#ifndef KV_RULE_6_2_4_BAD_EDGE_HPP
#define KV_RULE_6_2_4_BAD_EDGE_HPP

#include <cstdint>

namespace kv::rule_6_2_4::bad_edge {

template <typename T>
T zero() {
  return T{};
}
template <>
std::int32_t zero<std::int32_t>() {
  return 0;
}

std::int32_t counter = 0;

struct Config {
  static std::int32_t level;
};
std::int32_t Config::level = 1;

}  // namespace kv::rule_6_2_4::bad_edge

#endif  // KV_RULE_6_2_4_BAD_EDGE_HPP
