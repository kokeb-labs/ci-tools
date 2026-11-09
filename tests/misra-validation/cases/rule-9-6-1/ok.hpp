// Compliant: the search is a plain counted loop; no jump.
#ifndef KV_RULE_9_6_1_OK_HPP
#define KV_RULE_9_6_1_OK_HPP

#include <array>
#include <cstdint>

namespace kv::rule_9_6_1::ok {

inline std::int32_t first_negative(const std::array<std::int32_t, 4>& values) {
  std::int32_t found = -1;
  for (std::uint32_t i = 0U; i < 4U; ++i) {
    if ((found < 0) && (values[i] < 0)) {
      found = static_cast<std::int32_t>(i);
    }
  }
  return found;
}

}  // namespace kv::rule_9_6_1::ok

#endif  // KV_RULE_9_6_1_OK_HPP
