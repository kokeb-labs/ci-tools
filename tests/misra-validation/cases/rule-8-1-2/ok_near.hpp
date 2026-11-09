// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_1_2_OK_NEAR_HPP
#define KV_RULE_8_1_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_1_2::ok_near {

inline std::uint32_t named(std::uint32_t start, std::uint32_t step) {
  std::uint32_t base = start;
  auto f = [&base, step]() -> std::uint32_t { return (base > step) ? base : step; };
  return f();
}

inline std::uint32_t transient(std::uint32_t start) {
  std::uint32_t base = start;
  return [&]() -> std::uint32_t { return base; }();
}

}  // namespace kv::rule_8_1_2::ok_near

#endif  // KV_RULE_8_1_2_OK_NEAR_HPP
