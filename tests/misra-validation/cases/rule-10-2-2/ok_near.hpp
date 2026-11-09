// Near misses (near): the scoped spellings and constexpr constants.
#ifndef KV_RULE_10_2_2_OK_NEAR_HPP
#define KV_RULE_10_2_2_OK_NEAR_HPP

#include <cstdint>

namespace kv::rule_10_2_2::ok_near {

enum struct Speed : std::uint8_t { kSlow, kFast };

inline constexpr std::uint32_t kMaxRetries = 3U;

inline bool fast(Speed s) { return s == Speed::kFast; }

}  // namespace kv::rule_10_2_2::ok_near

#endif  // KV_RULE_10_2_2_OK_NEAR_HPP
