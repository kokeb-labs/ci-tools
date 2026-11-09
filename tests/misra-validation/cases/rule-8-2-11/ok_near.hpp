// Near misses: compliant code close to a violation.
#ifndef KV_RULE_8_2_11_OK_NEAR_HPP
#define KV_RULE_8_2_11_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_8_2_11::ok_near {

template <typename... Args>
std::int32_t count_of(Args const&... /*args*/) {
  return static_cast<std::int32_t>(sizeof...(Args));
}

inline std::int32_t smaller(std::int32_t a) { return a; }

inline std::int32_t smaller(std::int32_t a, std::int32_t b) { return (a < b) ? a : b; }

inline std::int32_t use() { return smaller(count_of(1, 2), smaller(1)); }

}  // namespace kv::rule_8_2_11::ok_near

#endif  // KV_RULE_8_2_11_OK_NEAR_HPP
