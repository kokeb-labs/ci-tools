// Near misses (near): structured jumps: break, continue, early return.
#ifndef KV_RULE_9_6_3_OK_NEAR_HPP
#define KV_RULE_9_6_3_OK_NEAR_HPP

#include <array>
#include <cstdint>

namespace kv::rule_9_6_3::ok_near {

inline std::int32_t first_negative(const std::array<std::int32_t, 4>& values) {
  std::int32_t found = -1;
  for (std::uint32_t i = 0U; i < 4U; ++i) {
    if (values[i] < 0) {
      found = static_cast<std::int32_t>(i);
      break;
    }
  }
  return found;
}

inline std::uint32_t positives(const std::array<std::int32_t, 4>& values) {
  std::uint32_t n = 0U;
  for (const std::int32_t v : values) {
    if (v <= 0) {
      continue;
    }
    n = n + 1U;
  }
  return n;
}

inline bool has_pair(const std::array<std::uint32_t, 4>& values, std::uint32_t key) {
  for (std::uint32_t i = 0U; i < 4U; ++i) {
    for (std::uint32_t j = i; j < 4U; ++j) {
      if ((i != j) && ((values[i] ^ values[j]) == key)) {
        return true;
      }
    }
  }
  return false;
}

}  // namespace kv::rule_9_6_3::ok_near

#endif  // KV_RULE_9_6_3_OK_NEAR_HPP
