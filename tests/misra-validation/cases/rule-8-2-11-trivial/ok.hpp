// Compliant for this guideline: only a trivially copyable integer goes through the ellipsis.
#ifndef KV_RULE_8_2_11_TRIVIAL_OK_HPP
#define KV_RULE_8_2_11_TRIVIAL_OK_HPP

#include <cstdint>

namespace kv::rule_8_2_11_trivial::ok {

std::int32_t first(std::int32_t count, ...);

inline std::int32_t use() {
  const std::int32_t value = 7;
  return first(std::int32_t{1}, value);
}

}  // namespace kv::rule_8_2_11_trivial::ok

#endif  // KV_RULE_8_2_11_TRIVIAL_OK_HPP
