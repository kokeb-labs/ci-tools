// Near misses: compliant code that resembles a violation.
#ifndef KV_RULE_0_2_2_OK_NEAR_HPP
#define KV_RULE_0_2_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_0_2_2::near {

// A member function that does not need one parameter leaves it unnamed.
class Counter {
 public:
  [[nodiscard]] std::uint32_t put(std::uint32_t value, std::uint32_t /*weight*/) const { return value; }
};

// A parameter read only in a lambda body is used.
inline std::uint32_t scaled(std::uint32_t value, std::uint32_t shift) {
  const auto f = [shift](std::uint32_t x) -> std::uint32_t { return x << shift; };
  return f(value);
}

}  // namespace kv::rule_0_2_2::near

#endif  // KV_RULE_0_2_2_OK_NEAR_HPP
